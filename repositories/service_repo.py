from models.service import Service
from repositories.base import BaseRepository
from db.tables import ServiceRow


class ServiceRepository(BaseRepository[Service]):
    _Row = ServiceRow

    def _to_model(self, row: ServiceRow) -> Service:
        return Service(
            id=row.id,
            name=row.name,
            endpoint=row.endpoint,
            category=row.category,
        )

    def _to_row(self, item: Service) -> ServiceRow:
        return ServiceRow(
            id=item.id,
            name=item.name,
            endpoint=item.endpoint,
            category=item.category,
        )

    def get_by_category(self) -> dict[str, list[Service]]:
        grouped: dict[str, list[Service]] = {}
        for s in self.get_all():
            grouped.setdefault(s.category, []).append(s)
        return grouped


service_repo = ServiceRepository()
