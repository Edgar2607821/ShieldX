from fastapi import HTTPException
from shieldx.log.logger_config import get_logger
from shieldx.repositories import RulesTriggerRepository
import time as T

L = get_logger(__name__)

class RulesTriggerService:
    """
    Servicio encargado de gestionar la relación entre triggers y reglas,
    utilizando la colección intermedia `rules_trigger` para vincular reglas a triggers.
    """

    def __init__(self, repository: RulesTriggerRepository):
        """
        Inicializa el servicio con una instancia del repositorio correspondiente.

        :param repository: Instancia de RulesTriggerRepository para interactuar con la base de datos.
        """
        self.repository = repository

    async def link_rule(self, trigger_id: str, rule_id: str):
        """
        Crea una asociación entre un trigger y una regla y registra la operación.

        :param trigger_id: ID del trigger.
        :param rule_id: ID de la regla que se desea vincular.
        :return: Resultado de la operación de enlace.
        """
        t1 = T.time()
        try:
            result = await self.repository.link(trigger_id, rule_id)
            if result:
                # Log de vínculo exitoso
                L.info({
                    "event": "RULE_TRIGGER.LINKED",
                    "trigger_id": trigger_id,
                    "rule_id": rule_id,
                    "time": T.time() - t1
                })
            else:
                # Log si ya existía la relación
                L.warning({
                    "event": "RULE_TRIGGER.LINK.EXISTS",
                    "trigger_id": trigger_id,
                    "rule_id": rule_id,
                    "time": T.time() - t1
                })
            return result
        except Exception as e:
            L.error({"event": "RULE_TRIGGER.LINK.ERROR", "trigger_id": trigger_id, "rule_id": rule_id, "error": str(e)})
            raise HTTPException(status_code=500, detail="Error linking rule")

    async def unlink_rule(self, trigger_id: str, rule_id: str):
        """
        Elimina la asociación entre una regla y un trigger y registra la operación.

        :param trigger_id: ID del trigger.
        :param rule_id: ID de la regla que se desea desvincular.
        """
        t1 = T.time()
        try:
            await self.repository.unlink(trigger_id, rule_id)
            # Log de desvinculación
            L.info({
                "event": "RULE_TRIGGER.UNLINKED",
                "trigger_id": trigger_id,
                "rule_id": rule_id,
                "time": T.time() - t1
            })
        except Exception as e:
            L.error({"event": "RULE_TRIGGER.UNLINK.ERROR", 
                    "trigger_id": trigger_id, 
                    "rule_id": rule_id, 
                    "error": str(e)})
            raise HTTPException(status_code=500, detail="Error unlinking rule")
        
    async def list_rules(self, trigger_id: str):
        """
        Lista todas las reglas asociadas a un trigger específico y registra la operación.

        :param trigger_id: ID del trigger.
        :return: Lista de reglas asociadas.
        """
        t1 = T.time()
        try:
            rules = await self.repository.list_by_trigger(trigger_id)
            # Log de consulta
            L.debug({
                "event": "RULE_TRIGGER.LIST.BY_TRIGGER",
                "trigger_id": trigger_id,
                "count": len(rules),
                "time": T.time() - t1
            })
            return rules
        except Exception as e:
            L.error({"event": "RULE_TRIGGER.LIST.ERROR", 
                    "trigger_id": trigger_id, 
                    "error": str(e)})
            return []