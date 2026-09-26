from datetime import datetime

from flask import Blueprint, jsonify, request

from app import db
from app.models.email_classification import EmailClassification
from app.models.email_dataset import EmailDataset
from app.utils.errors import not_found_error, validation_error
from app.auth import login_required

classifications_bp = Blueprint(
    "classifications",
    __name__,
    url_prefix="/api/classifications",
)


@classifications_bp.post("/<int:classification_id>/feedback")
@login_required()
def submit_feedback(classification_id):
    record = db.session.get(EmailClassification, classification_id)
    if record is None:
        return not_found_error("Classification not found.")

    data = request.get_json(silent=True) or {}
    label = data.get("label")
    label = label.strip().upper() if isinstance(label, str) else ""
    if label not in ("SPAM", "NOT_SPAM"):
        return validation_error("Label must be SPAM or NOT_SPAM.")

    examples = EmailDataset.query.filter_by(email_content=record.email_content).all()
    if not examples:
        example = EmailDataset(email_content=record.email_content, label=label)
        db.session.add(example)
        action = "added"
    else:
        example = examples[0]
        action = "unchanged" if all(item.label == label for item in examples) else "updated"
        for item in examples:
            if item.label != label:
                item.label = label
                item.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({
        "message": "Feedback saved to the training dataset.",
        "action": action,
        "dataset": example.to_dict(),
    }), 200


@classifications_bp.get("")
@login_required()
def list_classifications():
    records = (
        EmailClassification.query
        .order_by(EmailClassification.created_at.desc())
        .all()
    )

    return jsonify({
        "data": [record.to_dict() for record in records],
    }), 200


@classifications_bp.get("/<int:classification_id>")
@login_required()
def get_classification(classification_id):
    record = db.session.get(EmailClassification, classification_id)

    if record is None:
        return not_found_error("Classification not found.")

    return jsonify(record.to_dict()), 200


@classifications_bp.delete("/<int:classification_id>")
@login_required()
def delete_classification(classification_id):
    record = db.session.get(EmailClassification, classification_id)

    if record is None:
        return not_found_error("Classification not found.")

    db.session.delete(record)
    db.session.commit()

    return jsonify({
        "message": "Classification deleted successfully.",
    }), 200
