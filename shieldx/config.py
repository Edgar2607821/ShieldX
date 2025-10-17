import os

# ========================
# Configuración General
# ========================
SHIELDX_TITLE = os.environ.get("SHIELDX_TITLE", "ShieldX API")
SHIELDX_API_PREFIX = os.environ.get("SHIELDX_API_PREFIX", "/api/v1")
SHIELDX_HOST = os.environ.get("SHIELDX_HOST", "0.0.0.0")
SHIELDX_PORT = int(os.environ.get("SHIELDX_PORT", "20000"))
SHIELDX_MONGODB_MAX_RETRIES = int(os.environ.get("SHIELDX_MONGODB_MAX_RETRIES", "5"))
SHIELDX_RELOAD = bool(int(os.environ.get("SHIELDX_RELOAD", "1")))
SHIELDX_VERSION = os.environ.get("SHIELDX_VERSION", "0.1.0")

# ========================
# Configuración de ShieldX Client
# ========================
SHIELDX_CLIENT_BASE_URL = os.environ.get(
"SHIELDX_CLIENT_BASE_URL",
f"http://{SHIELDX_HOST}:{SHIELDX_PORT}{SHIELDX_API_PREFIX}"
)

# ========================
# Conexión a Base de Datos
# ========================
SHIELDX_MONGODB_URI = os.environ.get("SHIELDX_MONGODB_URI", "mongodb://localhost:27017/shieldx")
SHIELDX_MONGO_DATABASE_NAME = os.environ.get("SHIELDX_MONGO_DATABASE_NAME", "shieldx")

# ========================
# Configuración de Logs
# ========================
SHIELDX_LOG_PATH = os.environ.get("SHIELDX_LOG_PATH", "/log")
SHIELDX_LOG_LEVEL = os.environ.get("SHIELDX_LOG_LEVEL", "DEBUG")
SHIELDX_LOG_ROTATION_WHEN = os.environ.get("SHIELDX_LOG_ROTATION_WHEN", "m")
SHIELDX_LOG_ROTATION_INTERVAL = int(os.environ.get("SHIELDX_LOG_ROTATION_INTERVAL", "10"))
SHIELDX_LOG_TO_FILE = bool(int(os.environ.get("SHIELDX_LOG_TO_FILE", "1")))
SHIELDX_LOG_ERROR_FILE = bool(int(os.environ.get("SHIELDX_LOG_ERROR_FILE", "1")))

# ========================
# Modo y entorno
# ========================
SHIELDX_DEBUG = bool(int(os.environ.get("SHIELDX_DEBUG", "1")))
SHIELDX_ENV = os.environ.get("SHIELDX_ENV", "dev")
SHIELDX_TEST = bool(int(os.environ.get("SHIELDX_TEST", "1")))

# ========================
# Contacto de la API
# ========================
SHIELDX_CONTACT_NAME = os.environ.get("SHIELDX_CONTACT_NAME", "Equipo ShieldX")
SHIELDX_CONTACT_EMAIL = os.environ.get("SHIELDX_CONTACT_EMAIL", "soporte@shieldx.io")
