from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from pymongo.errors import PyMongoError
from shieldx.models import TriggerModel
from shieldx.log.logger_config import get_logger
import time as T
from shieldx.repositories import BaseRepository


L = get_logger(__name__)  # Logger específico para este módulo



class TriggersRepository(BaseRepository[TriggerModel]):
    """
    Repositorio encargado de realizar operaciones CRUD sobre la colección de `triggers`
    en MongoDB, incluyendo manejo de errores y conversión de ObjectId.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(collection=db["triggers"], model=TriggerModel)


    
    async def get_trigger_by_name(self, name: str) -> Optional[TriggerModel]:
        """
        Obtiene un trigger específico por su nombre y registra la consulta.

        :param name: Nombre del trigger.
        :return: Objeto `TriggerModel` si existe, de lo contrario `None`.
        """
        t1 = T.time()
        try:
            document = await self.collection.find_one({"name": name})
            if document:
                document["id"] = str(document["_id"])
                # Log de éxito en la consulta
                L.debug({
                    "event": "TRIGGER.FETCH.BY_NAME",
                    "name": name,
                    "time": T.time() - t1
                })
                return TriggerModel(**document)
            else:
                # Log de advertencia si no se encuentra
                L.warning({
                    "event": "TRIGGER.NOT_FOUND",
                    "name": name,
                    "time": T.time() - t1
                })
                return None
        except PyMongoError as e:
            # Log de error
            L.error({"event": "TRIGGER.FETCH.BY_NAME.ERROR", 
                    "name": name, 
                    "error": str(e)})
            return None
