from fastapi import APIRouter, Depends, status
from typing import List
from shieldx.models import TriggerModel
from shieldx.services import TriggerService
from shieldx.db import get_database
from shieldx.repositories import TriggersRepository
from shieldx.log.logger_config import get_logger
import time as T
import shieldx_core.dtos as DTOS


router = APIRouter()
L = get_logger(__name__)

# Crea la instancia del servicio pasando la colección MongoDB

def get_triggers_service(db=Depends(get_database)):
    repository = TriggersRepository(db)
    return TriggerService(repository)

@router.post(
    "/triggers/",
    response_model=DTOS.MessageWithIDDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo trigger",
    description=(
        "Crea un nuevo trigger en la base de datos. "
        "El trigger debe incluir un nombre único y una regla (`RuleModel`) "
        "que contenga el `target` y un diccionario de `parameters`, definidos como `ParameterDetailModel`."
    ),
)
async def create_trigger(trigger: DTOS.TriggerCreateDTO, service: TriggerService = Depends(get_triggers_service)):
    t1 = T.time()
    result = await service.create_trigger(trigger)
    L.info({
        "event": "API.TRIGGER.CREATED",
        "name": trigger.name,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message="Trigger Created", id=str(result.trigger_id))

@router.get(
    "/triggers/",
    response_model=List[DTOS.TriggerResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los triggers",
    description=(
        "Recupera todos los triggers almacenados en la base de datos. "
        "Cada trigger contiene su nombre, reglas asociadas y detalles sobre su configuración."
    )
)
async def get_all_triggers(service: TriggerService = Depends(get_triggers_service)):
    t1 = T.time()
    triggers = await service.get_all_triggers()
    L.debug({
        "event": "API.TRIGGER.LISTED",
        "count": len(triggers),
        "time": T.time() - t1
    })
    return [DTOS.TriggerResponseDTO.model_validate(t.model_dump(by_alias=True)) for t in triggers]

@router.get(
    "/triggers/{name}",
    response_model=DTOS.TriggerResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Obtener un trigger por nombre",
    description=(
        "Devuelve un trigger específico dado su nombre único. "
        "Se pueden consultar los detalles de su configuración y reglas asociadas."
    )
)
async def get_trigger(name: str, service: TriggerService = Depends(get_triggers_service)):
    t1 = T.time()
    trigger = await service.get_trigger(name)
    L.debug({
        "event": "API.TRIGGER.FETCHED",
        "name": name,
        "time": T.time() - t1
    })
    return DTOS.TriggerResponseDTO.model_validate(trigger.model_dump(by_alias=True))

@router.put(
    "/triggers/{name}",
    response_model=DTOS.MessageWithIDDTO,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un trigger por nombre",
    description=(
        "Actualiza la definición completa de un trigger existente identificado por su nombre. "
        "Se debe enviar el objeto `TriggerModel` actualizado, incluyendo cualquier cambio en sus reglas y parámetros."
    )
)
async def update_trigger(name: str, updated_trigger: DTOS.TriggerCreateDTO, service: TriggerService = Depends(get_triggers_service)):
    t1 = T.time()
    updated = await service.update_trigger(name, updated_trigger)
    L.info({
        "event": "API.TRIGGER.UPDATED",
        "name": name,
        "time": T.time() - t1
    })
    return DTOS.MessageWithIDDTO(message="Trigger Updated", id= str(updated.trigger_id))

@router.delete(
    "/triggers/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un trigger por nombre",
    description=(
        "Elimina un trigger de la base de datos según su nombre. "
        "Esta operación es permanente y no se puede deshacer."
    )
)
async def delete_trigger(name: str, service: TriggerService = Depends(get_triggers_service)):
    t1 = T.time()
    await service.delete_trigger(name)
    L.info({
        "event": "API.TRIGGER.DELETED",
        "name": name,
        "time": T.time() - t1
    })
