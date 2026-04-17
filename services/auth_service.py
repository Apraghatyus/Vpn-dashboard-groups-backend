"""Auth service — JWT token management and password hashing."""

import time
from functools import wraps

import bcrypt
import jwt
from flask import request, jsonify

from config import Config
from models.user import User
from repositories.user_repo import user_repo


class AuthService:
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def generate_token(self, user: User) -> str:
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "iat": int(time.time()),
            "exp": int(time.time()) + Config.JWT_EXPIRY_HOURS * 3600,
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def login(self, username: str, password: str) -> tuple[str, User] | None:
        """Returns (token, user) on success, None on failure."""
        user = user_repo.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        token = self.generate_token(user)
        return token, user

    def get_current_user(self) -> User | None:
        """Extract user from the Authorization header."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header[7:]
        payload = self.decode_token(token)
        if not payload:
            return None
        return user_repo.get_by_id(payload["sub"])

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        user = user_repo.get_by_id(user_id)
        if not user:
            return False
        if not self.verify_password(old_password, user.password_hash):
            return False
        user.password_hash = self.hash_password(new_password)
        user_repo.update(user_id, user)
        return True


auth_service = AuthService()


def require_auth(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = auth_service.get_current_user()
        if not user:
            return jsonify({"error": "No autorizado"}), 401
        request.current_user = user  # type: ignore
        return f(*args, **kwargs)
    return decorated
