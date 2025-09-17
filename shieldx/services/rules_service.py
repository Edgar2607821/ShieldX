from fastapi import HTTPException
from shieldx.repositories import RuleRepository
from shieldx.models import RuleModel
from shieldx.log.logger_config import get_logger
from bson import ObjectId
import time as T

L = get_logger(__name__)

class RuleService:
    """
    Servicio encargado de gestionar la lógica relacionada con las reglas (`Rule`),
    incluyendo su creación, consulta, actualización y eliminación.
    """

    def __init__(self, repository: RuleRepository):
        """
        Inicializa el servicio con una instancia del repositorio correspondiente.

        :param repository: Instancia de RuleRepository para interactuar con la base de datos.
        """
        self.repository = repository

    async def create_rule(self, rule: RuleModel) -> str:
        """
        Crea una nueva regla en la base de datos y registra la operación.

        :param rule: Objeto RuleModel con los datos de la regla.
        :return: ID de la nueva regla creada.
        """
        t1 = T.time()
        try:
            #rule_id = await self.repository.create(rule.model_dump(by_alias=True, exclude_none=True))
            rule_id = await self.repository.insert_one(rule)
            L.info({
                "event": "RULE.CREATED",
                "rule_id": rule_id,
                "time": T.time() - t1
            })
            return rule_id
        except Exception as e:
            L.error({"event": "RULE.CREATE.ERROR", 
                    "error": str(e)})
            raise HTTPException(status_code=500, detail="Error creating rule")

    async def list_rules(self):
        """
        Devuelve todas las reglas almacenadas en la base de datos y registra la operación.

        :return: Lista de objetos RuleModel.
        """
        t1 = T.time()
        try:
            rules = await self.repository.find_all()
            L.debug({
                "event": "RULE.LIST",
                "count": len(rules),
                "time": T.time() - t1
            })
            return rules
        except Exception as e:
            L.error({"event": "RULE.LIST.ERROR", "error": str(e)})
            return []

    async def get_rule(self, rule_id: str):
        """
        Obtiene una regla específica a partir de su identificador único y registra la operación.

        :param rule_id: ID de la regla a consultar.
        :return: Objeto RuleModel si existe, de lo contrario lanza HTTPException 404.
        """
        t1 = T.time()
        try:
            rule = await self.repository.find_one({"_id": ObjectId(rule_id)})
        except HTTPException:
            raise
        except Exception as e:
            L.error({"event": "RULE.GET.ERROR", 
                    "rule_id": rule_id, 
                    "error": str(e)})
            raise HTTPException(status_code=500, detail="Error fetching rule")
        if not rule:
            L.warning({
                "event": "RULE.NOT_FOUND",
                "rule_id": rule_id,
                "time": T.time() - t1
            })
            raise HTTPException(status_code=404, detail="Rule not found")
        L.debug({
            "event": "RULE.FETCHED",
            "rule_id": rule_id,
            "time": T.time() - t1
        })
        return rule

    async def update_rule(self, rule_id: str, rule: RuleModel):
        """
        Actualiza los datos de una regla existente y registra la operación.

        :param rule_id: ID de la regla a actualizar.
        :param rule: Objeto RuleModel con los datos actualizados.
        """
        t1 = T.time()
        try:
            await self.repository.update_one({"_id": ObjectId(rule_id)}, rule)
            L.info({
                "event": "RULE.UPDATED",
                "rule_id": rule_id,
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "RULE.UPDATE.ERROR", "rule_id": rule_id, "error": str(e)})
            raise HTTPException(status_code=500, detail="Error updating rule")

    async def delete_rule(self, rule_id: str):
        """
        Elimina una regla de la base de datos por su ID y registra la operación.

        :param rule_id: ID de la regla a eliminar.
        """
        t1 = T.time()
        try:
            rule = await self.repository.find_one({"_id": ObjectId(rule_id)})
            if not rule:
                L.warning({
                    "event": "RULE.DELETE.NOT_FOUND",
                    "rule_id": rule_id,
                    "time": T.time() - t1
                })
                raise HTTPException(status_code=404, detail="Rule not found")
            await self.repository.delete_one({"_id": ObjectId(rule_id)})
            L.info({
                "event": "RULE.DELETED",
                "rule_id": rule_id,
                "time": T.time() - t1
            })
        except HTTPException:
            raise
        except Exception as e:
            L.error({"event": "RULE.DELETE.ERROR", "rule_id": rule_id, "error": str(e)})
            raise HTTPException(status_code=500, detail="Error deleting rule")