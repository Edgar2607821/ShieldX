from motor.motor_asyncio import AsyncIOMotorDatabase
from shieldx.models import EventsTriggersModel
from shieldx.log.logger_config import get_logger
import time as T
from pymongo.errors import PyMongoError

L = get_logger(__name__)

class EventsTriggersRepository:
    """
    Repositorio encargado de manejar la relación muchos-a-muchos entre tipos de evento (`EventType`)
    y triggers, usando la colección `events_triggers`.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["events_triggers"]

    async def link(self, event_type_id: str, trigger_id: str):
        """
        Crea una relación entre un tipo de evento y un trigger si no existe previamente.
        """
        t1 = T.time()
        try:
            exists = await self.collection.find_one({
                "event_type_id": event_type_id,
                "trigger_id": trigger_id
            })
            if exists:
                L.warning({
                    "event": "EVENT_TRIGGER.LINK.EXISTS",
                    "event_type_id": event_type_id,
                    "trigger_id": trigger_id,
                    "time": T.time() - t1
                })
                return None

            await self.collection.insert_one({
                "event_type_id": event_type_id,
                "trigger_id": trigger_id
            })
            L.info({
                "event": "EVENT_TRIGGER.LINKED",
                "event_type_id": event_type_id,
                "trigger_id": trigger_id,
                "time": T.time() - t1
            })
            return {"message": "Linked"}
        except PyMongoError as e:
            L.error({
                "event": "EVENT_TRIGGER.LINK.ERROR",
                "event_type_id": event_type_id,
                "trigger_id": trigger_id,
                "error": str(e)
            })
            return None

    async def unlink(self, event_type_id: str, trigger_id: str):
        """
        Elimina la relación entre un tipo de evento y un trigger.
        """
        t1 = T.time()
        try:
            result = await self.collection.delete_one({
                "event_type_id": event_type_id,
                "trigger_id": trigger_id
            })
            if result.deleted_count > 0:
                L.info({
                    "event": "EVENT_TRIGGER.UNLINKED",
                    "event_type_id": event_type_id,
                    "trigger_id": trigger_id,
                    "time": T.time() - t1
                })
            else:
                L.warning({
                    "event": "EVENT_TRIGGER.UNLINK.NOT_FOUND",
                    "event_type_id": event_type_id,
                    "trigger_id": trigger_id,
                    "time": T.time() - t1
                })
        except PyMongoError as e:
            L.error({
                "event": "EVENT_TRIGGER.UNLINK.ERROR",
                "event_type_id": event_type_id,
                "trigger_id": trigger_id,
                "error": str(e)
            })

    async def get_triggers_by_event_type(self, event_type_id: str):
        """
        Obtiene todos los triggers vinculados a un tipo de evento específico.
        """
        t1 = T.time()
        try:
            cursor = self.collection.find({"event_type_id": event_type_id})
            triggers = [EventsTriggersModel(**doc) async for doc in cursor]
            L.debug({
                "event": "EVENT_TRIGGER.FETCH.BY_EVENT_TYPE",
                "event_type_id": event_type_id,
                "count": len(triggers),
                "time": T.time() - t1
            })
            return triggers
        except PyMongoError as e:
            L.error({
                "event": "EVENT_TRIGGER.FETCH.BY_EVENT_TYPE.ERROR",
                "event_type_id": event_type_id,
                "error": str(e)
            })
            return []

    async def replace_links(self, event_type_id: str, triggers: list[str]):
        """
        Reemplaza todos los triggers asociados a un tipo de evento por una nueva lista.
        """
        t1 = T.time()
        try:
            await self.collection.delete_many({"event_type_id": event_type_id})
            docs = [{"event_type_id": event_type_id, "trigger_id": t} for t in triggers]
            if docs:
                await self.collection.insert_many(docs)
            L.info({
                "event": "EVENT_TRIGGER.REPLACED",
                "event_type_id": event_type_id,
                "new_links_count": len(triggers),
                "time": T.time() - t1
            })
        except PyMongoError as e:
            L.error({
                "event": "EVENT_TRIGGER.REPLACE.ERROR",
                "event_type_id": event_type_id,
                "error": str(e)
            })
