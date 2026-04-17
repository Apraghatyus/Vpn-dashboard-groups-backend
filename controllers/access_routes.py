"""Access matrix routes — get and toggle permissions."""

from flask import Blueprint, request, jsonify
from services.access_service import access_service
from services.auth_service import require_auth

access_bp = Blueprint("access", __name__, url_prefix="/api/access")


@access_bp.route("", methods=["GET"])
@require_auth
def get_matrix():
    matrix = access_service.get_matrix()
    return jsonify([e.to_dict() for e in matrix])


@access_bp.route("/toggle", methods=["POST"])
@require_auth
def toggle():
    data = request.get_json(silent=True) or {}
    role_id = data.get("roleId", "")
    service_id = data.get("serviceId", "")

    if not role_id or not service_id:
        return jsonify({"error": "roleId y serviceId requeridos"}), 400

    updated = access_service.toggle(role_id, service_id)
    return jsonify([e.to_dict() for e in updated])
