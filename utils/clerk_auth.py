import os
import json
from functools import wraps
from flask import request, jsonify

# JWT verification
try:
    import jwt
    from jwt import PyJWKClient
except ImportError:
    jwt = None
    PyJWKClient = None

def _verify_jwt(token: str):
    """Verify JWT using JWKS from the configured issuer and return claims.

    Requires environment variable CLERK_ISSUER (e.g., https://your-clerk-domain)."""
    issuer = os.getenv('CLERK_ISSUER')
    if not issuer:
        raise RuntimeError('Missing CLERK_ISSUER environment variable')

    if jwt is None or PyJWKClient is None:
        raise RuntimeError('PyJWT is not installed; cannot verify tokens')

    jwks_url = issuer.rstrip('/') + '/.well-known/jwks.json'

    jwk_client = PyJWKClient(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    # Clerk tokens typically use RS256 and include `iss`
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "RS512"],
        issuer=issuer,
        options={
            # Frontend tokens may not include audience we control; skip aud verification
            'verify_aud': False
        }
    )
    return claims

def require_auth(f):
    """Decorator to enforce authentication via verified JWT (Clerk)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401

        # Remove 'Bearer ' prefix if present
        token = auth_header[7:] if auth_header.startswith('Bearer ') else auth_header

        try:
            claims = _verify_jwt(token)

            user_id = claims.get('sub') or claims.get('userid')
            if not user_id:
                return jsonify({'error': 'Invalid token: missing subject'}), 401

            # Prefer Clerk public metadata role if present
            role = (
                (claims.get('public_metadata') or {}).get('role')
                or claims.get('role')
                or 'user'
            )

            request.current_user = {
                'id': user_id,
                'role': role,
                'claims': claims,
            }

            return f(*args, **kwargs)

        except Exception as e:
            # Avoid leaking verification details, return generic auth error
            return jsonify({'error': 'Invalid or unverifiable token'}), 401

    return decorated_function
