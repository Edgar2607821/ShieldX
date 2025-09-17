from motor.motor_asyncio import AsyncIOMotorDatabase
from shieldx.models import EventTypeModel
from shieldx.log.logger_config import get_logger
import time as T
from shieldx.repositories import BaseRepository

L = get_logger(__name__)


class EventTypeRepository(BaseRepository[EventTypeModel]):
    """
    Repositorio responsable de realizar operaciones CRUD sobre la colección `event_types`
    en la base de datos MongoDB.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(collection=db["event_types"], model=EventTypeModel)

    async def get_by_name(self, name: str):
        """
        Recupera un tipo de evento por su nombre (event_type).

        :param name: Nombre del tipo de evento.
        :return: Instancia de EventTypeModel si existe, None en caso contrario.
        """
        t1 = T.time()
        try:
            doc = await self.collection.find_one({"event_type": name})
            if doc:
                L.debug(
                    {
                        "event": "EVENT_TYPE.FOUND_BY_NAME",
                        "name": name,
                        "time": T.time() - t1,
                    }
                )
                return EventTypeModel(**doc)
            else:
                L.warning(
                    {
                        "event": "EVENT_TYPE.NOT_FOUND_BY_NAME",
                        "name": name,
                        "time": T.time() - t1,
                    }
                )
                return None
        except Exception as e:
            L.error(
                {
                    "event": "EVENT_TYPE.GET_BY_NAME.ERROR",
                    "name": name,
                    "error": str(e),
                    "time": T.time() - t1,
                }
            )
            return None
