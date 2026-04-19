"""Database engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

_SessionFactory: sessionmaker | None = None


def init_db(database_url: str) -> None:
    """Initialize engine, create all tables, set up session factory."""
    from db.tables import Base

    global _SessionFactory
    engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=3600)
    Base.metadata.create_all(engine)
    _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Session:
    if _SessionFactory is None:
        raise RuntimeError("DB not initialized — call init_db() first")
    return _SessionFactory()
