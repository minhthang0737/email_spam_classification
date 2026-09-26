from datetime import datetime

from app import db


class BlockedIP(db.Model):
    __tablename__ = "blocked_ip"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(45), unique=True, nullable=False, index=True)
    reason = db.Column(db.String(300), nullable=False, default="Được quản trị viên đánh dấu")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "ip": self.address, "reason": self.reason,
                "createdAt": self.created_at.isoformat()}


class BlockedDomain(db.Model):
    __tablename__ = "blocked_domain"

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(253), unique=True, nullable=False, index=True)
    reason = db.Column(db.String(300), nullable=False, default="Được quản trị viên đánh dấu")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "domain": self.domain, "reason": self.reason,
                "createdAt": self.created_at.isoformat()}
