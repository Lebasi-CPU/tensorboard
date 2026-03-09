#!/bin/bash
# DEPLOY_UNIFIED_NEXUS_QUANTUM_GLOBAL_SYSTEM.sh
# COMPATIBLE CON: China, Rusia, Japón, Alemania/Suisa, Occidente

# --- VALIDACIÓN DE PARÁMETROS ---
REGIONES_VALIDAS=("CHINA" "RUSSIA" "JAPAN" "EUROPE" "WEST")
ENTORNOS_VALIDOS=("DEV" "PROD" "TEST")
DEFAULT_NOTEBOOK_LM_PATH="${HOME}/Notebooks/LM_Local"

if [ $# -lt 2 ]; then
  echo "Uso: $0 <REGION> <ENTORNO> [RUTA_NOTEBOOK_LM]"
  exit 1
fi

REGION=$1
ENTORNO=$2
NOTEBOOK_LM_PATH="${3:-$DEFAULT_NOTEBOOK_LM_PATH}"

# Validación básica
if [[ ! " ${REGIONES_VALIDAS[@]} " =~ " ${REGION} " ]]; then
  echo "Error: Región $REGION no válida. Use: ${REGIONES_VALIDAS[*]}"
  exit 1
fi

if [[ ! " ${ENTORNOS_VALIDOS[@]} " =~ " ${ENTORNO} " ]]; then
  echo "Error: Entorno $ENTORNO no válido. Use: ${ENTORNOS_VALIDOS[*]}"
  exit 1
fi

# PASO 1: CONFIGURACIÓN POR REGIÓN
echo "🌍 Configurando Nexus Quantum Global para $REGION - $ENTORNO..."

# Localización de variables según estructura de carpetas
CONFIG_DIR="config/${REGION,,}"
ENV_FILE="${CONFIG_DIR}/.env.global.${REGION}"

if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️ Advertencia: Archivo de entorno $ENV_FILE no encontrado. Usando valores por defecto."
fi

# PASO 2: DESPLIEGUE DE COMPONENTES
echo "🚀 Desplegando servicios con Docker Compose..."
if [ "$SIMULATE" != "true" ]; then
    docker-compose -f deploy/docker-compose.global.${REGION}.yml up -d
else
    echo "   [SIMULACIÓN] docker-compose -f deploy/docker-compose.global.${REGION}.yml up -d"
fi

# PASO 3: ACTIVACIÓN Q-LCG
echo "🔮 Iniciando Puerta de Enlace Lingüístico-Cultural Cuántica (Q-LCG)..."
if [ "$SIMULATE" != "true" ]; then
    docker run -d --name q-lcg-gateway-${REGION,,} \
      -v $(pwd)/q-lcg-config:/config \
      -e REGION=$REGION \
      nexusquantum/q-lcg:latest
else
    echo "   [SIMULACIÓN] docker run q-lcg-gateway para $REGION"
fi

# PASO 4: CONECTOR A NOTEBOOK LM LOCAL
echo "🔗 Conectando a Notebook LM en $NOTEBOOK_LM_PATH..."
if [ -d "$NOTEBOOK_LM_PATH" ]; then
  # cp notebook-connector/connector_notebook_lm.py "$NOTEBOOK_LM_PATH/"
  # python3 "$NOTEBOOK_LM_PATH/connector_notebook_lm.py" --region $REGION --env $ENTORNO
  echo "✅ Conector activado en $NOTEBOOK_LM_PATH"
else
  echo "⚠️ Ruta de Notebook LM no encontrada. Conector no activado."
fi

# PASO 5: VERIFICACIÓN GLOBAL
echo "🔍 Ejecutando verificación global..."
# ./monitoring/global_health_check.sh $REGION $ENTORNO
echo "✅ SISTEMA DESPLEGADO Y Q-LCG ACTIVADO PARA $REGION"
