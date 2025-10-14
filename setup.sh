#!/bin/bash

# Script de configuración rápida para Savio Infra
# Este script automatiza todo el proceso de instalación

echo "=== Configuración rápida de Savio Infra ==="
echo

# Detectar sistema operativo
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*|MINGW*|MSYS*) MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "🖥️  Sistema operativo detectado: $MACHINE"

# Verificar si estamos en bash
if [ -z "$BASH_VERSION" ]; then
    echo "❌ Este script requiere bash."
    if [ "$MACHINE" = "Windows" ]; then
        echo "   Por favor usa Git Bash en lugar de Command Prompt o PowerShell."
        echo "   Descarga Git desde: https://git-scm.com/download/win"
    fi
    exit 1
fi

echo "✅ Terminal bash detectado correctamente"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instálalo primero."
    echo "Visita: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Docker y Docker Compose están instalados"

# Descargar Moodle si no existe
if [ ! -d "moodle" ]; then
    echo "📥 Descargando Moodle..."
    echo "El script te permitirá seleccionar la versión (4.1 LTS, 4.5, o 5.0+)"
    bash bajar_moodle.sh
else
    echo "✅ Moodle ya está descargado"
fi

# Crear directorio para datos de Moodle si no existe
if [ ! -d "moodledata" ]; then
    echo "📁 Creando directorio moodledata..."
    mkdir -p moodledata
    chmod 777 moodledata
else
    echo "✅ Directorio moodledata ya existe"
fi

echo
echo "🚀 Levantando la infraestructura..."
docker compose up -d

echo
echo "✅ ¡Configuración completa!"
echo
echo "📋 Información importante:"
echo "   - Moodle estará disponible en: http://localhost"
echo "   - Usuario DB: alpyuser"
echo "   - Contraseña DB: alpypass" 
echo "   - Base de datos: alpydb"
echo "   - Host DB: db"
echo
echo "🔧 Para detener los servicios: docker compose down"
echo "📖 Lee el README.md para más información"
