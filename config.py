"""
WG-ACL Manager — Configuration
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)


class Config:
    """Application configuration."""

    # Data file paths
    DATA_DIR = str(DATA_DIR)
    PEERS_FILE = str(DATA_DIR / "peers.json")
    ROLES_FILE = str(DATA_DIR / "roles.json")
    SERVICES_FILE = str(DATA_DIR / "services.json")
    ACCESS_FILE = str(DATA_DIR / "access_matrix.json")
    USERS_FILE = str(DATA_DIR / "users.json")
    YAML_OUTPUT = str(DATA_DIR / "roles.yaml")

    # JWT
    SECRET_KEY = os.environ.get("SECRET_KEY", "wg-acl-change-me-in-production")
    JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Default admin credentials (only used for initial seed)
    DEFAULT_ADMIN_USER = os.environ.get("DEFAULT_ADMIN_USER", "admin")
    DEFAULT_ADMIN_PASS = os.environ.get("DEFAULT_ADMIN_PASS", "admin")
