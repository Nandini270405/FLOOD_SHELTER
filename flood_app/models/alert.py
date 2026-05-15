from datetime import datetime, timezone

from ..db import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), nullable=False, default="info", index=True)
    channel = db.Column(db.String(50), nullable=False, default="in_app")
    status = db.Column(db.String(50), nullable=False, default="pending", index=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"), index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    sent_at = db.Column(db.DateTime(timezone=True))

    shelter = db.relationship("Shelter", back_populates="alerts", lazy="joined")
    created_by_user = db.relationship("User", back_populates="created_alerts", lazy="joined")
