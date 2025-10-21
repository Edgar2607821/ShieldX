from fastapi import FastAPI
import shieldx.controllers as Controllers
from shieldx.db import connect_to_mongo,close_mongo_connection, get_database
import asyncio
from contextlib import asynccontextmanager
from shieldx.db.indexes import create_indexes
from shieldx.log import Log
from shieldx.log.logger_config import get_logger
from fastapi.middleware.cors import CORSMiddleware
import time as T
from shieldx import config

SHIELDX_TITLE               = config.SHIELDX_TITLE
SHIELDX_API_PREFIX          = config.SHIELDX_API_PREFIX
SHIELDX_HOST                = config.SHIELDX_HOST
SHIELDX_PORT                = config.SHIELDX_PORT
SHIELDX_VERSION             = config.SHIELDX_VERSION
CONTACT_NAME                = config.SHIELDX_CONTACT_NAME
CONTACT_EMAIL               = config.SHIELDX_CONTACT_EMAIL
SHIELDX_MONGODB_MAX_RETRIES = config.SHIELDX_MONGODB_MAX_RETRIES
SHIELDX_RELOAD              = config.SHIELDX_RELOAD

L =  get_logger("shieldx-server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    t1 = T.time()
    L.debug({
        "event":"CONNECTING.DB",
    })
    await connect_to_mongo()
        
    # Esperar hasta que la base de datos esté disponible
    for attempt in range(SHIELDX_MONGODB_MAX_RETRIES):  # Intentos máximos
        try:
            db = get_database()
            if db is not None:
                await create_indexes()
                L.info({
                    "event":"CONNECT.DB",
                    "attempt":attempt,
                    "time":T.time() - t1
                })
                break  # Salir del bucle si la base de datos está lista
            L.error({
                "event":"CONNECTING.MONGODB.FAILED",
                "attempts":attempt+1,
                "left_attempts": SHIELDX_MONGODB_MAX_RETRIES - attempt
            })
            
        except RuntimeError:
            L.debug({
                "event":"CONNECTING.DB.WAITING",
            })
            await asyncio.sleep(1)  # Esperar un segundo antes de intentar nuevamente
    
    yield 
    await close_mongo_connection()
    L.debug({
        "event":"CLOSE.MONGODB.CONNECTION",
        "time":T.time() - t1 
    })


app = FastAPI(
    title=SHIELDX_TITLE,
    version=SHIELDX_VERSION,
    lifespan=lifespan, 
    description="API para registrar y consultar eventos generados por microservicios.",
    contact={
        "name": CONTACT_NAME,
        "email": CONTACT_EMAIL,
    })

# origins = config.SHIELDX_CORS_ORIGINS


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.SHIELDX_CORS_ORIGINS, 
    allow_credentials=config.SHIELDX_CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# Include API routes from the service controller under /api/v1
# Rutas para la gestión de eventos generados por servicios
app.include_router(Controllers.events_router, prefix=SHIELDX_API_PREFIX,tags=["Eventos"],)
# Rutas para la gestión de triggers del sistema
app.include_router(Controllers.trigger_router, prefix=SHIELDX_API_PREFIX, tags=["Triggers"])
# Rutas para la gestión de tipos de eventos
app.include_router(Controllers.event_types_router, prefix=SHIELDX_API_PREFIX, tags=["Tipos de Evento"])
# Rutas para administrar la relación EventType <-> Trigger
app.include_router(Controllers.events_triggers_router, prefix=SHIELDX_API_PREFIX, tags=["Event-Triggers"])
# Rutas para manejar la relación jerárquica entre triggers (parent-child)
app.include_router(Controllers.triggers_triggers_router, prefix=SHIELDX_API_PREFIX, tags=["Triggers-Triggers"])
# Rutas para administrar la relación Trigger <-> Rule
app.include_router(Controllers.rules_trigger_router, prefix=SHIELDX_API_PREFIX, tags=["Trigger - Rule"])
# Rutas para CRUD de reglas
app.include_router(Controllers.rules_router, prefix=SHIELDX_API_PREFIX,  tags=["Rules"])
# Ruta para Choreogrphy
app.include_router(Controllers.choreogrpy_router, prefix=SHIELDX_API_PREFIX, tags=["Choreography"])


# if __name__ == "__main__":
    # uvicorn.run(app, host=SHIELDX_HOST, port=SHIELDX_PORT,reload=SHIELDX_RELOAD)
