"""Access matrix entry — mirrors frontend IAccessEntry."""

from dataclasses import dataclass


@dataclass
class AccessEntry:
    role_id: str
    service_id: str

    def to_dict(self) -> dict:
        return {
            "roleId": self.role_id,
            "serviceId": self.service_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AccessEntry":
        return cls(
            role_id=data.get("roleId", data.get("role_id", "")),
            service_id=data.get("serviceId", data.get("service_id", "")),
        )
