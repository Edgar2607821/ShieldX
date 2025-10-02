from fastapi import APIRouter, Depends, Body
from shieldx.models.choreography_models import ChoreographyRequest
from shieldx.services.choreography_service import ChoreographyService
from shieldx import config

router = APIRouter()

SHIELDX_CLIENT_BASE_URL = config.SHIELDX_CLIENT_BASE_URL

def get_service() -> ChoreographyService:
    
    return ChoreographyService(base_url=SHIELDX_CLIENT_BASE_URL)

# ---------- 1. Endpoint JSON (UI) ----------
@router.post("/interpret")
async def interpret_choreography(
    request: ChoreographyRequest,
    service: ChoreographyService = Depends(get_service),
):
    """
    Recibe un JSON desde la UI que describe la coreografía 
    (grafo o YAML embebido) y lo interpreta con ShieldXClient.
    """
    return await service.interpret(request)


# ---------- 2. Endpoint YAML (archivo/texto) ----------
@router.post("/interpret/yaml")
async def interpret_choreography_yaml(
    payload: str = Body(..., media_type="application/x-yaml"),
    service: ChoreographyService = Depends(get_service),
):
    """
    Recibe directamente un archivo/texto YAML y lo interpreta con ShieldXClient.
    """
    request = ChoreographyRequest(format="yaml", content=payload)
    return await service.interpret(request)

@router.post("/choreography/run")
async def run_choreography(
    
):
    pass