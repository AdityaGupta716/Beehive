import os
import json
import requests
import jwt
from functools import wraps
from flask import request, jsonify
from jwt import PyJWKClient

CLERK_ISSUER = os.getenv("CLERK_ISSUER")

if not CLERK_ISSUER:
    raise RuntimeError("CLERK_ISSUER environment variable is not set")

JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"
jwks_client = PyJWKClient(JWKS_URL)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # print("Authenticating request...")

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid authorization format"}), 401

        token = auth_header.split(" ", 1)[1]
        # print("ISS FROM TOKEN:", jwt.decode(token, options={"verify_signature": False})["iss"])
        # print("ISS FROM ENV  :", CLERK_ISSUER)

        try:
            # print( "Fetching signing key...")
            signing_key = jwks_client.get_signing_key_from_jwt(token).key
            # print(signing_key)

            decoded = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=None,
                issuer=CLERK_ISSUER,
                options={
                    "verify_exp": True,
                    "verify_signature": True,
                },
            )

            user_id = decoded.get("sub")
            if not user_id:
                return jsonify({"error": "Invalid token payload"}), 401

            role = decoded.get("role", "user")

            request.current_user = {
                "id": user_id,
                "role": role,
            }

            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        except Exception:
            return jsonify({"error": "Authentication failed"}), 401

    return decorated_function
