# ====== Stage 1: builder ======
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=1.8.3 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependencias del sistema mínimas (compilación si hace falta)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Instala SOLO dependencias (no dev) en una venv dentro de /opt/venv
RUN poetry config virtualenvs.in-project true && \
    poetry lock --no-update && \
    poetry install --no-interaction --no-ansi --without dev

# Copia código fuente
COPY shieldx ./shieldx

# ====== Stage 2: runtime ======
FROM python:3.11-slim AS runtime

# Crea un usuario no root
RUN useradd -m -u 10001 appuser

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=20000 \
    HOST=0.0.0.0

WORKDIR /app

# Crear carpeta de logs y dar permisos
RUN mkdir /log && chown -R appuser:appuser /log



# Copia la venv y el código desde builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/shieldx /app/shieldx

# Puerto expuesto (coincide con el server actual)
EXPOSE 20000

# Healthcheck sencillo a /docs (ajusta si tienes /health)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:20000/docs')" >/dev/null 2>&1 || exit 1

# Bajar privilegios
USER appuser

# Arranque del servidor
# Si tu entrypoint cambia, ajusta este comando
CMD ["uvicorn", "shieldx.server:app", "--host", "0.0.0.0", "--port", "20000", "--workers", "2"]
