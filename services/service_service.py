"""Service service — business logic for VPN service management."""

import time
from models.service import Service, NewServiceDTO
from repositories.service_repo import service_repo


class ServiceService:
    def get_all(self) -> list[Service]:
        return service_repo.get_all()

    def get_by_id(self, service_id: str) -> Service | None:
        return service_repo.get_by_id(service_id)

    def get_by_category(self) -> dict[str, list[Service]]:
        return service_repo.get_by_category()

    def create(self, dto: NewServiceDTO) -> Service:
        service = Service(
            id=f"svc-{int(time.time() * 1000)}",
            name=dto.name,
            endpoint=dto.endpoint,
            category=dto.category,
        )
        return service_repo.add(service)

    def count(self) -> int:
        return service_repo.count()


service_service = ServiceService()
