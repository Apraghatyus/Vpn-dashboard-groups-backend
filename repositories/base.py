"""
Base repository — SQLAlchemy session-based persistence.

Services and controllers remain completely unchanged.
To add a new entity: subclass BaseRepository, define _Row, _to_model, _to_row.
"""

from contextlib import contextmanager
from typing import TypeVar, Generic
from db import get_session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    _Row = None  # SQLAlchemy ORM class — set by each subclass

    def _to_model(self, row) -> T:
        raise NotImplementedError

    def _to_row(self, item: T):
        raise NotImplementedError

    @contextmanager
    def _session(self):
        session = get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_all(self) -> list[T]:
        with self._session() as s:
            return [self._to_model(r) for r in s.query(self._Row).all()]

    def get_by_id(self, item_id: str, id_field: str = "id") -> T | None:
        with self._session() as s:
            row = s.get(self._Row, item_id)
            return self._to_model(row) if row else None

    def add(self, item: T) -> T:
        with self._session() as s:
            s.add(self._to_row(item))
        return item

    def update(self, item_id: str, item: T, id_field: str = "id") -> T | None:
        with self._session() as s:
            row = s.get(self._Row, item_id)
            if not row:
                return None
            new_row = self._to_row(item)
            for col in self._Row.__table__.columns.keys():
                setattr(row, col, getattr(new_row, col))
        return item

    def delete(self, item_id: str, id_field: str = "id") -> bool:
        with self._session() as s:
            row = s.get(self._Row, item_id)
            if not row:
                return False
            s.delete(row)
        return True

    def replace_all(self, items: list[T]) -> None:
        with self._session() as s:
            s.query(self._Row).delete()
            for item in items:
                s.add(self._to_row(item))

    def count(self) -> int:
        with self._session() as s:
            return s.query(self._Row).count()

    def exists(self) -> bool:
        return self.count() > 0
