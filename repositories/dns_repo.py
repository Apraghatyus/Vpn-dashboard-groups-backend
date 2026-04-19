from models.dns_record import DnsRecord
from repositories.base import BaseRepository
from db.tables import DnsRecordRow


class DnsRepository(BaseRepository[DnsRecord]):
    _Row = DnsRecordRow

    def _to_model(self, row: DnsRecordRow) -> DnsRecord:
        return DnsRecord(
            id=row.id,
            domain=row.domain,
            answer=row.answer,
            type=row.type,
            description=row.description,
            service_id=row.service_id,
            created_at=row.created_at,
        )

    def _to_row(self, item: DnsRecord) -> DnsRecordRow:
        return DnsRecordRow(
            id=item.id,
            domain=item.domain,
            answer=item.answer,
            type=item.type,
            description=item.description,
            service_id=item.service_id,
            created_at=item.created_at,
        )

    def get_by_domain(self, domain: str) -> DnsRecord | None:
        with self._session() as s:
            row = s.query(DnsRecordRow).filter_by(domain=domain).first()
            return self._to_model(row) if row else None

    def get_by_service(self, service_id: str) -> list[DnsRecord]:
        with self._session() as s:
            rows = s.query(DnsRecordRow).filter_by(service_id=service_id).all()
            return [self._to_model(r) for r in rows]


dns_repo = DnsRepository()
