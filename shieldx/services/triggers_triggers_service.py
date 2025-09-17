from fastapi import HTTPException
from shieldx.repositories import TriggersTriggersRepository
from shieldx.log.logger_config import get_logger
import time as T

L = get_logger(__name__)


class TriggersTriggersService:
    """
    Servicio encargado de gestionar la relación jerárquica entre triggers,
    permitiendo la vinculación de triggers padres e hijos mediante la colección `triggers_triggers`.
    """

    def __init__(self, repository: TriggersTriggersRepository):
        """
        Inicializa el servicio con una instancia del repositorio correspondiente.

        :param repository: Instancia de TriggersTriggersRepository para interactuar con la base de datos.
        """
        self.repository = repository

    async def link_triggers(self, parent_id: str, child_id: str):
        """
        Crea una relación de dependencia entre un trigger padre y un trigger hijo
        y registra la operación.

        :param parent_id: ID del trigger que actuará como padre.
        :param child_id: ID del trigger que actuará como hijo.
        :return: Resultado de la operación de enlace.
        """
        t1 = T.time()
        try:
            result = await self.repository.link(parent_id, child_id)
            if result:
                # Log de vínculo exitoso
                L.info(
                    {
                        "event": "TRIGGERS_TRIGGERS.LINKED",
                        "parent_id": parent_id,
                        "child_id": child_id,
                        "time": T.time() - t1,
                    }
                )
            else:
                # Log si ya existía la relación
                L.warning(
                    {
                        "event": "TRIGGERS_TRIGGERS.LINK.EXISTS",
                        "parent_id": parent_id,
                        "child_id": child_id,
                        "time": T.time() - t1,
                    }
                )
            return result
        except Exception as e:
            L.error(
                {
                    "event": "TRIGGERS_TRIGGERS.LINK.ERROR",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "error": str(e),
                }
            )
            raise HTTPException(status_code=500, detail="Error linking triggers")

    async def unlink_triggers(self, parent_id: str, child_id: str):
        """
        Elimina la relación entre un trigger padre y su trigger hijo y registra la operación.

        :param parent_id: ID del trigger padre.
        :param child_id: ID del trigger hijo.
        """
        t1 = T.time()
        try:
            await self.repository.unlink(parent_id, child_id)
            # Log de desvinculación
            L.info(
                {
                    "event": "TRIGGERS_TRIGGERS.UNLINKED",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "time": T.time() - t1,
                }
            )
        except Exception as e:
            L.error(
                {
                    "event": "TRIGGERS_TRIGGERS.UNLINK.ERROR",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "error": str(e),
                }
            )
            raise HTTPException(status_code=500, detail="Error unlinking triggers")

    async def list_children(self, parent_id: str):
        """
        Lista todos los triggers hijos asociados a un trigger padre y registra la operación.

        :param parent_id: ID del trigger padre.
        :return: Lista de triggers hijos.
        """
        t1 = T.time()
        try:
            children = await self.repository.get_children(parent_id)
            # Log de consulta de hijos
            L.debug(
                {
                    "event": "TRIGGERS_TRIGGERS.LIST.CHILDREN",
                    "parent_id": parent_id,
                    "count": len(children),
                    "time": T.time() - t1,
                }
            )
            return children
        except Exception as e:
            L.error(
                {
                    "event": "TRIGGERS_TRIGGERS.LIST.CHILDREN.ERROR",
                    "parent_id": parent_id,
                    "error": str(e),
                }
            )
            return []

    async def list_parents(self, child_id: str):
        """
        Lista todos los triggers padres asociados a un trigger hijo y registra la operación.

        :param child_id: ID del trigger hijo.
        :return: Lista de triggers padres.
        """
        t1 = T.time()
        try:
            parents = await self.repository.get_parents(child_id)
            # Log de consulta de padres
            L.debug(
                {
                    "event": "TRIGGERS_TRIGGERS.LIST.PARENTS",
                    "child_id": child_id,
                    "count": len(parents),
                    "time": T.time() - t1,
                }
            )
            return parents
        except Exception as e:
            L.error(
                {
                    "event": "TRIGGERS_TRIGGERS.LIST.PARENTS.ERROR",
                    "child_id": child_id,
                    "error": str(e),
                }
            )
            return []
