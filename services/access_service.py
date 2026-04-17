"""Access service — business logic for the role×service permission matrix."""

from models.access import AccessEntry
from repositories.access_repo import access_repo
from repositories.service_repo import service_repo


class AccessService:
    def get_matrix(self) -> list[AccessEntry]:
        return access_repo.get_all()

    def has_access(self, role_id: str, service_id: str) -> bool:
        return access_repo.has_access(role_id, service_id)

    def toggle(self, role_id: str, service_id: str) -> list[AccessEntry]:
        return access_repo.toggle(role_id, service_id)

    def get_for_role(self, role_id: str) -> list[AccessEntry]:
        return access_repo.get_for_role(role_id)

    def get_rule_count(self, role_id: str) -> int:
        return len(access_repo.get_for_role(role_id))

    def get_rule_count_display(self, role_id: str) -> str:
        count = self.get_rule_count(role_id)
        total = service_repo.count()
        if count == total:
            return "∞ reglas"
        return f"{count} reglas"


access_service = AccessService()
