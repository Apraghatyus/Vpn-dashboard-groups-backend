from models.access import AccessEntry
from repositories.base import BaseRepository
from config import Config


class AccessRepository(BaseRepository[AccessEntry]):
    def __init__(self):
        super().__init__(
            filepath=Config.ACCESS_FILE,
            serializer=AccessEntry.to_dict,
            deserializer=AccessEntry.from_dict,
        )

    def has_access(self, role_id: str, service_id: str) -> bool:
        return any(
            e.role_id == role_id and e.service_id == service_id
            for e in self.get_all()
        )

    def get_for_role(self, role_id: str) -> list[AccessEntry]:
        return [e for e in self.get_all() if e.role_id == role_id]

    def toggle(self, role_id: str, service_id: str) -> list[AccessEntry]:
        entries = self.get_all()
        exists = any(
            e.role_id == role_id and e.service_id == service_id for e in entries
        )
        if exists:
            entries = [
                e for e in entries
                if not (e.role_id == role_id and e.service_id == service_id)
            ]
        else:
            entries.append(AccessEntry(role_id=role_id, service_id=service_id))

        self.replace_all(entries)
        return entries

    def remove_role(self, role_id: str) -> None:
        """Remove all entries for a role."""
        entries = [e for e in self.get_all() if e.role_id != role_id]
        self.replace_all(entries)


access_repo = AccessRepository()
