#!/bin/bash
set -e  # Detiene la ejecución si ocurre un error


# Variables de configuración

IMAGE_NAME="edgar821/shieldx-api"
VERSION=${1:-"latest"}

echo "=============================================="
echo " 🐳  Publishing ShieldX Docker image"
echo "----------------------------------------------"
echo " Image: ${IMAGE_NAME}:${VERSION}"
echo "=============================================="


# Login en Docker Hub (usando secrets del workflow)

if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_TOKEN" ]; then
    echo "❌ ERROR: DOCKER_USERNAME or DOCKER_TOKEN are not set."
    exit 1
fi

echo "🔑 Logging in to Docker Hub..."
echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "✅ Login successful."

echo "⬆️  Pushing image to Docker Hub..."
docker push "${IMAGE_NAME}:${VERSION}"
echo "✅ Published: ${IMAGE_NAME}:${VERSION}"

docker logout
echo "🔒 Logged out."
echo "=============================================="
echo " ✅ Publish completed successfully."
echo "=============================================="
