from models.role import Role
from repositories.base import BaseRepository
from config import Config


class RoleRepository(BaseRepository[Role]):
    def __init__(self):
        super().__init__(
            filepath=Config.ROLES_FILE,
            serializer=Role.to_dict,
            deserializer=Role.from_dict,
        )


role_repo = RoleRepository()
