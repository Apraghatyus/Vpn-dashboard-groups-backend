from models.vpn_user import VpnUser
from repositories.base import BaseRepository
from db.tables import VpnUserRow


class VpnUserRepository(BaseRepository[VpnUser]):
    _Row = VpnUserRow

    def _to_model(self, row: VpnUserRow) -> VpnUser:
        return VpnUser(
            id=row.id,
            display_name=row.display_name,
            email=row.email,
            role_id=row.role_id,
            created_at=row.created_at,
        )

    def _to_row(self, item: VpnUser) -> VpnUserRow:
        return VpnUserRow(
            id=item.id,
            display_name=item.display_name,
            email=item.email,
            role_id=item.role_id,
            created_at=item.created_at,
        )

    def get_by_email(self, email: str) -> VpnUser | None:
        with self._session() as s:
            row = s.query(VpnUserRow).filter_by(email=email).first()
            return self._to_model(row) if row else None

    def get_by_role(self, role_id: str) -> list[VpnUser]:
        with self._session() as s:
            rows = s.query(VpnUserRow).filter_by(role_id=role_id).all()
            return [self._to_model(r) for r in rows]


vpn_user_repo = VpnUserRepository()
