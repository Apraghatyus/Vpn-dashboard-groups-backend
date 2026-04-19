"""Role service — business logic for role management."""

import time
from models.role import Role, NewRoleDTO
from repositories.role_repo import role_repo
from repositories.access_repo import access_repo
from repositories.peer_repo import peer_repo


class RoleService:
    def get_all(self) -> list[Role]:
        return role_repo.get_all()

    def get_by_id(self, role_id: str) -> Role | None:
        return role_repo.get_by_id(role_id)

    def create(self, dto: NewRoleDTO) -> Role:
        role = Role(
            id=dto.id,
            display_name=dto.display_name,
            description=dto.description,
            color=dto.color,
            created_at=time.time(),
        )
        return role_repo.add(role)

    def update(self, role_id: str, data: dict) -> Role | None:
        existing = role_repo.get_by_id(role_id)
        if not existing:
            return None
        updated = Role(
            id=role_id,
            display_name=data.get("displayName", existing.display_name),
            description=data.get("description", existing.description),
            color=data.get("color", existing.color),
            created_at=existing.created_at,
        )
        return role_repo.update(role_id, updated)

    def remove(self, role_id: str) -> bool:
        # Also clean up access entries for this role
        access_repo.remove_role(role_id)
        # Reassign peers with this role to the first available role
        roles = role_repo.get_all()
        fallback_id = next((r.id for r in roles if r.id != role_id), "")
        for peer in peer_repo.get_by_role(role_id):
            peer.role_id = fallback_id
            peer_repo.update(peer.id, peer)
        return role_repo.delete(role_id)

    def get_color(self, role_id: str) -> str:
        role = role_repo.get_by_id(role_id)
        return role.color if role else "#a8a29e"

    def count(self) -> int:
        return role_repo.count()


role_service = RoleService()
