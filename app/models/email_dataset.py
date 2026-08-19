from datetime import datetime

from app import db


class EmailDataset(db.Model):
    __tablename__ = "email_dataset"

    id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    email_content = db.Column(
        db.Text,
        nullable=False
    )

    label = db.Column(
        db.String(20),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email_content,
            "label": self.label,
            "createdAt": self.created_at.isoformat()
            if self.created_at else None,
            "updatedAt": self.updated_at.isoformat()
            if self.updated_at else None
        }