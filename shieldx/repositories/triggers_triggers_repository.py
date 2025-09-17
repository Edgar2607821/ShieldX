from motor.motor_asyncio import AsyncIOMotorDatabase
from shieldx.models import TriggersTriggersModel
from shieldx.log.logger_config import get_logger
import time as T
from pymongo.errors import PyMongoError

L = get_logger(__name__)

class TriggersTriggersRepository:
    """
    Repositorio encargado de manejar relaciones jerárquicas entre triggers,
    representando conexiones de activación entre triggers padres e hijos
    mediante la colección `triggers_triggers`.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Inicializa el repositorio y selecciona la colección `triggers_triggers`.

        :param db: Instancia de la base de datos MongoDB.
        """
        self.collection = db["triggers_triggers"]

    async def link(self, parent_id: str, child_id: str):
        """
        Crea una relación de activación entre un trigger padre y un trigger hijo si no existe previamente.
        """
        t1 = T.time()
        try:
            exists = await self.collection.find_one({
                "trigger_parent_id": parent_id,
                "trigger_child_id": child_id
            })
            if exists:
                L.warning({
                    "event": "TRIGGERS_TRIGGERS.LINK.EXISTS",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "time": T.time() - t1
                })
                return None

            await self.collection.insert_one({
                "trigger_parent_id": parent_id,
                "trigger_child_id": child_id
            })
            L.info({
                "event": "TRIGGERS_TRIGGERS.LINKED",
                "parent_id": parent_id,
                "child_id": child_id,
                "time": T.time() - t1
            })
            return {"message": "Linked"}
        except PyMongoError as e:
            L.error({
                "event": "TRIGGERS_TRIGGERS.LINK.ERROR",
                "parent_id": parent_id,
                "child_id": child_id,
                "error": str(e)
            })
            return None

    async def unlink(self, parent_id: str, child_id: str):
        """
        Elimina la relación entre un trigger padre y un trigger hijo.
        """
        t1 = T.time()
        try:
            result = await self.collection.delete_one({
                "trigger_parent_id": parent_id,
                "trigger_child_id": child_id
            })
            if result.deleted_count > 0:
                L.info({
                    "event": "TRIGGERS_TRIGGERS.UNLINKED",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "time": T.time() - t1
                })
            else:
                L.warning({
                    "event": "TRIGGERS_TRIGGERS.UNLINK.NOT_FOUND",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "time": T.time() - t1
                })
        except PyMongoError as e:
            L.error({
                "event": "TRIGGERS_TRIGGERS.UNLINK.ERROR",
                "parent_id": parent_id,
                "child_id": child_id,
                "error": str(e)
            })

    async def get_children(self, parent_id: str):
        """
        Obtiene todos los triggers hijos asociados a un trigger padre.
        """
        t1 = T.time()
        try:
            cursor = self.collection.find({"trigger_parent_id": parent_id})
            children = [TriggersTriggersModel(**doc) async for doc in cursor]
            L.debug({
                "event": "TRIGGERS_TRIGGERS.FETCH.CHILDREN",
                "parent_id": parent_id,
                "count": len(children),
                "time": T.time() - t1
            })
            return children
        except PyMongoError as e:
            L.error({
                "event": "TRIGGERS_TRIGGERS.FETCH.CHILDREN.ERROR",
                "parent_id": parent_id,
                "error": str(e)
            })
            return []

    async def get_parents(self, child_id: str):
        """
        Obtiene todos los triggers padres que activan a un trigger hijo.
        """
        t1 = T.time()
        try:
            cursor = self.collection.find({"trigger_child_id": child_id})
            parents = [TriggersTriggersModel(**doc) async for doc in cursor]
            L.debug({
                "event": "TRIGGERS_TRIGGERS.FETCH.PARENTS",
                "child_id": child_id,
                "count": len(parents),
                "time": T.time() - t1
            })
            return parents
        except PyMongoError as e:
            L.error({
                "event": "TRIGGERS_TRIGGERS.FETCH.PARENTS.ERROR",
                "child_id": child_id,
                "error": str(e)
            })
            return []
