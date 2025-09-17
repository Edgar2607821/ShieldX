from fastapi import HTTPException
from shieldx.models import EventModel
from shieldx.repositories import EventsRepository
from bson import ObjectId
from typing import List, Optional
from shieldx.log.logger_config import get_logger
import time as T
from shieldx.repositories.event_types_repository import EventTypeRepository

L = get_logger(__name__)


class EventsService:
    """
    Servicio encargado de la lógica de negocio para gestionar eventos,
    incluyendo creación, consulta, actualización y eliminación.
    """

    def __init__(
        self, repository: EventsRepository, event_type_repo: EventTypeRepository
    ):
        """
        Inicializa el servicio con una instancia del repositorio de eventos.

        :param repository: Instancia de EventsRepository.
        :param event_type_repo: Instancia de EventTypeRepository.
        """
        self.repository = repository
        self.event_type_repo = event_type_repo

    async def create_event(self, event: EventModel) -> Optional[dict]:
        """
        Crea un evento en MongoDB validando que el EventType exista.
        """
        t1 = T.time()
        try:
            # Validar existencia del event_type por nombre
            event_type_doc = await self.event_type_repo.get_by_name(event.event_type)

            if not event_type_doc:
                L.error(
                    {
                        "event": "EVENT.CREATE.FAILED.EVENT_TYPE.NOT_FOUND",
                        "event_type": event.event_type,
                        "time": T.time() - t1,
                    }
                )
                raise HTTPException(
                    status_code=404, detail=f"Event type '{event.event_type}' not found"
                )

            # Crear el evento
            # created_event = await self.repository.create_event(event)
            created_event = await self.repository.insert_one(event)
            if created_event:
                L.info(
                    {
                        "event": "EVENT.CREATED",
                        "event_id": created_event,
                        "time": T.time() - t1,
                    }
                )
                return created_event

            L.error({"event": "EVENT.CREATE.FAILED", "time": T.time() - t1})
            return None
        except HTTPException:
            raise
        except Exception as e:
            L.error({"event": "EVENT.CREATE.ERROR", "error": str(e)})
            raise HTTPException(status_code=500, detail="Error creating event")

    async def get_all_events(self) -> list[EventModel]:
        """
        Obtiene todos los eventos almacenados en la base de datos.
        """
        t1 = T.time()
        try:
            # events = await self.repository.find_all_events()
            events = await self.repository.find_all()

            L.debug(
                {"event": "EVENT.LIST.ALL", "count": len(events), "time": T.time() - t1}
            )
            return events
        except Exception as e:
            L.error({"event": "EVENT.LIST.ALL.ERROR", "error": str(e)})
            return []

    async def get_events_filtered(
        self,
        service_id: Optional[str] = None,
        microservice_id: Optional[str] = None,
        function_id: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[EventModel]:
        """
        Obtiene eventos aplicando filtros dinámicos.

        :param service_id: Filtro por ID del servicio.
        :param microservice_id: Filtro por ID del microservicio.
        :param function_id: Filtro por ID de la función.
        :param limit: Límite de resultados.
        :param skip: Saltar resultados para paginación.
        :return: Lista de objetos EventModel filtrados.
        """
        t1 = T.time()
        filters = {}
        if service_id:
            filters["service_id"] = service_id
        if microservice_id:
            filters["microservice_id"] = microservice_id
        if function_id:
            filters["function_id"] = function_id

        try:
            events = await self.repository.find_events(filters, limit, skip)
            L.debug(
                {
                    "event": "EVENT.LIST.FILTERED",
                    "filters": filters,
                    "count": len(events),
                    "time": T.time() - t1,
                }
            )
            return events
        except Exception as e:
            L.error(
                {
                    "event": "EVENT.LIST.FILTERED.ERROR",
                    "filters": filters,
                    "error": str(e),
                }
            )
            return []

    async def get_event_by_id(self, event_id: str) -> Optional[EventModel]:
        """
        Obtiene un evento específico por `event_id`.
        """
        t1 = T.time()
        # event = await self.repository.find_event_by_id(event_id)
        try:
            event = await self.repository.find_one({"_id": ObjectId(event_id)})
            if event:
                L.debug(
                    {
                        "event": "EVENT.FETCH.BY_ID",
                        "event_id": str(event.event_id),
                        "time": T.time() - t1,
                    }
                )
            else:
                L.warning(
                    {
                        "event": "EVENT.NOT_FOUND",
                        "event_id": str(event.event_id),
                        "time": T.time() - t1,
                    }
                )
            return event
        except HTTPException:
            raise
        except Exception as e:
            L.error(
                {
                    "event": "EVENT.FETCH.BY_ID.ERROR",
                    "event_id": event_id,
                    "error": str(e),
                }
            )
            raise HTTPException(status_code=500, detail="Error fetching event")

    async def update_event(self, event_id: str, update_data: dict) -> Optional[EventModel]:
        """
        Actualiza un evento en la base de datos.

        :param event_id: ID del evento a actualizar.
        :param update_data: Campos a modificar.
        :return: Evento actualizado o None.
        """
        t1 = T.time()
        # updated_event = await self.repository.update_event(event_id, update_data)
        try:
            updated_event = await self.repository.update_one(
                {"_id": ObjectId(event_id)}, update_data
            )
            if updated_event:
                L.info(
                    {
                        "event": "EVENT.UPDATED",
                        "event_id": event_id,
                        "time": T.time() - t1,
                    }
                )
            else:
                L.warning(
                    {
                        "event": "EVENT.UPDATE.FAILED",
                        "event_id": event_id,
                        "time": T.time() - t1,
                    }
                )
            return updated_event
        except HTTPException:
            raise
        except Exception as e:
            L.error(
                {"event": "EVENT.UPDATE.ERROR", "event_id": event_id, "error": str(e)}
            )
            raise HTTPException(status_code=500, detail="Error updating event")

    async def delete_event(self, event_id: str) -> bool:
        """
        Elimina un evento de la base de datos.

        :param event_id: ID del evento a eliminar.
        :return: True si se eliminó, False si no se encontró.
        """
        t1 = T.time()
        # result = await self.repository.delete_event(event_id)
        try:
            result = await self.repository.delete_one({"_id": ObjectId(event_id)})
            if result:
                L.info(
                    {
                        "event": "EVENT.DELETED",
                        "event_id": event_id,
                        "time": T.time() - t1,
                    }
                )
            else:
                L.warning(
                    {
                        "event": "EVENT.DELETE.NOT_FOUND",
                        "event_id": event_id,
                        "time": T.time() - t1,
                    }
                )
            return bool(result)
        except HTTPException:
            raise
        except Exception as e:
            L.error(
                {"event": "EVENT.DELETE.ERROR", "event_id": event_id, "error": str(e)}
            )
            raise HTTPException(status_code=500, detail="Error deleting event")
