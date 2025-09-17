from fastapi import APIRouter, Depends, status
from shieldx.db import get_database
from shieldx.models import RuleModel
from shieldx.services import RulesTriggerService
from shieldx.services import RuleService
from shieldx.repositories import RulesTriggerRepository
from shieldx.repositories import RuleRepository
import shieldx_core.dtos as DTOS
from shieldx.log.logger_config import get_logger
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_service(db=Depends(get_database)):
    repo = RulesTriggerRepository(db)
    return RulesTriggerService(repo)

@router.get(
    "/triggers/{trigger_id}/rules",
    response_model=list[DTOS.RulesTriggerDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar reglas asociadas a un trigger",
    description="Devuelve todas las reglas actualmente vinculadas a un trigger específico."
)
async def list_rules(trigger_id: str, service: RulesTriggerService = Depends(get_service)):
    t1 = T.time()
    rules = await service.list_rules(trigger_id)
    L.debug({
        "event": "API.RULE_TRIGGER.LISTED",
        "trigger_id": trigger_id,
        "count": len(rules),
        "time": T.time() - t1
    })
    return [DTOS.RulesTriggerDTO.model_validate(r.model_dump(by_alias=True)) for r in rules]

@router.post(
    "/triggers/{trigger_id}/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Vincular regla a trigger",
    description="Asocia una regla existente a un trigger específico. Si ya está vinculada, no hace nada (idempotente)."
)
async def link_rule(trigger_id: str, rule_id: str, service: RulesTriggerService = Depends(get_service)):
    t1 = T.time()
    result = await service.link_rule(trigger_id, rule_id)
    if result:
        L.info({
            "event": "API.RULE_TRIGGER.LINKED",
            "trigger_id": trigger_id,
            "rule_id": rule_id,
            "time": T.time() - t1
        })
    else:
        L.warning({
            "event": "API.RULE_TRIGGER.LINK.EXISTS",
            "trigger_id": trigger_id,
            "rule_id": rule_id,
            "time": T.time() - t1
        })

@router.post(
    "/triggers/{trigger_id}/rules",
    response_model=DTOS.MessageWithIDDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear y vincular una nueva regla",
    description="Crea una nueva regla y la vincula automáticamente al trigger indicado."
)
async def create_and_link_rule(trigger_id: str, rule_data: DTOS.RuleCreateDTO, db=Depends(get_database)):
    t1 = T.time()
    # Crear la nueva regla
    rule_repo = RuleRepository(db)
    rule_service = RuleService(rule_repo)
    rule_id = await rule_service.create_rule(rule_data)

    # Vincular la nueva regla
    repo = RulesTriggerRepository(db)
    service = RulesTriggerService(repo)
    await service.link_rule(trigger_id, rule_id)

    L.info({
        "event": "API.RULE_TRIGGER.CREATED_AND_LINKED",
        "trigger_id": trigger_id,
        "rule_id": rule_id,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message= "Rule created and linked", id=rule_id)

@router.delete(
    "/triggers/{trigger_id}/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desvincular regla de trigger",
    description="Elimina la relación entre una regla y un trigger. Si no existe la relación, no hace nada (idempotente)."
)
async def unlink_rule(trigger_id: str, rule_id: str, service: RulesTriggerService = Depends(get_service)):
    t1 = T.time()
    await service.unlink_rule(trigger_id, rule_id)
    L.info({
        "event": "API.RULE_TRIGGER.UNLINKED",
        "trigger_id": trigger_id,
        "rule_id": rule_id,
        "time": T.time() - t1
    })
