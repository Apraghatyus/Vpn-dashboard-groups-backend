"""
Seed data — initializes JSON files with mock data on first run.
Same data as the frontend mockData.ts for consistency.
"""

import time
from pathlib import Path

from models import Peer, Role, Service, AccessEntry, User
from repositories.peer_repo import peer_repo
from repositories.role_repo import role_repo
from repositories.service_repo import service_repo
from repositories.access_repo import access_repo
from repositories.user_repo import user_repo
from services.auth_service import auth_service
from config import Config


def seed_all():
    """Seed all data files if they don't exist yet."""
    _seed_roles()
    _seed_peers()
    _seed_services()
    _seed_access_matrix()
    _seed_admin_user()
    print("✓ Seed completo")


def _seed_roles():
    if role_repo.exists():
        return
    now = time.time()
    roles = [
        Role(id="admin", display_name="admin", description="Acceso total a toda la infraestructura", color="#ef4444", created_at=now - 86400 * 30),
        Role(id="familia", display_name="familia", description="Media, archivos y DNS", color="#3b82f6", created_at=now - 86400 * 25),
        Role(id="gaming", display_name="gaming", description="Servidores de juegos", color="#f59e0b", created_at=now - 86400 * 20),
        Role(id="cliente_aguaquim", display_name="cliente_aguaquim", description="Solo acceso al CRM corporativo", color="#14b8a6", created_at=now - 86400 * 10),
    ]
    role_repo.replace_all(roles)
    print("  → Roles seeded")


def _seed_peers():
    if peer_repo.exists():
        return
    now = time.time()
    peers = [
        Peer(id="peer-1", display_name="Juan Camilo · Owner", username="apraghato", ip="10.8.0.2", role_id="admin", status="online", last_seen="ahora", created_at=now - 86400 * 30),
        Peer(id="peer-2", display_name="Camila · iPhone", username="camila_phone", ip="10.8.0.3", role_id="familia", status="online", last_seen="2 min", created_at=now - 86400 * 25),
        Peer(id="peer-3", display_name="Papá · Smart TV", username="papa_tv", ip="10.8.0.4", role_id="familia", status="offline", last_seen="3h", created_at=now - 86400 * 20),
        Peer(id="peer-4", display_name="Santi · Gaming rig", username="santi_pc", ip="10.8.0.5", role_id="gaming", status="online", last_seen="ahora", created_at=now - 86400 * 15),
        Peer(id="peer-5", display_name="Operador 1 · Aguaquim", username="aguaquim_op1", ip="10.8.0.6", role_id="cliente_aguaquim", status="offline", last_seen="1d", created_at=now - 86400 * 5),
    ]
    peer_repo.replace_all(peers)
    print("  → Peers seeded")


def _seed_services():
    if service_repo.exists():
        return
    services = [
        Service(id="jellyfin", name="Jellyfin", endpoint="100.75.203.14:8096", category="Media"),
        Service(id="navidrome", name="Navidrome", endpoint="100.75.203.14:4533", category="Media"),
        Service(id="filebrowser", name="FileBrowser", endpoint="100.75.203.14:8080", category="Herramientas"),
        Service(id="kavita", name="Kavita", endpoint="100.75.203.14:5000", category="Media"),
        Service(id="minecraft-java", name="Minecraft Java", endpoint="100.75.203.14:25565", category="Gaming"),
        Service(id="mc-bedrock", name="MC Bedrock", endpoint="100.75.203.14:19132", category="Gaming"),
        Service(id="terraria", name="Terraria", endpoint="100.75.203.14:7777", category="Gaming"),
        Service(id="aguaquim-crm", name="Aguaquim CRM", endpoint="100.75.203.14:5433", category="CRM"),
        Service(id="portainer", name="Portainer", endpoint="100.75.203.14:9443", category="Infraestructura"),
        Service(id="dns-pihole", name="DNS (Pi-hole)", endpoint="100.114.140.34:53", category="Red"),
    ]
    service_repo.replace_all(services)
    print("  → Services seeded")


def _seed_access_matrix():
    if access_repo.exists():
        return
    services = service_repo.get_all()
    entries: list[AccessEntry] = []

    # admin → everything
    for s in services:
        entries.append(AccessEntry(role_id="admin", service_id=s.id))

    # familia
    for sid in ["jellyfin", "navidrome", "filebrowser", "kavita", "dns-pihole", "minecraft-java"]:
        entries.append(AccessEntry(role_id="familia", service_id=sid))

    # gaming
    for sid in ["minecraft-java", "mc-bedrock", "terraria", "jellyfin"]:
        entries.append(AccessEntry(role_id="gaming", service_id=sid))

    # cliente_aguaquim
    for sid in ["aguaquim-crm", "portainer"]:
        entries.append(AccessEntry(role_id="cliente_aguaquim", service_id=sid))

    access_repo.replace_all(entries)
    print("  → Access matrix seeded")


def _seed_admin_user():
    if user_repo.exists():
        return
    admin = User(
        id="user-admin",
        username=Config.DEFAULT_ADMIN_USER,
        password_hash=auth_service.hash_password(Config.DEFAULT_ADMIN_PASS),
        display_name="Administrador",
        role="admin",
        created_at=time.time(),
    )
    user_repo.replace_all([admin])
    print(f"  → Admin user seeded ({Config.DEFAULT_ADMIN_USER}/{Config.DEFAULT_ADMIN_PASS})")
