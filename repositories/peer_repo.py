from models.peer import Peer
from repositories.base import BaseRepository
from config import Config


class PeerRepository(BaseRepository[Peer]):
    def __init__(self):
        super().__init__(
            filepath=Config.PEERS_FILE,
            serializer=Peer.to_dict,
            deserializer=Peer.from_dict,
        )

    def get_by_role(self, role_id: str) -> list[Peer]:
        return [p for p in self.get_all() if p.role_id == role_id]

    def count_online(self) -> int:
        return sum(1 for p in self.get_all() if p.status == "online")


peer_repo = PeerRepository()
