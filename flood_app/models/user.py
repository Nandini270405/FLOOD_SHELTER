from datetime import datetime, timezone

from ..db import db


USER_ROLES = ("admin", "shelter_manager", "citizen", "response_officer")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="citizen", index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    managed_status_updates = db.relationship("ShelterStatus", back_populates="updated_by_user", lazy="select")
    recommendation_logs = db.relationship("RecommendationLog", back_populates="user", lazy="select")
    created_alerts = db.relationship("Alert", back_populates="created_by_user", lazy="select")
    actor_audit_logs = db.relationship(
        "AuditLog",
        back_populates="actor_user",
        lazy="select",
        foreign_keys="AuditLog.actor_user_id",
    )
