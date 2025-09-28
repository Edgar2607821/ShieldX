from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class Node(BaseModel):
    id: str
    alias: Optional[str] = None
    type: Optional[str] = None
    label: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class Connection(BaseModel):
    from_: str = Field(..., alias="from")
    to: str


class GraphSpec(BaseModel):
    nodes: List[Node]
    connections: List[Connection] = []


class ChoreographyRequest(BaseModel):
    """
    Representa la coreografía enviada desde la UI.
    Puede venir como JSON (grafo) o directamente YAML.
    """
    format: str  # "json" o "yaml"
    content: str | GraphSpec  # puede ser texto (YAML) o dict validado (GraphSpec)
