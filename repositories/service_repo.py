from models.service import Service
from repositories.base import BaseRepository
from config import Config


class ServiceRepository(BaseRepository[Service]):
    def __init__(self):
        super().__init__(
            filepath=Config.SERVICES_FILE,
            serializer=Service.to_dict,
            deserializer=Service.from_dict,
        )

    def get_by_category(self) -> dict[str, list[Service]]:
        grouped: dict[str, list[Service]] = {}
        for s in self.get_all():
            grouped.setdefault(s.category, []).append(s)
        return grouped


service_repo = ServiceRepository()
