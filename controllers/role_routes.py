"""Role routes — CRUD for VPN roles."""

from flask import Blueprint, request, jsonify
from services.role_service import role_service
from services.auth_service import require_auth
from models.role import NewRoleDTO

role_bp = Blueprint("roles", __name__, url_prefix="/api/roles")


@role_bp.route("", methods=["GET"])
@require_auth
def get_all():
    roles = role_service.get_all()
    return jsonify([r.to_dict() for r in roles])


@role_bp.route("", methods=["POST"])
@require_auth
def create():
    data = request.get_json(silent=True) or {}
    try:
        dto = NewRoleDTO.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400

    role = role_service.create(dto)
    return jsonify(role.to_dict()), 201


@role_bp.route("/<role_id>", methods=["GET"])
@require_auth
def get_one(role_id: str):
    role = role_service.get_by_id(role_id)
    if not role:
        return jsonify({"error": "Rol no encontrado"}), 404
    return jsonify(role.to_dict())


@role_bp.route("/<role_id>", methods=["PUT"])
@require_auth
def update(role_id: str):
    data = request.get_json(silent=True) or {}
    role = role_service.update(role_id, data)
    if not role:
        return jsonify({"error": "Rol no encontrado"}), 404
    return jsonify(role.to_dict())


@role_bp.route("/<role_id>", methods=["DELETE"])
@require_auth
def delete(role_id: str):
    success = role_service.remove(role_id)
    if not success:
        return jsonify({"error": "Rol no encontrado"}), 404
    return jsonify({"message": "Rol eliminado"})
