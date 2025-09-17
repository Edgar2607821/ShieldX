from motor.motor_asyncio import AsyncIOMotorDatabase
from shieldx.models import RuleModel
from shieldx.log.logger_config import get_logger
from shieldx.repositories import BaseRepository

L = get_logger(__name__)

class RuleRepository(BaseRepository[RuleModel]):
    """
    Repositorio encargado de realizar operaciones CRUD sobre la colección `rules`
    en la base de datos MongoDB.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(collection=db["rules"], model=RuleModel)
