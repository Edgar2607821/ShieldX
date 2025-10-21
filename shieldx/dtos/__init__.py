from pydantic import BaseModel

class ChoreographyResultDTO(BaseModel):
    node_id: str
    status: str
    output_url: str
    error_message: str = ""



