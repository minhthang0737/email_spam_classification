from datetime import datetime

from flask import Blueprint, jsonify, request

from app import db
from app.models.email_dataset import EmailDataset
from app.utils.logger import get_logger

logger = get_logger(__name__)

dataset_bp = Blueprint(
    "dataset",
    __name__,
    url_prefix="/api/dataset"
)


@dataset_bp.get("")
def get_dataset():
    logger.info("Prediction completed")
    datasets = (
        EmailDataset.query
        .order_by(EmailDataset.id.desc())
        .all()
    )

    return jsonify({
        "data": [
            dataset.to_dict()
            for dataset in datasets
        ]
    }), 200


@dataset_bp.post("")
def create_dataset():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body cannot be empty."
        }), 400

    email_content = data.get("email")
    label = data.get("label")

    if not email_content or not email_content.strip():
        return jsonify({
            "message": "Email content cannot be empty."
        }), 400

    if not label:
        return jsonify({
            "message": "Label cannot be empty."
        }), 400

    label = label.strip().upper()

    if label not in ("SPAM", "NOT_SPAM"):
        return jsonify({
            "message": "Label must be SPAM or NOT_SPAM."
        }), 400

    dataset = EmailDataset(
        email_content=email_content.strip(),
        label=label
    )

    db.session.add(dataset)
    db.session.commit()

    return jsonify(dataset.to_dict()), 201


@dataset_bp.put("/<int:dataset_id>")
def update_dataset(dataset_id):
    dataset = db.session.get(
        EmailDataset,
        dataset_id
    )

    if dataset is None:
        return jsonify({
            "message": "Dataset not found."
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body cannot be empty."
        }), 400

    if "email" in data:
        email_content = data.get("email")

        if not email_content or not email_content.strip():
            return jsonify({
                "message": "Email content cannot be empty."
            }), 400

        dataset.email_content = email_content.strip()

    if "label" in data:
        label = data.get("label")

        if not label:
            return jsonify({
                "message": "Label cannot be empty."
            }), 400

        label = label.strip().upper()

        if label not in ("SPAM", "NOT_SPAM"):
            return jsonify({
                "message": "Label must be SPAM or NOT_SPAM."
            }), 400

        dataset.label = label

    dataset.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(dataset.to_dict()), 200


@dataset_bp.delete("/<int:dataset_id>")
def delete_dataset(dataset_id):
    dataset = db.session.get(
        EmailDataset,
        dataset_id
    )

    if dataset is None:
        return jsonify({
            "message": "Dataset not found."
        }), 404

    db.session.delete(dataset)
    db.session.commit()

    return jsonify({
        "message": "Dataset deleted successfully."
    }), 200