from datetime import datetime, timezone

from ..db import db


class ShelterStatus(db.Model):
    __tablename__ = "shelter_status"

    id = db.Column(db.Integer, primary_key=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"), nullable=False, index=True)
    available_beds = db.Column(db.Integer)
    medical_support_level = db.Column(db.String(50))
    food_water_status = db.Column(db.String(50))
    shelter_status = db.Column(db.String(50), nullable=False, default="operational")
    road_access_status = db.Column(db.String(50))
    notes = db.Column(db.Text)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    recorded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    shelter = db.relationship("Shelter", back_populates="status_entries", lazy="joined")
    updated_by_user = db.relationship("User", back_populates="managed_status_updates", lazy="joined")
