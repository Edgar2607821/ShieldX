#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE=${1:-"docker-compose.yml"}
PROJECT_NAME=${2:-"shieldx"}
COMPOSE_PROFILES=${3:-""}   # opcional, ej: "dev,api"
PULL_MODE=${4:-"auto"}       # auto|always|never

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
echo " Pull mode    : ${PULL_MODE}  (auto|always|never)"
echo "=============================================="

# Reinicio idempotente del stack
docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" down || true

if [[ -n "${COMPOSE_PROFILES}" ]]; then
    COMPOSE_PROFILES="${COMPOSE_PROFILES}" docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d
else
    docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d
fi

echo "✅ Stack deployed successfully."
