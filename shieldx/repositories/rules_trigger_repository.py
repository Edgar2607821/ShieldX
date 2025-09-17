from motor.motor_asyncio import AsyncIOMotorDatabase
from shieldx.models import RulesTriggerModel
from shieldx.log.logger_config import get_logger
import time as T
from pymongo.errors import PyMongoError

L = get_logger(__name__)

class RulesTriggerRepository:
    """
    Repositorio encargado de manejar la relación muchos-a-muchos entre triggers y reglas,
    utilizando la colección intermedia `rules_trigger`.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["rules_trigger"]

    async def link(self, trigger_id: str, rule_id: str):
        """
        Crea una relación entre un trigger y una regla si no existe previamente.
        """
        t1 = T.time()
        try:
            exists = await self.collection.find_one({
                "trigger_id": trigger_id,
                "rule_id": rule_id
            })
            if exists:
                L.warning({
                    "event": "RULE_TRIGGER.LINK.EXISTS",
                    "trigger_id": trigger_id,
                    "rule_id": rule_id,
                    "time": T.time() - t1
                })
                return {"message": "Already linked"}

            await self.collection.insert_one({
                "trigger_id": trigger_id,
                "rule_id": rule_id
            })
            L.info({
                "event": "RULE_TRIGGER.LINKED",
                "trigger_id": trigger_id,
                "rule_id": rule_id,
                "time": T.time() - t1
            })
            return {"message": "Linked"}
        except PyMongoError as e:
            L.error({
                "event": "RULE_TRIGGER.LINK.ERROR",
                "trigger_id": trigger_id,
                "rule_id": rule_id,
                "error": str(e)
            })
            return {"message": "Error"}

    async def unlink(self, trigger_id: str, rule_id: str):
        """
        Elimina la relación entre un trigger y una regla.
        """
        t1 = T.time()
        try:
            result = await self.collection.delete_one({
                "trigger_id": trigger_id,
                "rule_id": rule_id
            })
            if result.deleted_count > 0:
                L.info({
                    "event": "RULE_TRIGGER.UNLINKED",
                    "trigger_id": trigger_id,
                    "rule_id": rule_id,
                    "time": T.time() - t1
                })
            else:
                L.warning({
                    "event": "RULE_TRIGGER.UNLINK.NOT_FOUND",
                    "trigger_id": trigger_id,
                    "rule_id": rule_id,
                    "time": T.time() - t1
                })
        except PyMongoError as e:
            L.error({
                "event": "RULE_TRIGGER.UNLINK.ERROR",
                "trigger_id": trigger_id,
                "rule_id": rule_id,
                "error": str(e)
            })

    async def list_by_trigger(self, trigger_id: str):
        """
        Obtiene todas las reglas asociadas a un trigger específico.
        """
        t1 = T.time()
        try:
            cursor = self.collection.find({"trigger_id": trigger_id})
            rules = [RulesTriggerModel(**doc) async for doc in cursor]
            L.debug({
                "event": "RULE_TRIGGER.FETCH.BY_TRIGGER",
                "trigger_id": trigger_id,
                "count": len(rules),
                "time": T.time() - t1
            })
            return rules
        except PyMongoError as e:
            L.error({
                "event": "RULE_TRIGGER.FETCH.BY_TRIGGER.ERROR",
                "trigger_id": trigger_id,
                "error": str(e)
            })
            return []
