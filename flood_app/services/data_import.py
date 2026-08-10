import csv
from pathlib import Path
from ..db import db
from ..models import Shelter, AppMetadata

REQUIRED_COLUMNS = [
    "name",
    "capacity",
    "available_beds",
    "distance",
    "accessibility",
    "elevation_level",
    "proximity_to_water",
    "medical_facility",
    "latitude",
    "longitude",
]

def import_csv_to_db(csv_path: Path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV file is missing a header row.")

        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing)}")

        # Clear existing data
        Shelter.query.delete()
        AppMetadata.query.filter(AppMetadata.key.in_(["source_type", "dataset_name"])).delete()

        for line_number, row in enumerate(reader, start=2):
            try:
                shelter = Shelter(
                    name=row["name"].strip(),
                    capacity=int(row["capacity"]),
                    available_beds=int(row["available_beds"]),
                    distance=float(row["distance"]),
                    accessibility=row["accessibility"].strip().lower(),
                    elevation_level=row["elevation_level"].strip().lower(),
                    proximity_to_water=row["proximity_to_water"].strip().lower(),
                    medical_facility=row["medical_facility"].strip().lower(),
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                )
                db.session.add(shelter)
            except (TypeError, ValueError) as exc:
                db.session.rollback()
                raise ValueError(f"Invalid data on CSV line {line_number}: {exc}") from exc

        db.session.add(AppMetadata(key="source_type", value="custom"))
        db.session.add(AppMetadata(key="dataset_name", value=csv_path.stem))
        
        db.session.commit()
