from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from shieldx.repositories import BaseRepository
from shieldx.models import EventModel

from shieldx.log.logger_config import get_logger
import time as T

L = get_logger(__name__)



class EventsRepository(BaseRepository[EventModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(collection=db["events"], model=EventModel)
    
    async def find_events(self, filters: dict, limit: int = 100, skip: int = 0) -> List[EventModel]:
            """
            Obtiene eventos aplicando filtros dinámicos.
            """
            t1 = T.time()
            events = []
            try:
                cursor = self.collection.find(filters).skip(skip).limit(limit)
                async for document in cursor:
                    document["id"] = str(document["_id"])
                    events.append(EventModel(**document))
                L.debug({
                    "event": "EVENT.SEARCH",
                    "filters": filters,
                    "count": len(events),
                    "time": T.time() - t1
                })
            except PyMongoError as e:
                L.error({"event": "EVENT.SEARCH.ERROR", 
                        "error": str(e)})
            return events

    async def find_events_by_service(self, service_id: str) -> List[EventModel]:
        """
        Obtiene eventos filtrados por `service_id`.
        """
        t1 = T.time()
        events = []
        try:
            cursor = self.collection.find({"service_id": service_id})
            async for document in cursor:
                document["id"] = str(document["_id"])
                events.append(EventModel(**document))
            L.debug({
                "event": "EVENTS.FETCH.BY_SERVICE",
                "service_id": service_id,
                "count": len(events),
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "EVENTS.FETCH.BY_SERVICE.ERROR", 
                    "service_id": service_id, 
                    "error": str(e)})
        return events
    
    async def find_events_by_microservice(self, microservice_id: str) -> List[EventModel]:
        """
        Obtiene eventos filtrados por `microservice_id`.
        """
        t1 = T.time()
        events = []
        try:
            cursor = self.collection.find({"microservice_id": microservice_id})
            async for document in cursor:
                document["id"] = str(document["_id"])
                events.append(EventModel(**document))
            L.debug({
                "event": "EVENTS.FETCH.BY_MICROSERVICE",
                "microservice_id": microservice_id,
                "count": len(events),
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "EVENTS.FETCH.BY_MICROSERVICE.ERROR", 
                    "microservice_id": microservice_id,
                    "error": str(e)})
        return events
    
    async def find_events_by_function(self, function_id: str) -> List[EventModel]:
        """
        Obtiene eventos filtrados por `function_id`.
        """
        t1 = T.time()
        events = []
        try:
            cursor = self.collection.find({"function_id": function_id})
            async for document in cursor:
                document["id"] = str(document["_id"])
                events.append(EventModel(**document))
            L.debug({
                "event": "EVENTS.FETCH.BY_FUNCTION",
                "function_id": function_id,
                "count": len(events),
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "EVENTS.FETCH.BY_FUNCTION.ERROR", 
                    "function_id": function_id, 
                    "error": str(e)})
        return events