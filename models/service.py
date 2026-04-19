"""Service model — mirrors frontend IService."""

from dataclasses import dataclass

CATEGORY_COLORS = {
    "Media": "#f59e0b",
    "Gaming": "#3b82f6",
    "CRM": "#ef4444",
    "Infraestructura": "#a855f7",
    "Herramientas": "#14b8a6",
    "Red": "#ef4444",
}

@dataclass
class Service:
    id: str
    name: str
    endpoint: str
    category: str  # Media, Gaming, CRM, Infraestructura, Herramientas, Red
    url: str | None = None  # subdominio amigable ej. "jellyfin.home.local"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "endpoint": self.endpoint,
            "category": self.category,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Service":
        return cls(
            id=data["id"],
            name=data["name"],
            endpoint=data["endpoint"],
            category=data["category"],
            url=data.get("url"),
        )


@dataclass
class NewServiceDTO:
    name: str
    endpoint: str
    category: str
    url: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "NewServiceDTO":
        return cls(
            name=data["name"],
            endpoint=data["endpoint"],
            category=data["category"],
            url=data.get("url"),
        )
