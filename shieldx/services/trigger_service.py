from fastapi import HTTPException
from shieldx.models import TriggerModel
from shieldx.repositories import TriggersRepository
from shieldx.log.logger_config import get_logger
from bson import ObjectId
import time as T

L = get_logger(__name__)


class TriggerService:
    """
    Servicio encargado de gestionar la lógica relacionada con los triggers,
    incluyendo su creación, consulta, actualización y eliminación.
    """

    def __init__(self, repository: TriggersRepository):
        """Inicializa el repositorio para acceder a los datos de triggers."""
        self.repository = repository

    async def create_trigger(self, trigger: TriggerModel):
        """
        Crea un nuevo trigger si no existe uno con el mismo nombre y registra la operación.
        """
        t1 = T.time()
        try:
            if await self.repository.find_one({"name": trigger.name}):
                L.warning(
                    {
                        "event": "TRIGGER.CREATE.CONFLICT",
                        "name": trigger.name,
                        "time": T.time() - t1,
                    }
                )
                raise HTTPException(status_code=409, detail="Trigger already exists")

            created_trigger = await self.repository.insert_one(trigger)
            created_doc = await self.repository.find_one(
                {"_id": ObjectId(created_trigger)}
            )
            L.info(
                {
                    "event": "TRIGGER.CREATED",
                    "name": trigger.name,
                    "time": T.time() - t1,
                }
            )
            return created_doc
        except HTTPException:
            raise
        except Exception as e:
            L.error(
                {
                    "event": "TRIGGER.CREATE.ERROR",
                    "name": getattr(trigger, "name", None),
                    "error": str(e),
                }
            )
            raise HTTPException(status_code=500, detail="Error creating trigger")

    async def get_all_triggers(self):
        """
        Devuelve la lista de todos los triggers almacenados y registra la operación.
        """
        t1 = T.time()
        try:
            triggers = await self.repository.find_all()
            L.debug(
                {
                    "event": "TRIGGER.LIST.ALL",
                    "count": len(triggers),
                    "time": T.time() - t1,
                }
            )
            return triggers
        except Exception as e:
            L.error({"event": "TRIGGER.LIST.ALL.ERROR", "error": str(e)})
            return []

    async def get_trigger(self, name: str):
        """
        Obtiene un trigger específico por su nombre y registra la operación.
        """
        t1 = T.time()
        try:
            trigger = await self.repository.find_one({"name": name})
            if not trigger:
                L.warning(
                    {"event": "TRIGGER.NOT_FOUND", "name": name, "time": T.time() - t1}
                )
                raise HTTPException(status_code=404, detail="Trigger not found")
            L.debug({"event": "TRIGGER.FETCHED", "name": name, "time": T.time() - t1})
            return trigger
        except HTTPException:
            raise
        except Exception as e:
            L.error({"event": "TRIGGER.GET.ERROR", "name": name, "error": str(e)})
            raise HTTPException(status_code=500, detail="Error fetching trigger")

    async def update_trigger(self, name: str, updated: TriggerModel):
        """
        Actualiza un trigger existente con nuevos datos y registra la operación.
        """
        t1 = T.time()
        try:
            if not await self.repository.find_one({"name": name}):
                L.warning(
                    {
                        "event": "TRIGGER.UPDATE.NOT_FOUND",
                        "name": name,
                        "time": T.time() - t1,
                    }
                )
                raise HTTPException(status_code=404, detail="Trigger not found")

            await self.repository.update_one({"name": name}, updated)
            updated_trigger = await self.repository.find_one({"name": updated.name})

            L.info({"event": "TRIGGER.UPDATED", "name": name, "time": T.time() - t1})
            return updated_trigger
        except HTTPException:
            raise
        except Exception as e:
            L.error({"event": "TRIGGER.UPDATE.ERROR", "name": name, "error": str(e)})
            raise HTTPException(status_code=500, detail="Error updating trigger")

    async def delete_trigger(self, name: str):
        """
        Elimina un trigger por su nombre y registra la operación.
        """
        t1 = T.time()
        try:
            if not await self.repository.find_one({"name": name}):
                L.warning(
                    {
                        "event": "TRIGGER.DELETE.NOT_FOUND",
                        "name": name,
                        "time": T.time() - t1,
                    }
                )
                raise HTTPException(status_code=404, detail="Trigger not found")
            await self.repository.delete_one({"name": name})
            L.info({"event": "TRIGGER.DELETED", "name": name, "time": T.time() - t1})
            return {"detail": f"Trigger '{name}' deleted"}
        except HTTPException:
            raise
        except Exception as e:
            L.error({"event": "TRIGGER.DELETE.ERROR", "name": name, "error": str(e)})
            raise HTTPException(status_code=500, detail="Error deleting trigger")
