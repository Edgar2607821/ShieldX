from fastapi import APIRouter, Depends, HTTPException, status
from shieldx.db import get_database
from shieldx.models import RuleModel
from shieldx.repositories import RuleRepository
from shieldx.services import RuleService
from shieldx.log.logger_config import get_logger
import time as T
import shieldx_core.dtos as DTOS

router = APIRouter()
L = get_logger(__name__)

def get_service(db=Depends(get_database)):
    repository = RuleRepository(db)
    return RuleService(repository)

@router.post(
    "/rules",
    response_model=DTOS.MessageWithIDDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva regla",
    description="Crea una regla nueva especificando el `target` a ejecutar y sus `parameters` correspondientes."
)
async def create_rule(data: DTOS.RuleCreateDTO, service: RuleService = Depends(get_service)):
    t1 = T.time()
    rule_id = await service.create_rule(data)
    # Log de creación
    L.info({
        "event": "API.RULE.CREATED",
        "rule_id": rule_id,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message= "Rule created",id=rule_id)

@router.get(
    "/rules",
    response_model=list[DTOS.RuleResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar todas las reglas",
    description="Devuelve una lista con todas las reglas existentes en la base de datos."
)
async def list_rules(service: RuleService = Depends(get_service)):
    t1 = T.time()
    rules = await service.list_rules()
    # Log de consulta
    L.debug({
        "event": "API.RULE.LISTED",
        "count": len(rules),
        "time": T.time() - t1
    })
    return [DTOS.RuleResponseDTO.model_validate(r.model_dump(by_alias=True)) for r in rules]


@router.get(
    "/rules/{rule_id}",
    response_model=DTOS.RuleResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Obtener una regla por ID",
    description="Recupera una regla específica utilizando su identificador único."
)
async def get_rule(rule_id: str, service: RuleService = Depends(get_service)):
    t1 = T.time()
    rule = await service.get_rule(rule_id)
    if not rule:
        L.warning({
            "event": "API.RULE.NOT_FOUND",
            "rule_id": rule_id,
            "time": T.time() - t1
        })
        raise HTTPException(status_code=404, detail="Rule not found")
    L.debug({
        "event": "API.RULE.FETCHED",
        "rule_id": rule_id,
        "time": T.time() - t1
    })
    return DTOS.RuleResponseDTO.model_validate(rule.model_dump(by_alias=True))


@router.put(
    "/rules/{rule_id}",
    status_code=status.HTTP_200_OK,
    response_model=DTOS.MessageWithIDDTO,
    summary="Actualizar una regla existente",
    description="Actualiza completamente una regla mediante su ID. Se debe enviar el objeto `RuleModel` actualizado."
)
async def update_rule(rule_id: str, data: DTOS.RuleUpdateDTO, service: RuleService = Depends(get_service)):
    t1 = T.time()
    existing = await service.get_rule(rule_id)
    if not existing:
        L.warning({
            "event": "API.RULE.UPDATE.NOT_FOUND",
            "rule_id": rule_id,
            "time": T.time() - t1
        })
        raise HTTPException(status_code=404, detail="Rule not found")
    await service.update_rule(rule_id, data)
    L.info({
        "event": "API.RULE.UPDATED",
        "rule_id": rule_id,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message="Rule updated", id=str(existing.rule_id))


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una regla",
    description="Elimina de forma permanente una regla identificada por su ID."
)
async def delete_rule(rule_id: str, service: RuleService = Depends(get_service)):
    t1 = T.time()
    await service.delete_rule(rule_id)
    L.info({
        "event": "API.RULE.DELETED",
        "rule_id": rule_id,
        "time": T.time() - t1
    })
