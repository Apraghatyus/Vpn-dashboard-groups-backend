"""Peer routes — CRUD for VPN peers."""

from flask import Blueprint, request, jsonify
from services.peer_service import peer_service
from services.access_service import access_service
from services.auth_service import require_auth
from models.peer import NewPeerDTO

peer_bp = Blueprint("peers", __name__, url_prefix="/api/peers")


@peer_bp.route("", methods=["GET"])
@require_auth
def get_all():
    peers = peer_service.get_all()
    return jsonify([p.to_dict() for p in peers])


@peer_bp.route("", methods=["POST"])
@require_auth
def create():
    data = request.get_json(silent=True) or {}
    try:
        dto = NewPeerDTO.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400

    peer = peer_service.create(dto)
    return jsonify(peer.to_dict()), 201


@peer_bp.route("/<peer_id>", methods=["GET"])
@require_auth
def get_one(peer_id: str):
    peer = peer_service.get_by_id(peer_id)
    if not peer:
        return jsonify({"error": "Peer no encontrado"}), 404
    return jsonify(peer.to_dict())


@peer_bp.route("/<peer_id>/role", methods=["PUT"])
@require_auth
def update_role(peer_id: str):
    data = request.get_json(silent=True) or {}
    role_id = data.get("roleId", "")
    if not role_id:
        return jsonify({"error": "roleId requerido"}), 400

    peer = peer_service.update_role(peer_id, role_id)
    if not peer:
        return jsonify({"error": "Peer no encontrado"}), 404
    return jsonify(peer.to_dict())


@peer_bp.route("/<peer_id>", methods=["PUT"])
@require_auth
def update(peer_id: str):
    data = request.get_json(silent=True) or {}
    peer = peer_service.update(peer_id, data)
    if not peer:
        return jsonify({"error": "Peer no encontrado"}), 404
    return jsonify(peer.to_dict())


@peer_bp.route("/<peer_id>", methods=["DELETE"])
@require_auth
def delete(peer_id: str):
    success = peer_service.remove(peer_id)
    if not success:
        return jsonify({"error": "Peer no encontrado"}), 404
    return jsonify({"message": "Peer eliminado"})
