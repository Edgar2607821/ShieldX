from shieldx.repositories import EventsTriggersRepository
from shieldx.log.logger_config import get_logger
from fastapi import HTTPException
import time as T

L = get_logger(__name__)

class EventsTriggersService:
    """
    Servicio encargado de gestionar la relación entre tipos de evento (`EventType`) y triggers,
    utilizando una tabla intermedia (`events_triggers`) para manejar asociaciones M:N.
    """

    def __init__(self, repository: EventsTriggersRepository):
        """
        Inicializa el servicio con una instancia del repositorio correspondiente.

        :param repository: Instancia de EventsTriggersRepository para interactuar con la base de datos.
        """
        self.repository = repository

    async def link_trigger(self, event_type_id: str, trigger_id: str):
        """
        Vincula un trigger a un tipo de evento y registra la operación.

        :param event_type_id: ID del tipo de evento.
        :param trigger_id: ID del trigger que se desea asociar.
        :return: Resultado de la operación de enlace.
        """
        t1 = T.time()
        try:
            result = await self.repository.link(event_type_id, trigger_id)
            if result:
                # Log si se creó la relación
                L.info({
                    "event": "EVENT_TRIGGER.LINKED",
                    "event_type_id": event_type_id,
                    "trigger_id": trigger_id,
                    "time": T.time() - t1
                })
            else:
                # Log si la relación ya existía
                L.warning({
                    "event": "EVENT_TRIGGER.LINK.EXISTS",
                    "event_type_id": event_type_id,
                    "trigger_id": trigger_id,
                    "time": T.time() - t1
                })
            return result
        except Exception as e:
            L.error({"event": "EVENT_TRIGGER.LINK.ERROR", 
                    "event_type_id": event_type_id, 
                    "trigger_id": trigger_id, 
                    "error": str(e)})
            raise HTTPException(status_code=500, detail="Error linking trigger")

    async def unlink_trigger(self, event_type_id: str, trigger_id: str):
        """
        Desvincula un trigger previamente asociado a un tipo de evento y registra la operación.

        :param event_type_id: ID del tipo de evento.
        :param trigger_id: ID del trigger que se desea desvincular.
        """
        t1 = T.time()
        try:
            await self.repository.unlink(event_type_id, trigger_id)
            # Log de desvinculación
            L.info({
                "event": "EVENT_TRIGGER.UNLINKED",
                "event_type_id": event_type_id,
                "trigger_id": trigger_id,
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "EVENT_TRIGGER.UNLINK.ERROR", 
                    "event_type_id": event_type_id, 
                    "trigger_id": trigger_id, 
                    "error": str(e)})
            raise HTTPException(status_code=500, detail="Error unlinking trigger")

    async def list_triggers_for_event_type(self, event_type_id: str):
        """
        Lista todos los triggers vinculados a un tipo de evento específico y registra la operación.

        :param event_type_id: ID del tipo de evento.
        :return: Lista de asociaciones EventTriggerModel.
        """
        t1 = T.time()
        try:
            triggers = await self.repository.get_triggers_by_event_type(event_type_id)
            # Log de consulta
            L.debug({
                "event": "EVENT_TRIGGER.LIST.FOR_EVENT_TYPE",
                "event_type_id": event_type_id,
                "count": len(triggers),
                "time": T.time() - t1
            })
            return triggers
        except Exception as e:
            L.error({"event": "EVENT_TRIGGER.LIST.ERROR", 
                    "event_type_id": event_type_id, 
                    "error": str(e)})
            return []

    async def replace_triggers_for_event_type(self, event_type_id: str, trigger_ids: list[str]):
        """
        Reemplaza todos los triggers asociados a un tipo de evento por una nueva lista y registra la operación.

        :param event_type_id: ID del tipo de evento.
        :param trigger_ids: Lista de IDs de triggers que deben quedar asociados.
        """
        t1 = T.time()
        try:
            await self.repository.replace_links(event_type_id, trigger_ids)
            # Log de reemplazo de relaciones
            L.info({
                "event": "EVENT_TRIGGER.REPLACED",
                "event_type_id": event_type_id,
                "new_links_count": len(trigger_ids),
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "EVENT_TRIGGER.REPLACE.ERROR", 
                    "event_type_id": event_type_id, 
                    "error": str(e)})
            raise HTTPException(status_code=500, detail="Error replacing event triggers")
