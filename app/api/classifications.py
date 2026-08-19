from flask import Blueprint, jsonify

from app import db
from app.models.email_classification import EmailClassification
from app.utils.errors import not_found_error

classifications_bp = Blueprint(
    "classifications",
    __name__,
    url_prefix="/api/classifications",
)


@classifications_bp.get("")
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
def get_classification(classification_id):
    record = db.session.get(EmailClassification, classification_id)

    if record is None:
        return not_found_error("Classification not found.")

    return jsonify(record.to_dict()), 200


@classifications_bp.delete("/<int:classification_id>")
def delete_classification(classification_id):
    record = db.session.get(EmailClassification, classification_id)

    if record is None:
        return not_found_error("Classification not found.")

    db.session.delete(record)
    db.session.commit()

    return jsonify({
        "message": "Classification deleted successfully.",
    }), 200
