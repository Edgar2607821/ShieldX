from fastapi import APIRouter, Depends, status
from shieldx.models import EventTypeModel
from shieldx.repositories import EventTypeRepository
from shieldx.services import EventTypeService
from shieldx.db import get_database
from shieldx.log.logger_config import get_logger
import shieldx_core.dtos as DTOS
from typing import List
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_service(db=Depends(get_database)):
    repository = EventTypeRepository(db)
    return EventTypeService(repository)


@router.post(
    "/event-types",
    response_model=DTOS.MessageWithIDDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un tipo de evento",
    description="Crea un nuevo tipo de evento que podrá ser asociado a uno o más triggers."
)
async def create_event_type(data: DTOS.EventTypeCreateDTO, service: EventTypeService = Depends(get_service)):
    t1 = T.time()
    event_type_id = await service.create_event_type(data)
    # Log de creación
    L.info({
        "event": "API.EVENT_TYPE.CREATED",
        "event_type_id": event_type_id,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message= "Event Type Created", id=event_type_id)

@router.get(
    "/event-types",
    response_model=List[DTOS.EventTypeResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar tipos de evento",
    description="Devuelve todos los tipos de evento registrados en el sistema."
)
async def list_event_types(service: EventTypeService = Depends(get_service)):
    t1 = T.time()
    event_types = await service.list_event_types()
    # Log de consulta de lista
    L.debug({
        "event": "API.EVENT_TYPE.LISTED",
        "count": len(event_types),
        "time": T.time() - t1
    })
    return [DTOS.EventTypeResponseDTO.model_validate(et.model_dump(by_alias=True)) for et in event_types]

@router.get(
    "/event-types/{type_id}",
    response_model=DTOS.EventTypeResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Obtener tipo de evento por ID",
    description="Obtiene un tipo de evento específico mediante su identificador único."
)
async def get_event_type(type_id: str, service: EventTypeService = Depends(get_service)):
    t1 = T.time()
    event_type = await service.get_event_type(type_id)
    # Log de consulta individual
    L.debug({
        "event": "API.EVENT_TYPE.FETCHED",
        "event_type_id": type_id,
        "time": T.time() - t1
    })
    return DTOS.EventTypeResponseDTO.model_validate(event_type.model_dump(by_alias=True))


@router.delete(
    "/event-types/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un tipo de evento",
    description="Elimina de forma permanente un tipo de evento según su identificador."
)
async def delete_event_type(type_id: str, service: EventTypeService = Depends(get_service)):
    t1 = T.time()
    await service.delete_event_type(type_id)
    # Log de eliminación
    L.info({
        "event": "API.EVENT_TYPE.DELETED",
        "event_type_id": type_id,
        "time": T.time() - t1
    })
