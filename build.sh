#!/bin/bash
set -e  # Detener ejecución si ocurre algún error

# Variables

IMAGE_NAME="edgar821/shieldx-api"
VERSION=${1:-"latest"}
COMPOSE_FILE="docker-compose.yml"

# Banner de inicio para ShieldX
echo -e "\e[36m"  # Color cian
cat << "EOF"
███████╗██╗  ██╗██╗███████╗██╗     ██████╗ ██╗  ██╗
██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗╚██╗██╔╝
███████╗███████║██║█████╗  ██║     ██║  ██║ ╚███╔╝
╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║ ██╔██╗
███████║██║  ██║██║███████╗███████╗██████╔╝██╔╝ ██╗
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝
EOF
echo -e "\e[0m"  # Restaurar color por defecto
echo

echo "=============================================="
echo " 🛠️  Construyendo imagen Docker de ShieldX"
echo "----------------------------------------------"
echo " Imagen: $IMAGE_NAME:$VERSION"
echo " Compose file: $COMPOSE_FILE"
echo "=============================================="

# Construcción de la imagen local

docker build -f ./Dockerfile -t $IMAGE_NAME:$VERSION .

echo "✅ Imagen construida correctamente: $IMAGE_NAME:$VERSION"

if [ -f "$COMPOSE_FILE" ]; then
    echo "📦 Levantando stack con docker-compose..."
    docker compose -f "$COMPOSE_FILE" down || true
    docker compose -f "$COMPOSE_FILE" up -d
    echo "✅ Stack desplegado correctamente."
else
    echo "⚠️  No se encontró $COMPOSE_FILE, solo se construyó la imagen."
fi

echo "✅ Proceso finalizado."
