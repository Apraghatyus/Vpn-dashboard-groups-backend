from models.user import User
from repositories.base import BaseRepository
from config import Config


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(
            filepath=Config.USERS_FILE,
            serializer=User.to_storage_dict,
            deserializer=User.from_dict,
        )

    def get_by_username(self, username: str) -> User | None:
        for u in self.get_all():
            if u.username == username:
                return u
        return None


user_repo = UserRepository()
