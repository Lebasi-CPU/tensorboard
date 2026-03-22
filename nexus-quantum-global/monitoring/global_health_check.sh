#!/bin/bash
# GLOBAL_HEALTH_CHECK.sh
# Verifica el estado de todos los componentes críticos del sistema Nexus Quantum Global

REGION=${1:-"WEST"}
ENTORNO=${2:-"DEV"}

echo "🔍 Iniciando verificación global para $REGION ($ENTORNO)..."

# 1. Verificar API Stealth
echo "📡 Verificando API Stealth..."
if [ -f "./deploy/health_check.sh" ]; then
    ./deploy/health_check.sh
else
    echo "⚠️ health_check.sh no encontrado en ./deploy/"
fi

# 2. Verificar Servidor de Métricas Prometheus
echo "📊 Verificando métricas (Puerto 8000)..."
curl -s -f http://localhost:8000/metrics > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Servidor de métricas activo."
else
    echo "❌ Servidor de métricas no responde."
fi

# 3. Verificar Servicio de Finanzas (Puerto 5000)
echo "💰 Verificando motor de finanzas (Puerto 5000)..."
curl -s -f http://localhost:5000/api/finanzas/estado > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Motor de finanzas activo."
else
    # El servicio de finanzas podría no estar corriendo si solo estamos ejecutando main.py
    echo "ℹ️ Motor de finanzas no detectado en puerto 5000 (podría ser normal según el modo de ejecución)."
fi

echo "✅ Verificación global completada."
