from dataclasses import asdict
from typing import List

from ..db import db
from ..models.shelter import AppMetadata, Shelter


class ShelterRepository:
    def __init__(self, _db_path: str):
        # db_path is ignored in favor of the active SQLAlchemy session
        pass

    def fetch_dataset_info(self) -> dict:
        dataset_info = {
            "source_type": "demo",
            "dataset_name": "Built-in demo shelters",
            "record_count": 0,
            "is_demo": True,
        }

        if Shelter is None or db is None:
            return dataset_info

        try:
            metadata_entries = AppMetadata.query.all()
            metadata = {m.key: m.value for m in metadata_entries}
            if metadata:
                dataset_info["source_type"] = metadata.get("source_type", dataset_info["source_type"])
                dataset_info["dataset_name"] = metadata.get("dataset_name", dataset_info["dataset_name"])
                dataset_info["is_demo"] = dataset_info["source_type"] == "demo"
        except Exception:
            # Table might not exist yet, fallback to demo defaults
            pass

        try:
            dataset_info["record_count"] = Shelter.query.count()
            
            # If no metadata, try to guess if it's demo
            if dataset_info["source_type"] == "demo" and dataset_info["record_count"] > 0:
                demo_count = Shelter.query.filter(Shelter.name.like("Shelter %")).count()
                dataset_info["is_demo"] = demo_count == dataset_info["record_count"]
                if not dataset_info["is_demo"]:
                    dataset_info["source_type"] = "custom"
                    dataset_info["dataset_name"] = "Imported shelter dataset"
        except Exception:
            pass

        return dataset_info

    def fetch_candidates(self, min_beds: int, max_distance: float) -> List[dict]:
        if Shelter is None:
            return []
        
        shelters = (
            Shelter.query.filter(Shelter.available_beds >= min_beds, Shelter.distance <= max_distance)
            .order_by(Shelter.distance.asc())
            .all()
        )
        return [asdict(shelter.to_record()) for shelter in shelters]
