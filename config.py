"""
WG-ACL Manager — Configuration
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)


class Config:
    """Application configuration."""

    # YAML output (still file-based — bind-mounted to host for WireGuard)
    DATA_DIR = str(DATA_DIR)
    YAML_OUTPUT = os.path.join(DATA_DIR, "roles.yaml")
    ACL_OUTPUT = os.environ.get("ACL_OUTPUT", YAML_OUTPUT)

    # MariaDB
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "wgacl")
    DB_USER = os.environ.get("DB_USER", "wgacl")
    DB_PASS = os.environ.get("DB_PASS", "wgacl")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

    # JWT
    SECRET_KEY = os.environ.get("SECRET_KEY", "wg-acl-change-me-in-production")
    JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Default admin credentials (only used for initial seed)
    DEFAULT_ADMIN_USER = os.environ.get("DEFAULT_ADMIN_USER", "admin")
    DEFAULT_ADMIN_PASS = os.environ.get("DEFAULT_ADMIN_PASS", "admin")

    # AdGuard Home integration
    ADGUARD_URL = os.environ.get("ADGUARD_URL", "")
    ADGUARD_USER = os.environ.get("ADGUARD_USER", "")
    ADGUARD_PASS = os.environ.get("ADGUARD_PASS", "")

    # WireGuard server
    WG_SERVER_PUBLIC_KEY = os.environ.get("WG_SERVER_PUBLIC_KEY", "")
    WG_SERVER_ENDPOINT   = os.environ.get("WG_SERVER_ENDPOINT", "")
    WG_PORT              = os.environ.get("WG_PORT", "51820")
    WG_SUBNET            = os.environ.get("WG_SUBNET", "10.8.0.0/24")
    WG_DNS               = os.environ.get("WG_DNS", "10.8.0.1")
