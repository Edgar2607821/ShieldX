from fastapi import APIRouter, Depends, Request
from shieldx_core.dtos import EnrichedGraphSpecDTO
from shieldx.services.choreography_run_service import ChoreographyRunServiece

router = APIRouter()

def get_service() -> ChoreographyRunServiece:
    return ChoreographyRunServiece()

@router.post("/choreography/run")
async def run_choreography(graph: EnrichedGraphSpecDTO,service: ChoreographyRunServiece = Depends(get_service)):
    """
    Recibe un JSON desde la UI que describe la coreografía 
    y la ejecuta con AXO.
    """
    results = await service.run(graph)
    return {"status": "ok", "results": results}
