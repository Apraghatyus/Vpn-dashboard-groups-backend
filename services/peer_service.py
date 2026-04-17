"""Peer service — business logic for peer management."""

import time
from models.peer import Peer, NewPeerDTO
from repositories.peer_repo import peer_repo


class PeerService:
    def get_all(self) -> list[Peer]:
        return peer_repo.get_all()

    def get_by_id(self, peer_id: str) -> Peer | None:
        return peer_repo.get_by_id(peer_id)

    def create(self, dto: NewPeerDTO) -> Peer:
        peer = Peer(
            id=f"peer-{int(time.time() * 1000)}",
            display_name=dto.display_name,
            username=dto.username,
            ip=dto.ip,
            role_id=dto.role_id,
            status="offline",
            last_seen="ahora",
            created_at=time.time(),
        )
        return peer_repo.add(peer)

    def update_role(self, peer_id: str, role_id: str) -> Peer | None:
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return None
        peer.role_id = role_id
        return peer_repo.update(peer_id, peer)

    def remove(self, peer_id: str) -> bool:
        return peer_repo.delete(peer_id)

    def get_by_role(self, role_id: str) -> list[Peer]:
        return peer_repo.get_by_role(role_id)

    def count_online(self) -> int:
        return peer_repo.count_online()

    def count(self) -> int:
        return peer_repo.count()


peer_service = PeerService()
