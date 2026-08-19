from datetime import datetime

from app import db


class ModelInformation(db.Model):
    __tablename__ = "model_information"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    model_name = db.Column(
        db.String(100),
        nullable=False
    )

    model_version = db.Column(
        db.String(50),
        nullable=False
    )

    accuracy = db.Column(
        db.Numeric(6, 5),
        nullable=True
    )

    precision_score = db.Column(
        db.Numeric(6, 5),
        nullable=True
    )

    recall_score = db.Column(
        db.Numeric(6, 5),
        nullable=True
    )

    f1_score = db.Column(
        db.Numeric(6, 5),
        nullable=True
    )

    trained_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )