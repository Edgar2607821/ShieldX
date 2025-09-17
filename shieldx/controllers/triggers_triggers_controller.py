from fastapi import APIRouter, Depends, status
from shieldx.db import get_database
from shieldx.services import TriggersTriggersService
from shieldx.repositories import TriggersTriggersRepository
from shieldx.log.logger_config import get_logger
import time as T
import shieldx_core.dtos as DTOS

router = APIRouter()
L = get_logger(__name__)

def get_service(db=Depends(get_database)):
    repo = TriggersTriggersRepository(db)
    return TriggersTriggersService(repo)

@router.get(
    "/triggers/{trigger_id}/children",
    response_model=list[DTOS.TriggersTriggersDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar triggers hijos",
    description="Devuelve todos los triggers hijos que son activados por el trigger padre especificado."
)
async def list_children(trigger_id: str, service: TriggersTriggersService = Depends(get_service)):
    t1 = T.time()
    children = await service.list_children(trigger_id)
    L.debug({
        "event": "API.TRIGGER.CHILDREN.LISTED",
        "parent_id": trigger_id,
        "count": len(children),
        "time": T.time() - t1
    })
    return [DTOS.TriggersTriggersDTO.model_validate(c.model_dump(by_alias=True)) for c in children]

@router.get(
    "/triggers/{trigger_id}/parents",
    response_model=list[DTOS.TriggersTriggersDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar triggers padres",
    description="Devuelve todos los triggers padres que activan al trigger especificado como hijo."
)
async def list_parents(trigger_id: str, service: TriggersTriggersService = Depends(get_service)):
    t1 = T.time()
    parents = await service.list_parents(trigger_id)
    L.debug({
        "event": "API.TRIGGER.PARENTS.LISTED",
        "child_id": trigger_id,
        "count": len(parents),
        "time": T.time() - t1
    })
    return [DTOS.TriggersTriggersDTO.model_validate(p.model_dump(by_alias=True)) for p in parents]

@router.post(
    "/triggers/{parent_id}/children/{child_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Vincular trigger hijo a trigger padre",
    description="Asocia un trigger hijo a un trigger padre, estableciendo que cuando se active el padre, también se dispare el hijo. Idempotente."
)
async def link_triggers(parent_id: str, child_id: str, service: TriggersTriggersService = Depends(get_service)):
    t1 = T.time()
    result = await service.link_triggers(parent_id, child_id)
    if result:
        L.info({
            "event": "API.TRIGGER.LINKED",
            "parent_id": parent_id,
            "child_id": child_id,
            "time": T.time() - t1
        })
    else:
        L.debug({
            "event": "API.TRIGGER.LINK.EXISTS",
            "parent_id": parent_id,
            "child_id": child_id,
            "time": T.time() - t1
        })

@router.delete(
    "/triggers/{parent_id}/children/{child_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desvincular trigger hijo de trigger padre",
    description="Elimina la relación entre un trigger padre y un trigger hijo. Si ya estaba desvinculado, también responde 204 (idempotente)."
)
async def unlink_triggers(parent_id: str, child_id: str, service: TriggersTriggersService = Depends(get_service)):
    t1 = T.time()
    await service.unlink_triggers(parent_id, child_id)
    L.info({
        "event": "API.TRIGGER.UNLINKED",
        "parent_id": parent_id,
        "child_id": child_id,
        "time": T.time() - t1
    })
