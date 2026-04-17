"""User model for authentication."""

from dataclasses import dataclass, field
import time


@dataclass
class User:
    id: str
    username: str
    password_hash: str
    display_name: str = ""
    role: str = "admin"  # future: 'admin' | 'viewer'
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Serialize — NEVER includes password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name,
            "role": self.role,
            "createdAt": self.created_at,
        }

    def to_storage_dict(self) -> dict:
        """Serialize for storage — includes password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "passwordHash": self.password_hash,
            "displayName": self.display_name,
            "role": self.role,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            username=data["username"],
            password_hash=data.get("passwordHash", data.get("password_hash", "")),
            display_name=data.get("displayName", data.get("display_name", "")),
            role=data.get("role", "admin"),
            created_at=data.get("createdAt", data.get("created_at", time.time())),
        )
