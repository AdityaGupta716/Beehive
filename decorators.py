from functools import wraps
from flask import jsonify, request, session

# Shared decorators to prevent circular imports

def login_is_required(function):
    @wraps(function)
    def login_wrapper(*args, **kwargs):
        if "google_id" not in session:
            return "Unauthorized", 401
        else:
            return function(*args, **kwargs)
    return login_wrapper


def require_admin_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(request, "current_user", None)

        if not user:
            return jsonify({"error": "Authentication required"}), 401

        if user.get("role") != "admin":
            return jsonify({"error": "Forbidden: admin role required"}), 403

        return f(*args, **kwargs)

    return decorated_function
