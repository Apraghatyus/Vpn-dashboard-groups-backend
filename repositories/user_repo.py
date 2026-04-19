from models.user import User
from repositories.base import BaseRepository
from db.tables import UserRow


class UserRepository(BaseRepository[User]):
    _Row = UserRow

    def _to_model(self, row: UserRow) -> User:
        return User(
            id=row.id,
            username=row.username,
            password_hash=row.password_hash,
            display_name=row.display_name,
            role=row.role,
            created_at=row.created_at,
        )

    def _to_row(self, item: User) -> UserRow:
        return UserRow(
            id=item.id,
            username=item.username,
            password_hash=item.password_hash,
            display_name=item.display_name,
            role=item.role,
            created_at=item.created_at,
        )

    def get_by_username(self, username: str) -> User | None:
        with self._session() as s:
            row = s.query(UserRow).filter_by(username=username).first()
            return self._to_model(row) if row else None


user_repo = UserRepository()
