"""DnsRecord model — DNS rewrite entry for AdGuard Home."""

from dataclasses import dataclass, field
import time


@dataclass
class DnsRecord:
    id: str
    domain: str       # e.g. "jellyfin.home.local"
    answer: str       # IP for A records, hostname for CNAME
    type: str         # "A" | "CNAME"
    description: str = ""
    service_id: str = ""   # optional FK to Service
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "answer": self.answer,
            "type": self.type,
            "description": self.description,
            "serviceId": self.service_id,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DnsRecord":
        return cls(
            id=data["id"],
            domain=data["domain"],
            answer=data["answer"],
            type=data.get("type", "A"),
            description=data.get("description", ""),
            service_id=data.get("serviceId", data.get("service_id", "")),
            created_at=data.get("createdAt", data.get("created_at", time.time())),
        )


@dataclass
class NewDnsRecordDTO:
    domain: str
    answer: str
    type: str = "A"
    description: str = ""
    service_id: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "NewDnsRecordDTO":
        return cls(
            domain=data["domain"],
            answer=data["answer"],
            type=data.get("type", "A"),
            description=data.get("description", ""),
            service_id=data.get("serviceId", data.get("service_id", "")),
        )
