#!/bin/bash
set -e  # Detener ejecución si ocurre algún error

# Variables

IMAGE_NAME=${1:-"edgar821/shieldx-api"}
IMAGE_TAG=${2:-"latest"}
COMPOSE_FILE=${3:-"docker-compose.yml"}

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
echo " 🛠️  Building ShieldX Docker image"
echo "----------------------------------------------"
echo " Imagen: $IMAGE_NAME:$IMAGE_TAG"
echo " Compose file: $COMPOSE_FILE"
echo "=============================================="

# Construcción de la imagen local

docker build -f ./Dockerfile -t $IMAGE_NAME:$IMAGE_TAG .

echo "✅ Image built successfully: $IMAGE_NAME:$IMAGE_TAG"

if [ -f "$COMPOSE_FILE" ]; then
    echo "📦 Starting stack with Docker Compose..."
    docker compose -f "$COMPOSE_FILE" down || true
    docker compose -f "$COMPOSE_FILE" up -d
    echo "✅ Stack deployed successfully."
else
    echo "⚠️  $COMPOSE_FILE not found, only the image was built."
fi

echo "✅ Process completed successfully."
