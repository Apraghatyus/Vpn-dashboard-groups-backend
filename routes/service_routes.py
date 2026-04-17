"""Service routes — VPN service endpoints."""

from flask import Blueprint, request, jsonify
from services.service_service import service_service
from services.auth_service import require_auth
from models.service import Service

service_bp = Blueprint("services", __name__, url_prefix="/api/services")


@service_bp.route("", methods=["GET"])
@require_auth
def get_all():
    services = service_service.get_all()
    return jsonify([s.to_dict() for s in services])


@service_bp.route("", methods=["POST"])
@require_auth
def create():
    data = request.get_json(silent=True) or {}
    try:
        svc = Service.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400

    created = service_service.create(svc)
    return jsonify(created.to_dict()), 201
