"""VpnUser model — person who owns one or more VPN devices (peers)."""

from dataclasses import dataclass, field
import time


@dataclass
class VpnUser:
    id: str
    display_name: str
    email: str
    role_id: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "displayName": self.display_name,
            "email": self.email,
            "roleId": self.role_id,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VpnUser":
        return cls(
            id=data["id"],
            display_name=data.get("displayName", data.get("display_name", "")),
            email=data["email"],
            role_id=data.get("roleId", data.get("role_id", "")),
            created_at=data.get("createdAt", data.get("created_at", time.time())),
        )


@dataclass
class NewVpnUserDTO:
    display_name: str
    email: str
    role_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "NewVpnUserDTO":
        return cls(
            display_name=data.get("displayName", data.get("display_name", "")),
            email=data["email"],
            role_id=data.get("roleId", data.get("role_id", "")),
        )
