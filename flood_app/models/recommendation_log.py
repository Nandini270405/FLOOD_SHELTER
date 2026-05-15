from datetime import datetime, timezone

from ..db import db


class RecommendationLog(db.Model):
    __tablename__ = "recommendation_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    num_people = db.Column(db.Integer, nullable=False)
    distance_level = db.Column(db.String(50), nullable=False)
    accessibility_required = db.Column(db.String(50), nullable=False)
    elevation_input = db.Column(db.String(50), nullable=False)
    proximity_input = db.Column(db.String(50), nullable=False)
    medical_input = db.Column(db.String(50), nullable=False)
    top_shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"), index=True)
    result_count = db.Column(db.Integer, nullable=False, default=0)
    request_context = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="recommendation_logs", lazy="joined")
    top_shelter = db.relationship("Shelter", back_populates="recommendation_logs", lazy="joined")
