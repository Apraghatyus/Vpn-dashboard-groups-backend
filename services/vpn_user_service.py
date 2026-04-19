"""VpnUser service — business logic for user management."""

import time

from models.vpn_user import VpnUser, NewVpnUserDTO
from repositories.vpn_user_repo import vpn_user_repo
from repositories.peer_repo import peer_repo


class VpnUserService:
    def get_all(self) -> list[VpnUser]:
        return vpn_user_repo.get_all()

    def get_by_id(self, user_id: str) -> VpnUser | None:
        return vpn_user_repo.get_by_id(user_id)

    def get_by_email(self, email: str) -> VpnUser | None:
        return vpn_user_repo.get_by_email(email)

    def get_with_devices(self, user_id: str) -> dict | None:
        user = vpn_user_repo.get_by_id(user_id)
        if not user:
            return None
        devices = peer_repo.get_by_user(user_id)
        return {**user.to_dict(), "devices": [d.to_dict() for d in devices]}

    def create(self, dto: NewVpnUserDTO) -> VpnUser | None:
        if vpn_user_repo.get_by_email(dto.email):
            return None  # email already taken
        user = VpnUser(
            id=f"vpnuser-{int(time.time() * 1000)}",
            display_name=dto.display_name,
            email=dto.email,
            role_id=dto.role_id,
        )
        return vpn_user_repo.add(user)

    def update(self, user_id: str, dto: NewVpnUserDTO) -> VpnUser | None:
        existing = vpn_user_repo.get_by_id(user_id)
        if not existing:
            return None
        # If email changed, check it's not already taken by another user
        if dto.email != existing.email and vpn_user_repo.get_by_email(dto.email):
            return None
        updated = VpnUser(
            id=user_id,
            display_name=dto.display_name,
            email=dto.email,
            role_id=dto.role_id,
            created_at=existing.created_at,
        )
        return vpn_user_repo.update(user_id, updated)

    def delete(self, user_id: str) -> bool:
        return vpn_user_repo.delete(user_id)


vpn_user_service = VpnUserService()
