from models.access import AccessEntry
from repositories.base import BaseRepository
from db.tables import AccessEntryRow


class AccessRepository(BaseRepository[AccessEntry]):
    _Row = AccessEntryRow

    def _to_model(self, row: AccessEntryRow) -> AccessEntry:
        return AccessEntry(role_id=row.role_id, service_id=row.service_id)

    def _to_row(self, item: AccessEntry) -> AccessEntryRow:
        return AccessEntryRow(role_id=item.role_id, service_id=item.service_id)

    # Composite PK — override get_by_id to avoid using it (not applicable here)
    def get_by_id(self, item_id: str, id_field: str = "id") -> AccessEntry | None:
        raise NotImplementedError("Use has_access() instead")

    def has_access(self, role_id: str, service_id: str) -> bool:
        with self._session() as s:
            return s.query(AccessEntryRow).filter_by(
                role_id=role_id, service_id=service_id
            ).count() > 0

    def get_for_role(self, role_id: str) -> list[AccessEntry]:
        with self._session() as s:
            rows = s.query(AccessEntryRow).filter_by(role_id=role_id).all()
            return [self._to_model(r) for r in rows]

    def toggle(self, role_id: str, service_id: str) -> list[AccessEntry]:
        with self._session() as s:
            existing = s.query(AccessEntryRow).filter_by(
                role_id=role_id, service_id=service_id
            ).first()
            if existing:
                s.delete(existing)
            else:
                s.add(AccessEntryRow(role_id=role_id, service_id=service_id))
            s.commit()
            return [self._to_model(r) for r in s.query(AccessEntryRow).all()]

    def remove_role(self, role_id: str) -> None:
        with self._session() as s:
            s.query(AccessEntryRow).filter_by(role_id=role_id).delete()


access_repo = AccessRepository()
