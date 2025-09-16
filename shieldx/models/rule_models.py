from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Optional, Any
from bson import ObjectId

class TargetModel(BaseModel):
    alias: Optional[str] = None
    bucket_id: Optional[str] = None
    key: Optional[str] = None
    method: Optional[str] = None

    @field_validator("alias", mode="before")
    def accept_legacy_string(cls, v, values):
        """
        Permitir que target venga como string (legacy) y lo convierta a TargetModel.
        """
        if isinstance(v, str):
            # devolvemos un dict compatible
            return v  
        return v

    @model_validator(mode="before")
    def legacy_as_alias(cls, values):
        """
        Si todo el objeto es un string, convertirlo a alias.
        """
        if isinstance(values, str):
            return {"alias": values}
        return values

    @model_validator(mode="after")
    def validate_target(self) -> "TargetModel":
        if not self.alias and not (self.bucket_id and self.key):
            raise ValueError("Se requiere 'alias' o ('bucket_id' + 'key')")
        return self
    
class ParameterDetailModel(BaseModel):
    """
    Modelo que representa un parámetro dentro de una Regla.

    Puede ser:
        - un literal directo (int, str, bool, etc.)
        - o un objeto con información enriquecida (ref/$ref, type, name, description, value)
    """
    ref: Optional[str] = None
    ref_dollar: Optional[str] = Field(default=None, alias="$ref")
    value: Optional[Any] = None
    type_: Optional[str] = Field(default=None, alias="type")
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }
    @model_validator(mode="before")
    def accept_literal(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, (str, int, float, bool, list)):
            return {"value": v}
        return v

    
    @model_validator(mode="after")
    def validate_ref_or_value(self) -> "ParameterDetailModel":
        # Aceptar ref/$ref/value
        if self.ref or self.ref_dollar or self.value is not None:
            return self
        # Compatibilidad con legacy: type + description
        if self.type_ and self.description:
            return self
        raise ValueError("El parámetro debe tener 'ref'/'$ref' o un 'value'.")

class ParametersBlock(BaseModel):
    init: Dict[str, ParameterDetailModel] = Field(default_factory=dict)
    call: Dict[str, ParameterDetailModel] = Field(default_factory=dict)

    model_config = {"populate_by_name": True, "from_attributes": True}

class RuleModel(BaseModel):
    """
    Modelo que representa una regla de ejecución utilizada para activar funciones dentro del sistema ShieldX.

    Cada regla está vinculada a un `trigger` y define el objetivo (`target`) de ejecución junto con
    los parámetros requeridos por la función a invocar.

    Atributos:
    - rule_id: Identificador único de la regla (alias de `_id`, generado por MongoDB).
    - target: Ruta completa del método o función a ejecutar.
    - parameters: Diccionario de parámetros requeridos, donde la clave es el nombre del parámetro
                    y el valor es un objeto `ParameterDetailModel`.
    """

    rule_id: Optional[str] = Field(default=None, alias="_id")
    target: TargetModel
    parameters: ParametersBlock

    @field_validator("rule_id", mode="before")
    def convert_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @model_validator(mode="after")
    def validate_required_parameters(self) -> "RuleModel":
        # Ejemplo: validaciones según alias
        """
        Validación flexible: solo asegura que los parámetros tengan tipos válidos
        y que respeten el esquema de ParameterDetailModel.
        Ya no fuerza parámetros obligatorios por alias.
        """
        for block in [self.parameters.init, self.parameters.call]:
            for key, param in block.items():
                # Solo validamos que sea un ParameterDetailModel válido
                if not isinstance(param, ParameterDetailModel):
                    raise ValueError(f"Parámetro '{key}' no es válido")
        return self
    
    def dump(self) -> dict:
        """
        Exporta el modelo en formato dict, eliminando todos los campos None
        en todos los niveles, listo para persistir en Mongo.
        """
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )