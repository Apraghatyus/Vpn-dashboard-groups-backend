from .auth_routes import auth_bp
from .peer_routes import peer_bp
from .role_routes import role_bp
from .service_routes import service_bp
from .access_routes import access_bp
from .yaml_routes import yaml_bp
from .dns_routes import dns_bp
from .vpn_user_routes import vpn_user_bp

ALL_BLUEPRINTS = [
    auth_bp,
    peer_bp,
    role_bp,
    service_bp,
    access_bp,
    yaml_bp,
    dns_bp,
    vpn_user_bp,
]

__all__ = ["ALL_BLUEPRINTS"]
