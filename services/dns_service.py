"""
DNS service — local CRUD + AdGuard Home sync.

AdGuard Home API:
  GET  /control/rewrite/list          → list all rewrites
  POST /control/rewrite/add           → {"domain": "...", "answer": "..."}
  POST /control/rewrite/delete        → {"domain": "...", "answer": "..."}
"""

import time
import requests
from requests.auth import HTTPBasicAuth

from config import Config
from models.dns_record import DnsRecord, NewDnsRecordDTO
from repositories.dns_repo import dns_repo


class DnsService:
    def _adguard_auth(self):
        if Config.ADGUARD_USER and Config.ADGUARD_PASS:
            return HTTPBasicAuth(Config.ADGUARD_USER, Config.ADGUARD_PASS)
        return None

    def _adguard_url(self, path: str) -> str:
        return f"{Config.ADGUARD_URL.rstrip('/')}/control/{path.lstrip('/')}"

    def _push_to_adguard(self, domain: str, answer: str) -> bool:
        """Add a DNS rewrite to AdGuard Home."""
        if not Config.ADGUARD_URL:
            return False
        try:
            r = requests.post(
                self._adguard_url("rewrite/add"),
                json={"domain": domain, "answer": answer},
                auth=self._adguard_auth(),
                timeout=5,
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

    def _delete_from_adguard(self, domain: str, answer: str) -> bool:
        """Remove a DNS rewrite from AdGuard Home."""
        if not Config.ADGUARD_URL:
            return False
        try:
            r = requests.post(
                self._adguard_url("rewrite/delete"),
                json={"domain": domain, "answer": answer},
                auth=self._adguard_auth(),
                timeout=5,
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

    def get_all(self) -> list[DnsRecord]:
        return dns_repo.get_all()

    def get_by_id(self, record_id: str) -> DnsRecord | None:
        return dns_repo.get_by_id(record_id)

    def create(self, dto: NewDnsRecordDTO) -> tuple[DnsRecord, bool]:
        """Create a DNS record locally and sync to AdGuard. Returns (record, synced)."""
        record = DnsRecord(
            id=f"dns-{int(time.time() * 1000)}",
            domain=dto.domain,
            answer=dto.answer,
            type=dto.type,
            description=dto.description,
            service_id=dto.service_id,
        )
        dns_repo.add(record)
        synced = self._push_to_adguard(record.domain, record.answer)
        return record, synced

    def update(self, record_id: str, dto: NewDnsRecordDTO) -> tuple[DnsRecord | None, bool]:
        """Update a record: remove old entry from AdGuard, add new one."""
        existing = dns_repo.get_by_id(record_id)
        if not existing:
            return None, False

        # Remove old AdGuard entry
        self._delete_from_adguard(existing.domain, existing.answer)

        updated = DnsRecord(
            id=record_id,
            domain=dto.domain,
            answer=dto.answer,
            type=dto.type,
            description=dto.description,
            service_id=dto.service_id,
            created_at=existing.created_at,
        )
        dns_repo.update(record_id, updated)
        synced = self._push_to_adguard(updated.domain, updated.answer)
        return updated, synced

    def delete(self, record_id: str) -> bool:
        record = dns_repo.get_by_id(record_id)
        if not record:
            return False
        self._delete_from_adguard(record.domain, record.answer)
        return dns_repo.delete(record_id)

    def sync_all_to_adguard(self) -> dict:
        """Push all local DNS records to AdGuard Home."""
        if not Config.ADGUARD_URL:
            return {"ok": False, "reason": "ADGUARD_URL no configurado"}

        records = dns_repo.get_all()
        success, failed = 0, 0
        for rec in records:
            if self._push_to_adguard(rec.domain, rec.answer):
                success += 1
            else:
                failed += 1
        return {"ok": failed == 0, "synced": success, "failed": failed, "total": len(records)}

    def get_adguard_rewrites(self) -> list[dict] | None:
        """Fetch current rewrites directly from AdGuard Home."""
        if not Config.ADGUARD_URL:
            return None
        try:
            r = requests.get(
                self._adguard_url("rewrite/list"),
                auth=self._adguard_auth(),
                timeout=5,
            )
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        return None


dns_service = DnsService()
