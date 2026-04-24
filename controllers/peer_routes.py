"""Peer routes — CRUD for VPN peers."""

from flask import Blueprint, request, jsonify, Response
from services.peer_service import peer_service
from services.access_service import access_service
from services.auth_service import require_auth
from services.wg_easy_client import WgEasyError
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
    # Ignorar IP si el frontend la manda — ya no es input válido
    data.pop("ip", None)
    # NewPeerDTO.from_dict exige 'username' e 'ip'. Inyectamos placeholder
    # para que pase la validación — el service lo sobrescribe con la IP real.
    data.setdefault("ip", "0.0.0.0")
    try:
        dto = NewPeerDTO.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400
    if not dto.username:
        return jsonify({"error": "username requerido"}), 400
    if not dto.role_id:
        return jsonify({"error": "roleId requerido"}), 400

    try:
        peer = peer_service.create(dto)
    except WgEasyError as e:
        return jsonify(e.to_dict()), 502
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Unexpected error creating peer")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500
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


@peer_bp.route("/<peer_id>/config", methods=["GET"])
@require_auth
def download_config(peer_id: str):
    peer = peer_service.get_by_id(peer_id)
    if not peer:
        return jsonify({"error": "Peer no encontrado"}), 404
    if not peer.wg_easy_id:
        return jsonify({
            "error": "peer_not_linked",
            "message": (
                "Este peer fue creado antes de la integración con WG-Easy "
                "y no tiene claves reales. Ejecutá reconcile-wg-easy o "
                "recreá el peer para obtener un .conf funcional."
            ),
        }), 409
    try:
        content = peer_service.generate_config(peer_id)
    except WgEasyError as e:
        return jsonify(e.to_dict()), 502
    if content is None:
        return jsonify({"error": "no se pudo generar config"}), 500
    filename = f"{peer.username}.conf"
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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
    try:
        success = peer_service.remove(peer_id)
    except WgEasyError as e:
        return jsonify(e.to_dict()), 502
    if not success:
        return jsonify({"error": "Peer no encontrado"}), 404
    return jsonify({"message": "Peer eliminado"})

@peer_bp.route("/reconcile-wg-easy", methods=["POST"])
@require_auth
def reconcile():
    """
    Reconcilia la DB local con el estado real de WG-Easy.
    Útil para adoptar peers creados directo en la UI de WG-Easy,
    detectar huérfanos, y sanear IPs desactualizadas.
    """
    try:
        result = peer_service.reconcile_with_wg_easy()
    except WgEasyError as e:
        return jsonify(e.to_dict()), 502
    return jsonify(result), 200
