from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from shieldx.models import EventModel
from shieldx.services import EventsService
from shieldx.repositories import EventsRepository
from shieldx.repositories import EventTypeRepository
from shieldx.db import get_database
from shieldx.log.logger_config import get_logger
import time as T
import shieldx_core.dtos as DTOS

router = APIRouter()
L = get_logger(__name__)

def get_events_service(db=Depends(get_database)) -> EventsService:
    """
    Inicializa EventsService con acceso a EventsRepository y EventTypeRepository
    para validar existencia antes de crear eventos.
    """
    event_repo = EventsRepository(db["events"])
    event_type_repo = EventTypeRepository(db)
    return EventsService(event_repo, event_type_repo)

@router.get("/events", response_model=List[DTOS.EventResponseDTO], summary="Listar eventos",
    description="Recupera una lista de eventos registrados en el sistema...")
async def get_events(
    events_service: EventsService = Depends(get_events_service),
    service_id: Optional[str] = Query(None, description="Filtrar por service_id"),
    microservice_id: Optional[str] = Query(None, description="Filtrar por microservice_id"),
    function_id: Optional[str] = Query(None, description="Filtrar por function_id"),
    limit: int = Query(100, description="Cantidad máxima de eventos a devolver"),
    skip: int = Query(0, description="Número de eventos a omitir para paginación")
):
    t1 = T.time()
    events = await events_service.get_events_filtered(
        service_id=service_id, microservice_id=microservice_id,
        function_id=function_id, limit=limit, skip=skip
    )
    L.debug({
        "event": "API.EVENT.LIST.FILTERED",
        "filters": {"service_id": service_id, 
                    "microservice_id": microservice_id, 
                    "function_id": function_id},
        "count": len(events),
        "time": T.time() - t1
    })
    return [DTOS.EventResponseDTO.model_validate(e) for e in events]


@router.get("/events/service/{service_id}", 
            response_model=List[DTOS.EventResponseDTO], 
            summary="Buscar eventos por service_id",
            description="Recupera todos los eventos asociados al `service_id` especificado.")
async def get_events_by_service(service_id: str, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    events = await events_service.get_events_filtered(service_id=service_id)
    L.debug({
        "event": "API.EVENT.LIST.BY_SERVICE",
        "service_id": service_id,
        "count": len(events),
        "time": T.time() - t1
    })
    return [DTOS.EventResponseDTO.model_validate(e) for e in events]

@router.get("/events/microservice/{microservice_id}", 
            response_model=List[DTOS.EventResponseDTO], 
            summary="Buscar eventos por microservice_id",
            description="Recupera todos los eventos asociados al `microservice_id` especificado.")
async def get_events_by_microservice(microservice_id: str, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    events = await events_service.get_events_filtered(microservice_id=microservice_id)
    L.debug({
        "event": "API.EVENT.LIST.BY_MICROSERVICE",
        "microservice_id": microservice_id,
        "count": len(events),
        "time": T.time() - t1
    })
    return [DTOS.EventResponseDTO.model_validate(e) for e in events]


@router.get("/events/function/{function_id}", 
            response_model=List[DTOS.EventResponseDTO], 
            summary="Buscar eventos por function_id",
            description="Recupera todos los eventos asociados al `function_id` especificado.")
async def get_events_by_function(function_id: str, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    events = await events_service.get_events_filtered(function_id=function_id)
    L.debug({
        "event": "API.EVENT.LIST.BY_FUNCTION",
        "function_id": function_id,
        "count": len(events),
        "time": T.time() - t1
    })
    return [DTOS.EventResponseDTO.model_validate(e) for e in events]


@router.get("/events/{event_id}", 
            response_model=DTOS.EventResponseDTO, 
            summary="Obtener evento por ID",
            description="Recupera los detalles de un evento específico utilizando su `event_id`.")
async def get_event_by_id(event_id: str, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    event = await events_service.get_event_by_id(event_id)
    if not event:
        L.warning({
            "event": "API.EVENT.NOT_FOUND",
            "event_id": str(event.event_id),
            "time": T.time() - t1
        })
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    L.debug({
        "event": "API.EVENT.FETCHED",
        "event_id": str(event.event_id),
        "time": T.time() - t1
    })
    return DTOS.EventResponseDTO.model_validate(event.model_dump(by_alias=True))


@router.post("/events", 
            response_model=DTOS.MessageWithIDDTO, 
            summary="Crear un nuevo evento",
            description="Registra un nuevo evento en la base de datos utilizando el esquema definido en el modelo `EventModel`.",
            status_code=status.HTTP_201_CREATED)
async def create_event(event: DTOS.EventCreateDTO, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    created_event = await events_service.create_event(event)
    if not created_event:
        L.error({
            "event": "API.EVENT.CREATE.FAILED",
            "time": T.time() - t1
        })
        raise HTTPException(status_code=500, detail="No se pudo crear el evento")
    L.info({
        "event": "API.EVENT.CREATED",
        "event_id": created_event,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message="Evento creado exitosamente", id=created_event)


@router.put("/events/{event_id}", 
            response_model=DTOS.EventResponseDTO, 
            summary="Actualizar evento",
            description="Actualiza los campos de un evento existente utilizando su `event_id`.")
async def update_event(event_id: str, update_data: DTOS.EventUpdateDTO, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    updated_event = await events_service.update_event(event_id, update_data)
    if not updated_event:
        L.warning({
            "event": "API.EVENT.UPDATE.FAILED",
            "event_id": event_id,
            "time": T.time() - t1
        })
        raise HTTPException(status_code=404, detail="No se pudo actualizar el evento")
    L.info({
        "event": "API.EVENT.UPDATED",
        "event_id": event_id,
        "time": T.time() - t1
    })
    return DTOS.EventResponseDTO.model_validate(updated_event)

@router.delete("/events/{event_id}", 
            summary="Eliminar evento",
            status_code=status.HTTP_204_NO_CONTENT,
            description="Elimina un evento existente de la base de datos utilizando su `event_id`.")
async def delete_event(event_id: str, events_service: EventsService = Depends(get_events_service)):
    t1 = T.time()
    success = await events_service.delete_event(event_id)
    if not success:
        L.warning({
            "event": "API.EVENT.DELETE.FAILED",
            "event_id": event_id,
            "time": T.time() - t1
        })
        raise HTTPException(status_code=404, detail="No se pudo eliminar el evento")
    L.info({
        "event": "API.EVENT.DELETED",
        "event_id": event_id,
        "time": T.time() - t1
    })
    
