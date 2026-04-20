"""SQLAlchemy ORM table definitions — internal to the repository layer."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Text, PrimaryKeyConstraint


class Base(DeclarativeBase):
    pass


class PeerRow(Base):
    __tablename__ = "peers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(256))
    username: Mapped[str] = mapped_column(String(128), unique=True)
    ip: Mapped[str] = mapped_column(String(45))
    role_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))
    last_seen: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[float] = mapped_column(Float)
    user_id: Mapped[str] = mapped_column(String(64))
    device_name: Mapped[str] = mapped_column(String(256))
    wg_easy_id = Column(String(128), nullable=True, unique=True, index=True)

class RoleRow(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[float] = mapped_column(Float)


class ServiceRow(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    endpoint: Mapped[str] = mapped_column(String(256))
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    category: Mapped[str] = mapped_column(String(64))


class AccessEntryRow(Base):
    __tablename__ = "access_matrix"
    __table_args__ = (PrimaryKeyConstraint("role_id", "service_id"),)

    role_id: Mapped[str] = mapped_column(String(64))
    service_id: Mapped[str] = mapped_column(String(64))


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[float] = mapped_column(Float)


class VpnUserRow(Base):
    __tablename__ = "vpn_users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256), unique=True)
    role_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[float] = mapped_column(Float)


class DnsRecordRow(Base):
    __tablename__ = "dns_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    domain: Mapped[str] = mapped_column(String(256))
    answer: Mapped[str] = mapped_column(String(256))
    type: Mapped[str] = mapped_column(String(8))
    description: Mapped[str] = mapped_column(Text)
    service_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[float] = mapped_column(Float)
