"""Peer service — business logic for peer management."""

import time
from models.peer import Peer, NewPeerDTO
from repositories.peer_repo import peer_repo
from config import Config


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
            user_id=dto.user_id,
            device_name=dto.device_name,
        )
        return peer_repo.add(peer)

    def update(self, peer_id: str, data: dict) -> Peer | None:
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return None
        field_map = {
            "displayName": "display_name",
            "username": "username",
            "ip": "ip",
            "roleId": "role_id",
            "deviceName": "device_name",
        }
        for camel, snake in field_map.items():
            if camel in data:
                setattr(peer, snake, data[camel])
        if "userId" in data:
            peer.user_id = data["userId"] or ""
        return peer_repo.update(peer_id, peer)

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

    def generate_config(self, peer_id: str) -> str | None:
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return None

        subnet_prefix = Config.WG_SUBNET.split("/")[1]

        lines = [
            f"# WireGuard config — {peer.display_name}",
            "",
            "[Interface]",
            f"PrivateKey = <PEGAR_CLAVE_PRIVADA_DEL_DISPOSITIVO>",
            f"Address = {peer.ip}/{subnet_prefix}",
            f"DNS = {Config.WG_DNS}",
            "",
            "[Peer]",
            f"PublicKey = {Config.WG_SERVER_PUBLIC_KEY or '<CLAVE_PUBLICA_DEL_SERVIDOR>'}",
            f"Endpoint = {Config.WG_SERVER_ENDPOINT or '<IP_PUBLICA_DEL_SERVIDOR>'}:{Config.WG_PORT}",
            f"AllowedIPs = {Config.WG_SUBNET}",
            "PersistentKeepalive = 25",
        ]
        return "\n".join(lines)


peer_service = PeerService()
