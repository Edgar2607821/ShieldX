from fastapi import APIRouter, Depends, status
from shieldx.services import EventsTriggersService
from shieldx.repositories import EventsTriggersRepository
from shieldx.db import get_database
from shieldx.log.logger_config import get_logger
import time as T
import shieldx_core.dtos as DTOS

router = APIRouter()
L = get_logger(__name__)

def get_service(db=Depends(get_database)):
    repo = EventsTriggersRepository(db)
    return EventsTriggersService(repo)

@router.get(
    "/event-types/{event_type_id}/triggers",
    response_model=list[DTOS.EventsTriggersDTO],
    status_code=200,
    summary="Listar triggers de un tipo de evento",
    description="Devuelve todos los triggers vinculados al tipo de evento especificado."
)
async def list_triggers(event_type_id: str, service: EventsTriggersService = Depends(get_service)):
    t1 = T.time()
    triggers = await service.list_triggers_for_event_type(event_type_id)
    # Log de consulta de triggers vinculados
    L.debug({
        "event": "API.EVENT_TRIGGER.LIST",
        "event_type_id": event_type_id,
        "count": len(triggers),
        "time": T.time() - t1
    })
    return [DTOS.EventsTriggersDTO.model_validate(t.model_dump(by_alias=True)) for t in triggers]


@router.post(
    "/event-types/{event_type_id}/triggers/{trigger_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Vincular trigger a tipo de evento",
    description="Asocia un trigger existente a un tipo de evento. Si ya existe la relación, no hace nada (idempotente)."
)
async def link_trigger(event_type_id: str, trigger_id: str, service: EventsTriggersService = Depends(get_service)):
    t1 = T.time()
    await service.link_trigger(event_type_id, trigger_id)
    # Log de vinculación
    L.info({
        "event": "API.EVENT_TRIGGER.LINKED",
        "event_type_id": event_type_id,
        "trigger_id": trigger_id,
        "time": T.time() - t1
    })

@router.put(
    "/event-types/{event_type_id}/triggers",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reemplazar triggers de tipo de evento",
    description="Reemplaza completamente la lista de triggers asociados a un tipo de evento."
)
async def replace_triggers(event_type_id: str, trigger_ids: list[str], service: EventsTriggersService = Depends(get_service)):
    t1 = T.time()
    await service.replace_triggers_for_event_type(event_type_id, trigger_ids)
    # Log de reemplazo de relaciones
    L.info({
        "event": "API.EVENT_TRIGGER.REPLACED",
        "event_type_id": event_type_id,
        "new_links_count": len(trigger_ids),
        "time": T.time() - t1
    })

@router.delete(
    "/event-types/{event_type_id}/triggers/{trigger_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desvincular trigger de tipo de evento",
    description="Elimina la relación entre un trigger y un tipo de evento. Si ya estaba desvinculado, también devuelve 204 (idempotente)."
)
async def unlink_trigger(event_type_id: str, trigger_id: str, service: EventsTriggersService = Depends(get_service)):
    t1 = T.time()
    await service.unlink_trigger(event_type_id, trigger_id)
    # Log de desvinculación
    L.info({
        "event": "API.EVENT_TRIGGER.UNLINKED",
        "event_type_id": event_type_id,
        "trigger_id": trigger_id,
        "time": T.time() - t1
    })
