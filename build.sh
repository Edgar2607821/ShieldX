#!/bin/bash
set -e  # Detener ejecución si ocurre algún error

# Variables

IMAGE_NAME=${1:-"shieldx:api"}
IMAGE_TAG=${2:-"latest"}
DOCKERFILE=${3:-"./Dockerfile"}
BUILD_CONTEXT=${4:-"."}

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
echo " Image      : ${IMAGE_NAME}:${IMAGE_TAG}"
echo " Dockerfile : ${DOCKERFILE}"
echo " Context    : ${BUILD_CONTEXT}"
echo "=============================================="

# Construcción de la imagen local
docker build -f "${DOCKERFILE}" -t "${IMAGE_NAME}:${IMAGE_TAG}" "${BUILD_CONTEXT}"

echo "✅ Image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}"


#
#echo "✅ Image built successfully: $IMAGE_NAME:$IMAGE_TAG"
#
#if [ -f "$COMPOSE_FILE" ]; then
#    echo "📦 Starting stack with Docker Compose..."
#    docker compose -f "$COMPOSE_FILE" down || true
#    docker compose -f "$COMPOSE_FILE" up -d
#    echo "✅ Stack deployed successfully."
#else
#    echo "⚠️  $COMPOSE_FILE not found, only the image was built."
#fi
#
#echo "✅ Process completed successfully."
#