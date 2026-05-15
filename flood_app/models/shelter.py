from dataclasses import dataclass

from ..db import db


@dataclass
class ShelterRecord:
    id: int | None
    name: str
    capacity: int | None
    available_beds: int | None
    distance: float | None
    accessibility: str | None
    elevation_level: str | None
    proximity_to_water: str | None
    medical_facility: str | None
    latitude: float | None
    longitude: float | None


class Shelter(db.Model):
    __tablename__ = "shelters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer)
    available_beds = db.Column(db.Integer)
    distance = db.Column(db.Float)
    accessibility = db.Column(db.String(50))
    elevation_level = db.Column(db.String(50))
    proximity_to_water = db.Column(db.String(50))
    medical_facility = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    status_entries = db.relationship("ShelterStatus", back_populates="shelter", lazy="select")
    recommendation_logs = db.relationship("RecommendationLog", back_populates="top_shelter", lazy="select")
    alerts = db.relationship("Alert", back_populates="shelter", lazy="select")
    audit_logs = db.relationship("AuditLog", back_populates="shelter", lazy="select")

    def to_record(self) -> ShelterRecord:
        return ShelterRecord(
            id=self.id,
            name=self.name,
            capacity=self.capacity,
            available_beds=self.available_beds,
            distance=self.distance,
            accessibility=self.accessibility,
            elevation_level=self.elevation_level,
            proximity_to_water=self.proximity_to_water,
            medical_facility=self.medical_facility,
            latitude=self.latitude,
            longitude=self.longitude,
        )
