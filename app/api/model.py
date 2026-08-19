from flask import Blueprint, jsonify

from app.models.model_information import ModelInformation


model_bp = Blueprint(
    "model",
    __name__,
    url_prefix="/api/model"
)


@model_bp.route("", methods=["GET"])
def get_model_information():

    model = (
        ModelInformation.query
        .filter_by(is_active=True)
        .first()
    )

    if not model:
        return jsonify({
            "message": "Active model not found"
        }), 404

    return jsonify({
        "model": model.model_name,
        "version": model.model_version,
        "accuracy": float(model.accuracy) if model.accuracy is not None else None,
        "precision": float(model.precision_score)
            if model.precision_score is not None else None,
        "recall": float(model.recall_score)
            if model.recall_score is not None else None,
        "f1Score": float(model.f1_score)
            if model.f1_score is not None else None,
        "trainedAt": model.trained_at.isoformat(),
        "isActive": model.is_active
    }), 200