from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta, timezone
import random
import bcrypt

from database.databaseConfig import db
from database.userdatahandler import create_user, get_user_by_username
from utils.roles import is_admin_email
from utils.jwt_auth import create_access_token
from database.databaseConfig import beehive

auth_bp = Blueprint("auth", __name__)

# HELPER: CREATE EMAIL OTP
def create_email_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))

    # Remove old OTPs
    db.email_otps.delete_many({"email": email})
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    db.email_otps.insert_one({
        "email": email,
        "otp": otp,
        "expires_at": expires_at
        })

    return otp


# REQUEST OTP (SIGNUP)
@auth_bp.route("/request-otp", methods=["POST"])
def request_otp():
    data = request.get_json(force=True)
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    otp = create_email_otp(email)

    # Try to send the OTP via email if mail is configured
    try:
        mail_username = current_app.config.get("MAIL_USERNAME")
        mail_server = current_app.config.get("MAIL_SERVER")
        if mail_username and mail_server:
            # Import here to avoid circular imports at module import time
            from flask_mail import Message
            from app import mail

            subject = "Your Beehive OTP"
            body = f"Your Beehive verification code is: {otp}\nIt will expire in 5 minutes."
            msg = Message(subject=subject, recipients=[email], body=body, sender=mail_username)
            mail.send(msg)
            return jsonify({"message": "OTP sent"}), 200
        else:
            # Mail not configured — fall back to printing for dev
            current_app.logger.info("MAIL not configured, printing OTP to console")
            print("EMAIL OTP:", otp)
            return jsonify({"message": "OTP stored (mail not configured)"}), 200
    except Exception as e:
        current_app.logger.exception("Failed to send OTP email: %s", e)
        # Still return success to avoid leaking whether email exists; but inform admin in logs
        return jsonify({"message": "OTP stored (failed to send email)"}), 200


from datetime import datetime, timezone

@auth_bp.route("/verify-otp", methods=["POST"], strict_slashes=False)
def verify_otp():
    try:
        data = request.get_json(force=True)

        email = data.get("email")
        otp = data.get("otp")

        if not email or not otp:
            return jsonify({"error": "Email and OTP required"}), 400

        record = db.email_otps.find_one({
            "email": email,
            "otp": {"$in": [otp, str(otp), int(otp)]}
        })

        if not record:
            return jsonify({"error": "Invalid OTP"}), 400

        expires_at = record["expires_at"]

        # 🔑 FIX: normalize datetime
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            return jsonify({"error": "OTP expired"}), 400

        return jsonify({"message": "OTP verified"}), 200

    except Exception as e:
        print("VERIFY OTP ERROR:", e)
        return jsonify({"error": "Server error"}), 500


@auth_bp.route("/complete-signup", methods=["POST"])
def complete_signup():
    data = request.get_json(force=True)

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Prevent duplicate username
    if db.users.find_one({"username": username}):
        return jsonify({"error": "Username already taken"}), 400

    role = "admin" if is_admin_email(email) else "user"

    hashed_password = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    )

    result = db.users.insert_one({
        "email": email,
        "username": username,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    })

    token = create_access_token(
        user_id=str(result.inserted_id),
        role=role
    )

    # Cleanup OTPs
    db.email_otps.delete_many({"email": email})

    return jsonify({
        "access_token": token,
        "role": role
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    identifier = data.get("username")  # username OR email
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "Username/email and password required"}), 400

    user = beehive.users.find_one({
        "$or": [
            {"username": identifier},
            {"email": identifier}
        ]
    })

    if not user:
        return jsonify({"error": "User not found"}), 401

    stored_password = user.get("password")
    if not stored_password:
        return jsonify({"error": "Password not set"}), 400

    if not bcrypt.checkpw(password.encode(), stored_password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        user_id=str(user["_id"]),
        role=user.get("role", "user")
    )

    return jsonify({"access_token": token}), 200


@auth_bp.route("/set-password", methods=["POST"])
def set_password():
    data = request.get_json(force=True)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    role = "admin" if is_admin_email(email) else "user"

    user_id = db.users.insert_one({
        "email": email,
        "username": email.split("@")[0],
        "password": hashed,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }).inserted_id

    token = create_access_token(
        user_id=str(user_id),
        role=role
    )

    db.email_otps.delete_many({"email": email})

    return jsonify({
        "access_token": token,
        "role": role
    }), 201

# GOOGLE OAUTH (JWT ONLY)
@auth_bp.route("/google", methods=["POST"])
def google_auth():
    data = request.get_json(force=True)

    email = data.get("email")
    name = data.get("name")

    if not email:
        return jsonify({"error": "Email required"}), 400

    user = db.users.find_one({"email": email})

    if not user:
        role = "admin" if is_admin_email(email) else "user"

        user_id = create_user(
            username=name or email.split("@")[0],
            email=email,
            password=None,
            role=role,
            provider="google"
        )
    else:
        user_id = str(user["_id"])
        role = user.get("role", "user")

    token = create_access_token(user_id=user_id, role=role)

    return jsonify({
        "access_token": token,
        "role": role
    }), 200
