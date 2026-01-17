from functools import wraps
from flask import jsonify
from utils.jwt_auth import verify_jwt


def require_admin_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from flask import request

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        token = auth_header.replace("Bearer ", "")

        try:
            claims = verify_jwt(token)
        except ValueError:
            return jsonify({"error": "Invalid or expired token"}), 401

        if claims.get("role") != "admin":
            return jsonify({"error": "Admin role required"}), 403

        request.current_user = {
            "id": claims["sub"],
            "role": claims["role"],
        }

        return f(*args, **kwargs)

    return wrapper
