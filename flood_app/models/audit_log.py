from datetime import datetime, timezone

from ..db import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"), index=True)
    entity_type = db.Column(db.String(100), nullable=False, index=True)
    entity_id = db.Column(db.String(100), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    before_state = db.Column(db.JSON)
    after_state = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    actor_user = db.relationship(
        "User",
        back_populates="actor_audit_logs",
        lazy="joined",
        foreign_keys=[actor_user_id],
    )
    shelter = db.relationship("Shelter", back_populates="audit_logs", lazy="joined")
