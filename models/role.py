"""Role model — mirrors frontend IRole / NewRoleDTO."""

from dataclasses import dataclass, field
import time


@dataclass
class Role:
    id: str
    display_name: str
    description: str
    color: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "displayName": self.display_name,
            "description": self.description,
            "color": self.color,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Role":
        return cls(
            id=data["id"],
            display_name=data.get("displayName", data.get("display_name", "")),
            description=data.get("description", ""),
            color=data.get("color", "#a8a29e"),
            created_at=data.get("createdAt", data.get("created_at", time.time())),
        )


@dataclass
class NewRoleDTO:
    id: str
    display_name: str
    description: str
    color: str

    @classmethod
    def from_dict(cls, data: dict) -> "NewRoleDTO":
        return cls(
            id=data["id"],
            display_name=data.get("displayName", data.get("display_name", "")),
            description=data.get("description", ""),
            color=data.get("color", "#a8a29e"),
        )
