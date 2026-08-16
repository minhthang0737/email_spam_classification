from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({
        "status": "UP",
        "service": "Email Spam Classification API"
    })
