from datetime import datetime

from app import db


class EmailClassification(db.Model):
    __tablename__ = "email_classification"

    id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    email_content = db.Column(db.Text, nullable=False)

    result = db.Column(db.String(20), nullable=False)

    confidence = db.Column(db.Numeric(5, 4), nullable=True)

    model_version = db.Column(db.String(50), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email_content,
            "result": self.result,
            "confidence": float(self.confidence) if self.confidence is not None else None,
            "modelVersion": self.model_version,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
