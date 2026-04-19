from models.peer import Peer
from repositories.base import BaseRepository
from db.tables import PeerRow


class PeerRepository(BaseRepository[Peer]):
    _Row = PeerRow

    def _to_model(self, row: PeerRow) -> Peer:
        return Peer(
            id=row.id,
            display_name=row.display_name,
            username=row.username,
            ip=row.ip,
            role_id=row.role_id,
            status=row.status,
            last_seen=row.last_seen,
            created_at=row.created_at,
            user_id=row.user_id,
            device_name=row.device_name,
        )

    def _to_row(self, item: Peer) -> PeerRow:
        return PeerRow(
            id=item.id,
            display_name=item.display_name,
            username=item.username,
            ip=item.ip,
            role_id=item.role_id,
            status=item.status,
            last_seen=item.last_seen,
            created_at=item.created_at,
            user_id=item.user_id,
            device_name=item.device_name,
        )

    def get_by_role(self, role_id: str) -> list[Peer]:
        with self._session() as s:
            rows = s.query(PeerRow).filter_by(role_id=role_id).all()
            return [self._to_model(r) for r in rows]

    def get_by_user(self, user_id: str) -> list[Peer]:
        with self._session() as s:
            rows = s.query(PeerRow).filter_by(user_id=user_id).all()
            return [self._to_model(r) for r in rows]

    def count_online(self) -> int:
        with self._session() as s:
            return s.query(PeerRow).filter_by(status="online").count()


peer_repo = PeerRepository()
