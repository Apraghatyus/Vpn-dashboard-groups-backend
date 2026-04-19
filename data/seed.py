"""
Seed data — initializes JSON files with mock data on first run.
Same data as the frontend mockData.ts for consistency.
"""

import time
from pathlib import Path

from models import Peer, Role, Service, AccessEntry, User, VpnUser, DnsRecord
from repositories.peer_repo import peer_repo
from repositories.role_repo import role_repo
from repositories.service_repo import service_repo
from repositories.access_repo import access_repo
from repositories.user_repo import user_repo
from repositories.vpn_user_repo import vpn_user_repo
from repositories.dns_repo import dns_repo
from services.auth_service import auth_service
from config import Config


def seed_all():
    """Seed all data files if they don't exist yet."""
    _seed_roles()
    _seed_vpn_users()
    _seed_peers()
    _seed_services()
    _seed_access_matrix()
    _seed_admin_user()
    _seed_dns_records()
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


def _seed_vpn_users():
    if vpn_user_repo.exists():
        return
    now = time.time()
    users = [
        VpnUser(id="vpnuser-1", display_name="Juan Camilo Cardona", email="cardonarealpe@gmail.com", role_id="admin", created_at=now - 86400 * 30),
        VpnUser(id="vpnuser-2", display_name="Camila", email="camila@home.local", role_id="familia", created_at=now - 86400 * 25),
        VpnUser(id="vpnuser-3", display_name="Papá", email="papa@home.local", role_id="familia", created_at=now - 86400 * 20),
        VpnUser(id="vpnuser-4", display_name="Santi", email="santi@home.local", role_id="gaming", created_at=now - 86400 * 15),
        VpnUser(id="vpnuser-5", display_name="Operador Aguaquim", email="operador@aguaquim.com", role_id="cliente_aguaquim", created_at=now - 86400 * 5),
    ]
    vpn_user_repo.replace_all(users)
    print("  → VPN users seeded")


def _seed_peers():
    if peer_repo.exists():
        return
    now = time.time()
    peers = [
        Peer(id="peer-1", display_name="Juan Camilo · MacBook Pro", username="apraghato_mac", ip="10.8.0.2", role_id="admin", status="online", last_seen="ahora", created_at=now - 86400 * 30, user_id="vpnuser-1", device_name="MacBook Pro"),
        Peer(id="peer-2", display_name="Juan Camilo · iPhone", username="apraghato_iphone", ip="10.8.0.3", role_id="admin", status="offline", last_seen="1h", created_at=now - 86400 * 28, user_id="vpnuser-1", device_name="iPhone 15 Pro"),
        Peer(id="peer-3", display_name="Camila · iPhone", username="camila_phone", ip="10.8.0.4", role_id="familia", status="online", last_seen="2 min", created_at=now - 86400 * 25, user_id="vpnuser-2", device_name="iPhone 14"),
        Peer(id="peer-4", display_name="Camila · iPad", username="camila_ipad", ip="10.8.0.5", role_id="familia", status="offline", last_seen="5h", created_at=now - 86400 * 24, user_id="vpnuser-2", device_name="iPad Air"),
        Peer(id="peer-5", display_name="Papá · Smart TV", username="papa_tv", ip="10.8.0.6", role_id="familia", status="offline", last_seen="3h", created_at=now - 86400 * 20, user_id="vpnuser-3", device_name="Smart TV"),
        Peer(id="peer-6", display_name="Santi · Gaming rig", username="santi_pc", ip="10.8.0.7", role_id="gaming", status="online", last_seen="ahora", created_at=now - 86400 * 15, user_id="vpnuser-4", device_name="Gaming PC"),
        Peer(id="peer-7", display_name="Operador 1 · Aguaquim", username="aguaquim_op1", ip="10.8.0.8", role_id="cliente_aguaquim", status="offline", last_seen="1d", created_at=now - 86400 * 5, user_id="vpnuser-5", device_name="Laptop Oficina"),
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


def _seed_dns_records():
    if dns_repo.exists():
        return
    records = [
        DnsRecord(id="dns-1", domain="jellyfin.home.local", answer="100.75.203.14", type="A", description="Servidor de media Jellyfin", service_id="jellyfin"),
        DnsRecord(id="dns-2", domain="navidrome.home.local", answer="100.75.203.14", type="A", description="Servidor de música Navidrome", service_id="navidrome"),
        DnsRecord(id="dns-3", domain="kavita.home.local", answer="100.75.203.14", type="A", description="Biblioteca de libros Kavita", service_id="kavita"),
        DnsRecord(id="dns-4", domain="files.home.local", answer="100.75.203.14", type="A", description="FileBrowser — gestión de archivos", service_id="filebrowser"),
        DnsRecord(id="dns-5", domain="portainer.home.local", answer="100.75.203.14", type="A", description="Portainer — gestión de contenedores", service_id="portainer"),
        DnsRecord(id="dns-6", domain="crm.home.local", answer="100.75.203.14", type="A", description="Aguaquim CRM", service_id="aguaquim-crm"),
        DnsRecord(id="dns-7", domain="dns.home.local", answer="100.114.140.34", type="A", description="AdGuard Home — DNS", service_id=""),
        DnsRecord(id="dns-8", domain="*.home.local", answer="100.75.203.14", type="A", description="Wildcard — fallback para *.home.local", service_id=""),
    ]
    dns_repo.replace_all(records)
    print("  → DNS records seeded")
