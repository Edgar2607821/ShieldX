from fastapi import APIRouter, Depends, Body

router = APIRouter()


@router.post("/choreography/run")
async def run_choreography():
    """
    Recibe un JSON desde la UI que describe la coreografía 
    (grafo o YAML ) y lo interpreta para ejecutarlo con AXO.
    """
    pass