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
    serialized_results = {node_id: result.model_dump() for node_id, result in results.items()}
    print(serialized_results)
    return {"status": "ok", "results": serialized_results}
