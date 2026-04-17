"""YAML routes — generate and download WireGuard ACL config."""

from flask import Blueprint, Response, jsonify
from services.yaml_service import yaml_service
from services.auth_service import require_auth

yaml_bp = Blueprint("yaml", __name__, url_prefix="/api/yaml")


@yaml_bp.route("", methods=["GET"])
@require_auth
def generate():
    content = yaml_service.generate()
    return jsonify({"yaml": content})


@yaml_bp.route("/download", methods=["GET"])
@require_auth
def download():
    content = yaml_service.save_to_file()
    return Response(
        content,
        mimetype="text/yaml",
        headers={"Content-Disposition": "attachment; filename=wg-acl.yaml"},
    )
