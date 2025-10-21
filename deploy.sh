#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME=${1:-"shieldx"}
readonly ENV_FILE=${2:-".env.dev"}
COMPOSE_PROFILES=${3:-""}   # opcional, ej: "dev,api"

COMPOSE_FILE=${4:-"docker-compose.yml"}
# Banner
echo -e "\e[36m"
cat << "EOF"
███████╗██╗  ██╗██╗███████╗██╗     ██████╗ ██╗  ██╗
██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗╚██╗██╔╝
███████╗███████║██║█████╗  ██║     ██║  ██║ ╚███╔╝
╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║ ██╔██╗
███████║██║  ██║██║███████╗███████╗██████╔╝██╔╝ ██╗
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝ 
EOF
echo -e "\e[0m"

if [[ ! -f "${COMPOSE_FILE}" ]]; then
    echo "⚠️  ${COMPOSE_FILE} no existe. Aborto."
    exit 1
fi

echo "=============================================="
echo " 🚀 Deploying ShieldX stack"
echo "----------------------------------------------"
echo " Compose file : ${COMPOSE_FILE}"
echo " Project name : ${PROJECT_NAME}"
[[ -n "${COMPOSE_PROFILES}" ]] && echo " Profiles     : ${COMPOSE_PROFILES}"
echo "=============================================="

# Reinicio idempotente del stack
docker network create shieldx-net || true
docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" down || true

if [[ -n "${COMPOSE_PROFILES}" ]]; then
    COMPOSE_PROFILES="${COMPOSE_PROFILES}" docker compose --env-file ${ENV_FILE} -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d
else
    docker compose --env-file ${ENV_FILE} -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up --build -d
fi

echo "✅ Stack deployed successfully."
