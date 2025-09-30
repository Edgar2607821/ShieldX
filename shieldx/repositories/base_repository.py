from typing import Optional, TypeVar, Generic, Type
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from shieldx.log.logger_config import get_logger
from fastapi import HTTPException

L = get_logger(__name__)

"""
    Se declara un a variable llamada "T" la cual es igual a la creacion de una variable de tipo
    llamada "T" donde T debe de ser una clase que herede de BaseModel(Pydantic)
"""
T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Clase base genérica para operaciones CRUD sobre colecciones MongoDB 
    usando modelos Pydantic como esquema de validación.

    Esta clase abstrae la lógica común que comparten los repositorios 
    específicos del proyecto ShieldX, tales como:
    - EventsRepository
    - EventTypeRepository
    - TriggersRepository
    - RulesRepository

    Al parametrizar con TypeVar T, se garantiza compatibilidad tipada 
    con los modelos usados (como EventModel, TriggerModel, etc.).

    Atributos:
        collection (AsyncIOMotorCollection): Colección MongoDB asíncrona.
        model (Type[T]): Clase del modelo Pydantic que representa los documentos.

    Ejemplo de uso:
        repo = BaseRepository(collection=db["events"], model=EventModel)
    """
    def __init__(self, collection: AsyncIOMotorCollection, model: Type[T]):
        """
        Inicializa el repositorio con la colección y el modelo correspondiente.

        Args:
            collection (AsyncIOMotorCollection): Colección MongoDB objetivo.
            model (Type[T]): Modelo Pydantic usado para validar documentos.
        """
        self.collection = collection
        self.model = model

    async def find_one(self, query: dict) -> T | None:
        """
        Busca un único documento en la colección según el filtro proporcionado.

        Args:
            query (dict): Diccionario con los criterios de búsqueda.

        Returns:
            T: Instancia del modelo si se encuentra el documento, 
                None en caso contrario.
        """
        try:
            doc = await self.collection.find_one(query)
            return self.model(**doc) if doc else None
        except PyMongoError as e:
            L.error({            
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail="Database error in find_one")


    async def insert_one(self, data: T) -> str:
        """
        Inserta un nuevo documento validado por el modelo en la colección.

        Args:
            data (T): Objeto del modelo a insertar.

        Returns:
            str: ID del documento insertado (como string).
        """
        try:        
            if hasattr(data, "dump"):
                doc = data.dump()
            else:
                doc = data.model_dump(by_alias=True, exclude_none=True)
            result = await self.collection.insert_one(doc)
            return str(result.inserted_id)
        except PyMongoError as e:
            L.error({            
            "error": str(e)
            })
            raise HTTPException(status_code=500, detail="Database error in insert_one")
    

    async def update_one(self, query: dict, data: T |dict) -> Optional[T]:
        """
        Actualiza un documento existente en la colección.

        Args:
            query (dict): Filtro para localizar el documento a actualizar.
            data (T | dict): Datos a actualizar, ya sea un modelo Pydantic 
            o un diccionario.

        Returns:
            Optional[T]: Documento actualizado como instancia del modelo, 
            o None si no se modificó.
        """
        try:
            if isinstance(data, BaseModel):
                if hasattr(data, "dump"):
                    update_data = data.dump()
                else:
                    update_data = data.model_dump(by_alias=True, exclude_none=True)
            elif isinstance(data, dict):
                update_data = data
            else:
                raise TypeError(f"Expected BaseModel or dict, got {type(data).__name__}")

            result = await self.collection.update_one(query, {"$set": update_data})
            """
            Este resultado incluye información sobre lo que pasó al intentar actualizar.
            .modified_count indica cuántos documentos fueron realmente modificados.
            """
            if result.modified_count > 0:
                updated_doc = await self.collection.find_one(query)
                if updated_doc:
                    updated_doc["id"] = str(updated_doc["_id"])  # opcional si usas alias
                    return self.model(**updated_doc)

            return None
        except PyMongoError as e:
            L.error({            
                "error": str(e)
                })
            raise HTTPException(status_code=500, detail="Database error in update_one")
        except TypeError as e:
            L.error({            
                "error": str(e)
                })
            raise HTTPException(status_code=400, detail="Type error in update_one")
    

    async def delete_one(self, query: dict) -> bool:
        """
        Elimina un documento de la colección según el filtro proporcionado.

        Args:
            query (dict): Filtro de eliminación.

        Returns:
            bool: True si se eliminó al menos un documento, False en caso contrario.
        """
        try:
            result = await self.collection.delete_one(query)
            return result.deleted_count > 0
        except PyMongoError as e:
            L.error({            
            "error": str(e)
            })
            raise HTTPException(status_code=500, detail="Database error in delete_one")

    async def find_all(self) -> list[T]:
        """
        Recupera todos los documentos de la colección y los convierte al modelo.

        Returns:
            list[T]: Lista de instancias del modelo.
        """
        try:    
            cursor = self.collection.find()
            return [self.model(**doc) async for doc in cursor]
        except PyMongoError as e:
            L.error({
                "error": str(e)
            })
            raise HTTPException(status_code= 500, detail="Database error in find_all")
