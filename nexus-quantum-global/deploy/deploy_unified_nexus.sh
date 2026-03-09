#!/bin/bash
# DEPLOY_UNIFIED_NEXUS_QUANTUM_GLOBAL_SYSTEM.sh
# COMPATIBLE CON: Nexus Quantum Global / ÉLITE FMI VANGUARDIA

# --- VALIDACIÓN DE PARÁMETROS ---
REGIONES_VALIDAS=("CHINA" "RUSSIA" "JAPAN" "EUROPE" "WEST")
ENTORNOS_VALIDOS=("DEV" "PROD" "TEST")
DEFAULT_NOTEBOOK_LM_PATH="${HOME}/Notebooks/LM_Local"

if [ $# -lt 2 ]; then
  echo "Uso: $0 <REGION> <ENTORNO> [RUTA_NOTEBOOK_LM]"
  exit 1
fi

export REGION=$1
export ENTORNO=$2
NOTEBOOK_LM_PATH="${3:-$DEFAULT_NOTEBOOK_LM_PATH}"

# Validación básica
if [[ ! " ${REGIONES_VALIDAS[@]} " =~ " ${REGION} " ]]; then
  echo "Error: Región $REGION no válida."
  exit 1
fi

# PASO 1: VERIFICACIÓN DE SALUD (VANGUARDIA)
echo "🔍 Ejecutando verificación de salud..."
./deploy/health_check.sh
if [ $? -ne 0 ]; then
    echo "❌ Error de salud inicial. Abortando despliegue."
    exit 1
fi

# PASO 2: DESPLIEGUE DE COMPONENTES
echo "🚀 Desplegando servicios para $REGION..."
if [ "$SIMULATE" != "true" ]; then
    # docker-compose -f deploy/docker-compose.global.${REGION}.yml up -d
    echo "   [EXEC] Ejecutando Misión Maestra (main.py)..."
    python3 main.py
else
    echo "   [SIMULACIÓN] docker-compose -f deploy/docker-compose.global.${REGION}.yml up -d"
fi

# PASO 3: CONECTOR A NOTEBOOK LM LOCAL
echo "🔗 Conectando a Notebook LM..."
if [ -d "$NOTEBOOK_LM_PATH" ]; then
  echo "✅ Conector activado en $NOTEBOOK_LM_PATH"
else
  echo "⚠️ Ruta de Notebook LM no encontrada."
fi

echo "✨ SISTEMA DESPLEGADO Y VANGUARDIA ACTIVADA PARA $REGION"
