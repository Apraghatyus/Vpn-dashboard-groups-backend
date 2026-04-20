from flask import Blueprint, jsonify
from services.wg_easy_client import wg_easy, WgEasyError

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    checks = {"backend": "ok"}
    status = 200
    try:
        wg_easy.list_clients()
        checks["wg_easy"] = "ok"
    except WgEasyError as e:
        checks["wg_easy"] = f"fail: {e}"
        status = 503
    return jsonify(checks), status
