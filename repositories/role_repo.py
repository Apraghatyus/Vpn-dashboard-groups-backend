from models.role import Role
from repositories.base import BaseRepository
from db.tables import RoleRow


class RoleRepository(BaseRepository[Role]):
    _Row = RoleRow

    def _to_model(self, row: RoleRow) -> Role:
        return Role(
            id=row.id,
            display_name=row.display_name,
            description=row.description,
            color=row.color,
            created_at=row.created_at,
        )

    def _to_row(self, item: Role) -> RoleRow:
        return RoleRow(
            id=item.id,
            display_name=item.display_name,
            description=item.description,
            color=item.color,
            created_at=item.created_at,
        )


role_repo = RoleRepository()
