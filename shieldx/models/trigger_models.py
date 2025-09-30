from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId

class TriggerModel(BaseModel):
    """
    Modelo que representa un trigger dentro del sistema ShieldX.

    Un trigger define un punto de activación que puede estar vinculado a uno o más tipos de evento,
    y que a su vez puede activar una o más reglas.

    Atributos:
    - trigger_id: Identificador único del trigger (alias de `_id`, generado por MongoDB).
    - name: Nombre único del trigger.
    """

    trigger_id: Optional[str] = Field(default=None, alias="_id")
    name: str
    depends_on: Optional[str] = None

    @field_validator("trigger_id", mode="before")
    def convert_object_id(cls, v):
        """
        Convierte un ObjectId de MongoDB en una cadena de texto.

        :param v: Valor del campo `_id` recibido desde la base de datos.
        :return: Representación en string del ObjectId.
        """
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }
