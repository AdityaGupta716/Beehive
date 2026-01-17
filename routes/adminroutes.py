from flask import Blueprint, request, jsonify
from decorators import require_admin_role
from database.userdatahandler import (
    _get_paginated_images_by_user,
    get_recent_uploads,
    get_upload_stats,
    get_upload_analytics
)
from utils.logger import Logger

logger = Logger.get_logger("adminroutes")

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# -----------------------------
# Admin: Get user uploads
# -----------------------------
@admin_bp.route("/user_uploads/<user_id>")
@require_admin_role
def admin_user_images_show(user_id):
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 12))

        page = max(1, page)
        page_size = min(max(1, page_size), 50)

        result = _get_paginated_images_by_user(user_id, page, page_size)
        return jsonify(result), 200

    except Exception:
        logger.error("Error fetching user uploads", exc_info=True)
        return jsonify({"error": "Failed to fetch user uploads"}), 500


# -----------------------------
# Admin: Dashboard
# -----------------------------
@admin_bp.route("/dashboard", methods=["GET"])
@require_admin_role
def get_dashboard_data():
    try:
        limit = int(request.args.get("limit", 10))

        stats = get_upload_stats()
        recent_uploads = get_recent_uploads(limit)

        return jsonify({
            "stats": stats,
            "recentUploads": recent_uploads
        }), 200

    except Exception:
        logger.error("Error fetching dashboard data", exc_info=True)
        return jsonify({"error": "Failed to fetch dashboard data"}), 500


# -----------------------------
# Admin: Analytics (Uploads only)
# -----------------------------
@admin_bp.route("/analytics", methods=["GET"])
@require_admin_role
def get_all_analytics():
    try:
        days_ago = int(request.args.get("days", 7))

        upload_data = get_upload_analytics(trend_days=days_ago)

        if not upload_data:
            return jsonify({"error": "Failed to retrieve analytics data"}), 500

        return jsonify({
            "uploads": upload_data
        }), 200

    except Exception:
        logger.error("Error fetching analytics", exc_info=True)
        return jsonify({"error": "Failed to fetch analytics data"}), 500
