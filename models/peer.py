"""Peer model — mirrors frontend IPeer / NewPeerDTO."""

from dataclasses import dataclass, field
import time


@dataclass
class Peer:
    id: str
    display_name: str
    username: str
    ip: str
    role_id: str
    status: str = "offline"          # 'online' | 'offline'
    last_seen: str = "ahora"
    created_at: float = field(default_factory=time.time)
    user_id: str = ""                # FK to VpnUser (owner of this device)
    device_name: str = ""            # e.g. "MacBook Pro", "iPhone 15"

    def to_dict(self) -> dict:
        """Serialize to camelCase dict for API response."""
        return {
            "id": self.id,
            "displayName": self.display_name,
            "username": self.username,
            "ip": self.ip,
            "roleId": self.role_id,
            "status": self.status,
            "lastSeen": self.last_seen,
            "createdAt": self.created_at,
            "userId": self.user_id,
            "deviceName": self.device_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Peer":
        """Deserialize from camelCase dict."""
        return cls(
            id=data["id"],
            display_name=data.get("displayName", data.get("display_name", "")),
            username=data["username"],
            ip=data["ip"],
            role_id=data.get("roleId", data.get("role_id", "")),
            status=data.get("status", "offline"),
            last_seen=data.get("lastSeen", data.get("last_seen", "ahora")),
            created_at=data.get("createdAt", data.get("created_at", time.time())),
            user_id=data.get("userId", data.get("user_id", "")),
            device_name=data.get("deviceName", data.get("device_name", "")),
        )


@dataclass
class NewPeerDTO:
    display_name: str
    username: str
    ip: str
    role_id: str
    user_id: str = ""
    device_name: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "NewPeerDTO":
        return cls(
            display_name=data.get("displayName", data.get("display_name", "")),
            username=data["username"],
            ip=data["ip"],
            role_id=data.get("roleId", data.get("role_id", "")),
            user_id=data.get("userId", data.get("user_id", "")),
            device_name=data.get("deviceName", data.get("device_name", "")),
        )
