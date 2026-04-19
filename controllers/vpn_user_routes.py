"""VPN User routes — manage users and their associated devices."""

from flask import Blueprint, request, jsonify
from services.vpn_user_service import vpn_user_service
from services.auth_service import require_auth
from models.vpn_user import NewVpnUserDTO

vpn_user_bp = Blueprint("vpn_users", __name__, url_prefix="/api/vpn-users")


@vpn_user_bp.route("", methods=["GET"])
@require_auth
def get_all():
    return jsonify([u.to_dict() for u in vpn_user_service.get_all()])


@vpn_user_bp.route("", methods=["POST"])
@require_auth
def create():
    data = request.get_json(silent=True) or {}
    try:
        dto = NewVpnUserDTO.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400

    user = vpn_user_service.create(dto)
    if not user:
        return jsonify({"error": "El correo ya está registrado"}), 409
    return jsonify(user.to_dict()), 201


@vpn_user_bp.route("/<user_id>", methods=["GET"])
@require_auth
def get_one(user_id: str):
    """Returns user with their devices embedded."""
    result = vpn_user_service.get_with_devices(user_id)
    if not result:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(result)


@vpn_user_bp.route("/<user_id>", methods=["PUT"])
@require_auth
def update(user_id: str):
    data = request.get_json(silent=True) or {}
    user, error = vpn_user_service.update(user_id, data)
    if error == "not_found":
        return jsonify({"error": "Usuario no encontrado"}), 404
    if error == "conflict":
        return jsonify({"error": "El correo ya está en uso"}), 409
    return jsonify(user.to_dict())


@vpn_user_bp.route("/<user_id>", methods=["DELETE"])
@require_auth
def delete(user_id: str):
    cascade = request.args.get("cascade", "false").lower() == "true"
    if not vpn_user_service.delete(user_id, cascade=cascade):
        return jsonify({"error": "Usuario no encontrado"}), 404
    return "", 204


@vpn_user_bp.route("/<user_id>/devices", methods=["GET"])
@require_auth
def get_devices(user_id: str):
    """List all VPN devices (peers) belonging to this user."""
    result = vpn_user_service.get_with_devices(user_id)
    if not result:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(result.get("devices", []))
