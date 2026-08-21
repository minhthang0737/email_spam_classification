from flask import Blueprint, jsonify

from app.models.email_dataset import EmailDataset
from app.ml.trainer import train_model
from app.models.model_information import ModelInformation
from app.services.model_service import save_model_information
from app.utils.errors import conflict_error, not_found_error, validation_error

model_bp = Blueprint(
    "model",
    __name__,
    url_prefix="/api/model",
)


@model_bp.route("", methods=["GET"])
def get_model_information():
    model = ModelInformation.query.filter_by(is_active=True).first()

    if not model:
        return not_found_error("Active model not found.")

    return jsonify({
        "model": model.model_name,
        "version": model.model_version,
        "accuracy": float(model.accuracy) if model.accuracy is not None else None,
        "precision": float(model.precision_score)
        if model.precision_score is not None else None,
        "recall": float(model.recall_score)
        if model.recall_score is not None else None,
        "f1Score": float(model.f1_score) if model.f1_score is not None else None,
        "trainedAt": model.trained_at.isoformat(),
        "isActive": model.is_active,
    }), 200


@model_bp.route("/train", methods=["POST"])
def train_model_endpoint():
    dataset = EmailDataset.query.all()

    if len(dataset) < 2:
        return validation_error("Dataset must contain at least 2 records.")

    labels = {record.label for record in dataset if record.label in ("SPAM", "NOT_SPAM")}
    if len(labels) < 2:
        return conflict_error("Dataset must contain both SPAM and NOT_SPAM labels.")

    try:
        result = train_model(dataset)
    except ValueError as exc:
        return validation_error(str(exc))

    save_model_information(
        model_name=result["model_name"],
        model_version=result["model_version"],
        accuracy=result["accuracy"],
        precision_score=result["precision"],
        recall_score=result["recall"],
        f1_score=result["f1_score"],
    )

    return jsonify({
        "message": "Model trained successfully",
        "model": result["model_name"],
        "version": result["model_version"],
        "accuracy": result["accuracy"],
        "precision": result["precision"],
        "recall": result["recall"],
        "f1Score": result["f1_score"],
        "confusionMatrix": result["confusion_matrix"],
    }), 200
