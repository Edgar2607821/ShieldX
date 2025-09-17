from fastapi import HTTPException
from shieldx.repositories import EventTypeRepository
from shieldx.models import EventTypeModel
from shieldx.log.logger_config import get_logger
import time as T
from bson import ObjectId

L = get_logger(__name__)  # Logger específico para este módulo


class EventTypeService:
    """
    Servicio encargado de gestionar la lógica relacionada con los tipos de evento (`EventType`),
    incluyendo su creación, consulta y eliminación.
    """

    def __init__(self, repository: EventTypeRepository):
        """
        Inicializa el servicio con una instancia del repositorio correspondiente.

        :param repository: Instancia de EventTypeRepository para interactuar con la base de datos.
        """
        self.repository = repository

    async def create_event_type(self, data: EventTypeModel) -> str:
        """
        Crea un nuevo tipo de evento en la base de datos y registra la operación.

        :param data: Objeto EventTypeModel con los datos del nuevo tipo de evento.
        :return: ID del tipo de evento creado.
        """
        t1 = T.time()
        try:
            event_type_id = await self.repository.insert_one(data)
            # Log de éxito
            L.info(
                {
                    "event": "EVENT_TYPE.CREATED",
                    "event_type_id": event_type_id,
                    "time": T.time() - t1,
                }
            )
            return event_type_id
        except HTTPException:
            raise
        except Exception as e:
            # Log de error
            L.error({"event": "EVENT_TYPE.CREATE.ERROR", "error": str(e)})
            raise HTTPException(status_code=500, detail="Error creating event type")

    async def list_event_types(self):
        """
        Devuelve todos los tipos de evento registrados en la base de datos y registra la operación.

        :return: Lista de tipos de evento.
        """
        t1 = T.time()
        try:
            event_types = await self.repository.find_all()
            # Log de depuración con cantidad de resultados
            L.debug(
                {
                    "event": "EVENT_TYPE.LIST",
                    "count": len(event_types),
                    "time": T.time() - t1,
                }
            )
            return event_types
        except Exception as e:
            # Log de error
            L.error({"event": "EVENT_TYPE.LIST.ERROR", "error": str(e)})
            return []

    async def get_event_type(self, event_type_id: str):
        """
        Recupera un tipo de evento específico por su ID y registra la operación.

        :param event_type_id: Identificador único del tipo de evento.
        :return: Objeto EventTypeModel si se encuentra, de lo contrario lanza HTTPException 404.
        """
        t1 = T.time()
        try:
            result = await self.repository.find_one({"_id": ObjectId(event_type_id)})
        except HTTPException:
            raise
        except Exception as e:
            L.error(
                {
                    "event": "EVENT_TYPE.GET.ERROR",
                    "event_type_id": event_type_id,
                    "error": str(e),
                }
            )
            raise HTTPException(status_code=500, detail="Error fetching event type")

        if not result:
            # Log de advertencia si no se encuentra
            L.warning(
                {
                    "event": "EVENT_TYPE.NOT_FOUND",
                    "event_type_id": event_type_id,
                    "time": T.time() - t1,
                }
            )
            raise HTTPException(status_code=404, detail="Event type not found")

        # Log de éxito en la consulta
        L.debug(
            {
                "event": "EVENT_TYPE.FETCHED",
                "event_type_id": event_type_id,
                "time": T.time() - t1,
            }
        )
        return result

    async def delete_event_type(self, event_type_id: str):
        """
        Elimina un tipo de evento de la base de datos por su ID y registra la operación.

        :param event_type_id: Identificador único del tipo de evento a eliminar.
        """
        t1 = T.time()
        try:
            result = await self.repository.find_one({"_id": ObjectId(event_type_id)})

            if not result:
                # Log si no se encuentra el tipo de evento
                L.warning(
                    {
                        "event": "EVENT_TYPE.DELETE.NOT_FOUND",
                        "event_type_id": event_type_id,
                        "time": T.time() - t1,
                    }
                )
                raise HTTPException(status_code=404, detail="Event type not found")

            await self.repository.delete_one({"_id": ObjectId(event_type_id)})
            # Log de eliminación exitosa
            L.info(
                {
                    "event": "EVENT_TYPE.DELETED",
                    "event_type_id": event_type_id,
                    "time": T.time() - t1,
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            L.error(
                {
                    "event": "EVENT_TYPE.DELETE.ERROR",
                    "event_type_id": event_type_id,
                    "error": str(e),
                }
            )
            raise HTTPException(status_code=500, detail="Error deleting event type")
