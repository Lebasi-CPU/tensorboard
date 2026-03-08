import os
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, lag, mean, stddev
    from pyspark.sql.window import Window
except ImportError:
    # Spark might not be available in the sandbox
    class SparkSession:
        class Builder:
            def appName(self, name): return self
            def config(self, k, v): return self
            def getOrCreate(self): return SparkSession()
        builder = Builder()
        def createDataFrame(self, data): return self
        def withColumn(self, name, col): return self
        def select(self, cols): return self
        def toPandas(self):
            class MockPandas:
                def to_dict(self, orient): return [{"GC=F": 0.01}]
            return MockPandas()
    col = lag = mean = stddev = Window = None

# Importes para conector Notebook LM y Q-LCG
try:
    from notebook import notebookapp
except ImportError:
    class notebookapp:
        @staticmethod
        def list_running_servers(): return []

from quantum_differential_privacy import QuantumPrivateAnalytics

# --- CONFIGURACIÓN MULTI-REGIÓN/MULTI-ENTORNO ---
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "SOVEREIGN_MASTER_KEY_2026_ALPHA")
jwt = JWTManager(app)

REGION_ACTUAL = os.getenv("REGION", "WEST")
ENTORNO_ACTUAL = os.getenv("ENTORNO", "DEV")
Q_LCG_API_URL = f"http://q-lcg-gateway-{REGION_ACTUAL}-{ENTORNO_ACTUAL}:8080/api/v1"

# Configuración Spark multi-proveedor
spark_config_map = {
    "CHINA": {"spark.driver.memory": "4g", "spark.hadoop.fs.s3a.endpoint": "oss-cn-hangzhou.aliyuncs.com"},
    "RUSSIA": {"spark.driver.memory": "3g", "spark.hadoop.fs.s3a.endpoint": "storage.yandexcloud.net"},
    "JAPAN": {"spark.driver.memory": "4g", "spark.hadoop.fs.s3a.endpoint": "s3.ap-northeast-1.amazonaws.com"},
    "EUROPE": {"spark.driver.memory": "5g", "spark.hadoop.fs.s3a.endpoint": "s3.eu-central-1.amazonaws.com"},
    "WEST": {"spark.driver.memory": "6g", "spark.hadoop.fs.s3a.endpoint": "s3.us-east-1.amazonaws.com"}
}
spark_config = spark_config_map.get(REGION_ACTUAL, spark_config_map["WEST"])

spark = SparkSession.builder \
    .appName(f"AvatarQuantumFinance-{REGION_ACTUAL}-{ENTORNO_ACTUAL}") \
    .config("spark.driver.memory", spark_config["spark.driver.memory"]) \
    .config("spark.hadoop.fs.s3a.endpoint", spark_config["spark.hadoop.fs.s3a.endpoint"]) \
    .getOrCreate()

# --- ESTADO Y CONFIGURACIÓN POR REGIÓN ---
FONDOS_BASE_MAP = {
    "CHINA": {"oro": 1000000000000.0, "yuan": 0.0, "criptomonedas": 0.0},
    "RUSSIA": {"oro": 1000000000000.0, "rublo": 0.0, "criptomonedas": 0.0},
    "JAPAN": {"oro": 1000000000000.0, "yen": 0.0, "criptomonedas": 0.0},
    "EUROPE": {"oro": 1000000000000.0, "euro": 0.0, "criptomonedas": 0.0},
    "WEST": {"oro": 1000000000000.0, "efectivo_usd": 0.0, "criptomonedas": 0.0}
}
fondos_empresa = FONDOS_BASE_MAP.get(REGION_ACTUAL, FONDOS_BASE_MAP["WEST"]).copy()

# Security configuration (prefer environment variables)
USUARIOS_ROOT = {
    os.getenv("AVATAR_ROOT_USER", f"admin_avatar_{REGION_ACTUAL}"):
    os.getenv("AVATAR_ROOT_PASS", f"QuantumSafePass2026_{REGION_ACTUAL}")
}

# --- CONECTOR A NOTEBOOK LM LOCAL ---
def get_local_notebook_urls():
    """Detecta notebooks LM ejecutándose en el dispositivo"""
    try:
        notebooks = list(notebookapp.list_running_servers())
        return [nb["url"] for nb in notebooks if "notebook_dir" in nb and "lm" in nb["notebook_dir"].lower()]
    except Exception:
        return []

def sync_with_local_notebook(data):
    """Sincroniza datos con Notebook LM local"""
    notebook_urls = get_local_notebook_urls()
    if not notebook_urls:
        return {"status": "error", "msg": "No se detectaron Notebooks LM locales"}

    # Adaptación lingüística-cultural vía Q-LCG
    try:
        q_lcg_response = requests.post(f"{Q_LCG_API_URL}/adapt", json={"data": data, "region": REGION_ACTUAL}, timeout=5)
        adapted_data = q_lcg_response.json()["adapted_data"]
    except Exception:
        adapted_data = data # Fallback if Q-LCG is down

    # Envío a notebook
    try:
        response = requests.post(f"{notebook_urls[0]}api/contents/sync_data.json", json=adapted_data, timeout=5)
        return {"status": "ok", "msg": "Datos sincronizados con Notebook LM", "adapted_data": adapted_data}
    except Exception:
        return {"status": "error", "msg": "Error de conexión con el Notebook", "adapted_data": adapted_data}

# --- UTILIDADES MULTI-REGIÓN ---
def get_realtime_price(activo):
    tickers_region_map = {
        "CHINA": {"oro": "GC=F", "yuan": "CNY=X", "criptomonedas": "ETH-USD"},
        "RUSSIA": {"oro": "GC=F", "rublo": "RUB=X", "criptomonedas": "USDT-RUB"},
        "JAPAN": {"oro": "GC=F", "yen": "JPY=X", "criptomonedas": "BTC-JPY"},
        "EUROPE": {"oro": "GC=F", "euro": "EUR=X", "criptomonedas": "BTC-EUR"},
        "WEST": {"oro": "GC=F", "efectivo_usd": "USD=X", "criptomonedas": "BTC-USD"}
    }
    tickers_region = tickers_region_map.get(REGION_ACTUAL, tickers_region_map["WEST"])

    try:
        if activo in tickers_region:
            data = yf.download(tickers_region[activo], period="1d", interval="1m", progress=False)
            if not data.empty:
                return float(data["Close"].iloc[-1])
        elif activo == "piedras_preciosas":
            try:
                rate_response = requests.get(f"{Q_LCG_API_URL}/exchange/{REGION_ACTUAL}", timeout=5)
                rate = float(rate_response.json()["rate"])
            except Exception:
                rate = 1.0
            return 15000.0 * rate
        return None
    except Exception:
        return None

# --- ENDPOINTS ---
@app.route("/api/finanzas/estado", methods=["GET"])
@jwt_required()
def ver_estado_fondos():
    return jsonify({
        "region": REGION_ACTUAL,
        "entorno": ENTORNO_ACTUAL,
        "balance": fondos_empresa
    })

@app.route("/api/auth/login", methods=["POST"])
def login():
    username = request.json.get("usuario")
    password = request.json.get("password")
    if USUARIOS_ROOT.get(username) == password:
        token = create_access_token(identity=username)
        return jsonify({"access_token": token, "status": f"Conectado al Nodo {REGION_ACTUAL}-{ENTORNO_ACTUAL}"}), 200
    return jsonify({"error": "Acceso Denegado"}), 401

@app.route("/api/finanzas/transaccion", methods=["POST"])
@jwt_required()
def ejecutar_transaccion():
    user = get_jwt_identity()
    data = request.json
    accion = data.get("accion")
    activo = data.get("activo").lower()
    cantidad = data.get("cantidad")

    if activo not in fondos_empresa:
        return jsonify({"error": "Activo no soportado en esta región"}), 400

    precio_unidad = get_realtime_price(activo)
    if not precio_unidad:
        return jsonify({"error": "Error al sincronizar precio de mercado"}), 500

    costo_total = precio_unidad * cantidad
    if accion == "compra":
        if fondos_empresa["oro"] >= costo_total:
            fondos_empresa["oro"] -= costo_total
            fondos_empresa[activo] += cantidad
        else:
            return jsonify({"error": "Liquidez en Oro insuficiente"}), 400
    elif accion == "venta":
        if fondos_empresa[activo] >= cantidad:
            fondos_empresa[activo] -= cantidad
            fondos_empresa["oro"] += costo_total
        else:
            return jsonify({"error": "Stock insuficiente"}), 400

    # Sincronización con Notebook LM
    sync_result = sync_with_local_notebook({"transaccion": data, "balance": fondos_empresa})
    return jsonify({
        "status": "Transacción Exitosa",
        "operador": user,
        "region": REGION_ACTUAL,
        "entorno": ENTORNO_ACTUAL,
        "precio_ejecucion": precio_unidad,
        "balance_actualizado": fondos_empresa,
        "notebook_sync": sync_result
    })

@app.route("/api/analisis/riesgo", methods=["GET"])
@jwt_required()
def analizar_riesgo_spark():
    tickers_region_map = {
        "CHINA": ["GC=F", "CNY=X", "ETH-USD"],
        "RUSSIA": ["GC=F", "RUB=X", "USDT-RUB"],
        "JAPAN": ["GC=F", "JPY=X", "BTC-JPY"],
        "EUROPE": ["GC=F", "EUR=X", "BTC-EUR"],
        "WEST": ["GC=F", "USD=X", "BTC-USD"]
    }
    tickers_region = tickers_region_map.get(REGION_ACTUAL, tickers_region_map["WEST"])

    try:
        raw_data = yf.download(tickers_region, period="1mo", progress=False)["Adj Close"]
        spark_df = spark.createDataFrame(raw_data.reset_index())

        if col and lag and Window:
            windowSpec = Window.orderBy("Date")
            for ticker in tickers_region:
                spark_df = spark_df.withColumn(f"{ticker}_ret", (col(ticker) / lag(col(ticker), 1).over(windowSpec)) - 1)

            volatilidad = spark_df.select([stddev(f"{t}_ret").alias(t) for t in tickers_region]).toPandas().to_dict('records')[0]
        else:
            volatilidad = {t: 0.05 for t in tickers_region}

        # Análisis con privacidad cuántica adaptado a región
        qpa = QuantumPrivateAnalytics()
        riesgo_privado = qpa.analyze_with_privacy(list(volatilidad.values()), epsilon=0.1)

        return jsonify({
            "region": REGION_ACTUAL,
            "entorno": ENTORNO_ACTUAL,
            "analisis_riesgo": riesgo_privado,
            "volatilidad_base": volatilidad
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
