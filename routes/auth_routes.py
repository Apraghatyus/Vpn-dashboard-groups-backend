"""Auth routes — login, me, change password."""

from flask import Blueprint, request, jsonify
from services.auth_service import auth_service, require_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username y password requeridos"}), 400

    result = auth_service.login(username, password)
    if not result:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token, user = result
    return jsonify({
        "token": token,
        "user": user.to_dict(),
    })


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    user = request.current_user  # type: ignore
    return jsonify(user.to_dict())


@auth_bp.route("/change-password", methods=["POST"])
@require_auth
def change_password():
    data = request.get_json(silent=True) or {}
    old_password = data.get("oldPassword", "")
    new_password = data.get("newPassword", "")

    if not old_password or not new_password:
        return jsonify({"error": "Contraseñas requeridas"}), 400

    if len(new_password) < 4:
        return jsonify({"error": "La nueva contraseña debe tener al menos 4 caracteres"}), 400

    user = request.current_user  # type: ignore
    success = auth_service.change_password(user.id, old_password, new_password)
    if not success:
        return jsonify({"error": "Contraseña actual incorrecta"}), 401

    return jsonify({"message": "Contraseña actualizada"})
