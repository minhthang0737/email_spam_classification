from flask import Blueprint, jsonify, request

from app import db
from app.ml.predictor import ActiveModelNotFoundError
from app.models.email_classification import EmailClassification
from app.services.prediction_service import classify_and_save
from app.utils.errors import not_found_error, validation_error

predict_bp = Blueprint("predict", __name__, url_prefix="/api")


@predict_bp.post("/predict")
def predict():
    data = request.get_json(silent=True)

    if not data:
        return validation_error("Request body cannot be empty.")

    email_content = data.get("email")

    if not email_content or not str(email_content).strip():
        return validation_error("Email content cannot be empty.")

    try:
        classification = classify_and_save(str(email_content))
    except ActiveModelNotFoundError:
        return not_found_error("Active model not found.")

    return jsonify({
        "id": classification.id,
        "result": classification.result,
        "confidence": float(classification.confidence)
        if classification.confidence is not None else None,
        "modelVersion": classification.model_version,
    }), 200
