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
        with self._lock:
            return any(
                d.get("roleId") == role_id and d.get("serviceId") == service_id
                for d in self._read_raw()
            )

    def get_for_role(self, role_id: str) -> list[AccessEntry]:
        with self._lock:
            return [
                self._deserialize(d)
                for d in self._read_raw()
                if d.get("roleId") == role_id
            ]

    def toggle(self, role_id: str, service_id: str) -> list[AccessEntry]:
        with self._lock:
            data = self._read_raw()
            exists = any(
                d.get("roleId") == role_id and d.get("serviceId") == service_id
                for d in data
            )
            if exists:
                data = [
                    d for d in data
                    if not (d.get("roleId") == role_id and d.get("serviceId") == service_id)
                ]
            else:
                data.append({"roleId": role_id, "serviceId": service_id})
            self._write_raw(data)
            return [self._deserialize(d) for d in data]

    def remove_role(self, role_id: str) -> None:
        """Remove all entries for a role."""
        with self._lock:
            data = [d for d in self._read_raw() if d.get("roleId") != role_id]
            self._write_raw(data)


access_repo = AccessRepository()
