#!/bin/bash
set -e  # Detiene la ejecución si ocurre un error


# Variables de configuración

IMAGE_NAME="edgar821/shieldx-api"
VERSION=${1:-"latest"}

echo "=============================================="
echo " 🐳  Publicando imagen Docker de ShieldX (GitHub Actions)"
echo "----------------------------------------------"
echo " Imagen: $IMAGE_NAME:$VERSION"
echo "=============================================="


# Login en Docker Hub (usando secrets del workflow)

if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_TOKEN" ]; then
    echo "❌ ERROR: Variables DOCKER_USERNAME o DOCKER_TOKEN no están definidas."
    exit 1
fi

echo "🔑 Iniciando sesión en Docker Hub..."
echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "✅ Sesión iniciada correctamente."

echo "⬆️  Subiendo imagen al Docker Hub..."
docker push "$IMAGE_NAME:$VERSION"
echo "✅ Imagen publicada exitosamente como: $IMAGE_NAME:$VERSION"

docker logout
echo "🔒 Sesión de Docker cerrada."
echo "=============================================="
echo " ✅ Publicación completada con éxito."
echo "=============================================="
