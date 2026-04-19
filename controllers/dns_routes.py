"""DNS routes — CRUD for AdGuard Home DNS rewrites."""

from flask import Blueprint, request, jsonify
from services.dns_service import dns_service
from services.auth_service import require_auth
from models.dns_record import NewDnsRecordDTO

dns_bp = Blueprint("dns", __name__, url_prefix="/api/dns")


@dns_bp.route("", methods=["GET"])
@require_auth
def get_all():
    return jsonify([r.to_dict() for r in dns_service.get_all()])


@dns_bp.route("", methods=["POST"])
@require_auth
def create():
    data = request.get_json(silent=True) or {}
    try:
        dto = NewDnsRecordDTO.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400

    record, synced = dns_service.create(dto)
    return jsonify({**record.to_dict(), "adguardSynced": synced}), 201


@dns_bp.route("/<record_id>", methods=["GET"])
@require_auth
def get_one(record_id: str):
    record = dns_service.get_by_id(record_id)
    if not record:
        return jsonify({"error": "Registro no encontrado"}), 404
    return jsonify(record.to_dict())


@dns_bp.route("/<record_id>", methods=["PUT"])
@require_auth
def update(record_id: str):
    data = request.get_json(silent=True) or {}
    try:
        dto = NewDnsRecordDTO.from_dict(data)
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Datos inválidos: {e}"}), 400

    record, synced = dns_service.update(record_id, dto)
    if not record:
        return jsonify({"error": "Registro no encontrado"}), 404
    return jsonify({**record.to_dict(), "adguardSynced": synced})


@dns_bp.route("/<record_id>", methods=["DELETE"])
@require_auth
def delete(record_id: str):
    if not dns_service.delete(record_id):
        return jsonify({"error": "Registro no encontrado"}), 404
    return jsonify({"message": "Registro DNS eliminado"})


@dns_bp.route("/sync", methods=["POST"])
@require_auth
def sync():
    """Push all local records to AdGuard Home."""
    result = dns_service.sync_all_to_adguard()
    status = 200 if result.get("ok") else 207
    return jsonify(result), status


@dns_bp.route("/adguard/rewrites", methods=["GET"])
@require_auth
def adguard_rewrites():
    """Fetch live rewrites directly from AdGuard Home."""
    rewrites = dns_service.get_adguard_rewrites()
    if rewrites is None:
        return jsonify({"error": "No se pudo conectar a AdGuard Home"}), 503
    return jsonify(rewrites)
