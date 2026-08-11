from dataclasses import asdict
from typing import List, Tuple

from ..db import db
from ..models.shelter import AppMetadata, Shelter

BUILTIN_DEMO_RECORDS = [
    {"name": 'Shelter A', "capacity": 100, "available_beds": 30, "distance": 2.5, "accessibility": 'easy',     "elevation_level": 'high',   "proximity_to_water": 'moderate', "medical_facility": 'advanced', "latitude": 20.3068, "longitude": 85.8199},
    {"name": 'Shelter B', "capacity": 80,  "available_beds": 5,  "distance": 5.0, "accessibility": 'moderate',   "elevation_level": 'medium', "proximity_to_water": 'very close', "medical_facility": 'basic', "latitude": 20.3130, "longitude": 85.8254},
    {"name": 'Shelter C', "capacity": 60,  "available_beds": 10, "distance": 1.0, "accessibility": 'difficult',  "elevation_level": 'low',    "proximity_to_water": 'very close', "medical_facility": 'none', "latitude": 20.3002, "longitude": 85.8107},
    {"name": 'Shelter D', "capacity": 120, "available_beds": 50, "distance": 3.0, "accessibility": 'easy',     "elevation_level": 'high',   "proximity_to_water": 'far',        "medical_facility": 'advanced', "latitude": 20.3218, "longitude": 85.8342},
    {"name": 'Shelter E', "capacity": 90,  "available_beds": 20, "distance": 6.5, "accessibility": 'moderate',   "elevation_level": 'medium', "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.2976, "longitude": 85.8441},
    {"name": 'Shelter F', "capacity": 70,  "available_beds": 0,  "distance": 4.5, "accessibility": 'difficult',  "elevation_level": 'low',    "proximity_to_water": 'very close', "medical_facility": 'none', "latitude": 20.2929, "longitude": 85.8215},
    {"name": 'Shelter G', "capacity": 85,  "available_beds": 15, "distance": 2.0, "accessibility": 'moderate',   "elevation_level": 'medium', "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.3155, "longitude": 85.8094},
    {"name": 'Shelter H', "capacity": 110, "available_beds": 40, "distance": 3.8, "accessibility": 'easy',     "elevation_level": 'high',   "proximity_to_water": 'far',        "medical_facility": 'advanced', "latitude": 20.3266, "longitude": 85.8178},
    {"name": 'Shelter I', "capacity": 95,  "available_beds": 25, "distance": 7.0, "accessibility": 'difficult',  "elevation_level": 'medium', "proximity_to_water": 'far',        "medical_facility": 'basic', "latitude": 20.2888, "longitude": 85.8352},
    {"name": 'Shelter J', "capacity": 75,  "available_beds": 18, "distance": 1.5, "accessibility": 'moderate',   "elevation_level": 'medium', "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.3092, "longitude": 85.8039},
    {"name": 'Shelter K', "capacity": 65,  "available_beds": 22, "distance": 2.2, "accessibility": 'easy',      "elevation_level": 'medium', "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.3188, "longitude": 85.8421},
    {"name": 'Shelter L', "capacity": 55,  "available_beds": 5,  "distance": 6.2, "accessibility": 'difficult',  "elevation_level": 'low',    "proximity_to_water": 'very close', "medical_facility": 'none', "latitude": 20.2844, "longitude": 85.8132},
    {"name": 'Shelter M', "capacity": 105, "available_beds": 35, "distance": 4.0, "accessibility": 'moderate',  "elevation_level": 'high',   "proximity_to_water": 'moderate',   "medical_facility": 'advanced', "latitude": 20.3290, "longitude": 85.8280},
    {"name": 'Shelter N', "capacity": 60,  "available_beds": 8,  "distance": 8.0, "accessibility": 'moderate',   "elevation_level": 'medium', "proximity_to_water": 'far',        "medical_facility": 'basic', "latitude": 20.2795, "longitude": 85.8233},
    {"name": 'Shelter O', "capacity": 130, "available_beds": 60, "distance": 3.5, "accessibility": 'easy',     "elevation_level": 'high',   "proximity_to_water": 'far',        "medical_facility": 'advanced', "latitude": 20.3336, "longitude": 85.8099},
    {"name": 'Shelter P', "capacity": 40,  "available_beds": 15, "distance": 9.0, "accessibility": 'difficult',  "elevation_level": 'low',    "proximity_to_water": 'very close', "medical_facility": 'none', "latitude": 20.2738, "longitude": 85.8380},
    {"name": 'Shelter Q', "capacity": 90,  "available_beds": 25, "distance": 5.5, "accessibility": 'moderate',  "elevation_level": 'medium', "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.3057, "longitude": 85.8515},
    {"name": 'Shelter R', "capacity": 100, "available_beds": 30, "distance": 1.8, "accessibility": 'easy',     "elevation_level": 'high',   "proximity_to_water": 'moderate',   "medical_facility": 'advanced', "latitude": 20.3199, "longitude": 85.7970},
    {"name": 'Shelter S', "capacity": 80,  "available_beds": 12, "distance": 4.8, "accessibility": 'moderate',  "elevation_level": 'medium', "proximity_to_water": 'very close', "medical_facility": 'basic', "latitude": 20.2951, "longitude": 85.8541},
    {"name": 'Shelter T', "capacity": 95,  "available_beds": 27, "distance": 6.0, "accessibility": 'difficult',  "elevation_level": 'medium', "proximity_to_water": 'far',        "medical_facility": 'basic', "latitude": 20.2866, "longitude": 85.8015},
    {"name": 'Shelter U', "capacity": 50,  "available_beds": 50, "distance": 10.0,"accessibility": 'easy',     "elevation_level": 'medium', "proximity_to_water": 'far',        "medical_facility": 'none', "latitude": 20.2716, "longitude": 85.8158},
    {"name": 'Shelter V', "capacity": 120, "available_beds": 5,  "distance": 0.5, "accessibility": 'difficult',  "elevation_level": 'low',    "proximity_to_water": 'very close', "medical_facility": 'none', "latitude": 20.3385, "longitude": 85.8209},
    {"name": 'Shelter W', "capacity": 75,  "available_beds": 18, "distance": 7.2, "accessibility": 'moderate',  "elevation_level": 'low',    "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.2762, "longitude": 85.8460},
    {"name": 'Shelter X', "capacity": 90,  "available_beds": 20, "distance": 3.3, "accessibility": 'easy',      "elevation_level": 'high',   "proximity_to_water": 'moderate',   "medical_facility": 'advanced', "latitude": 20.3241, "longitude": 85.8476},
    {"name": 'Shelter Y', "capacity": 110, "available_beds": 0,  "distance": 5.5, "accessibility": 'moderate',  "elevation_level": 'medium', "proximity_to_water": 'far',        "medical_facility": 'none', "latitude": 20.3014, "longitude": 85.7922},
    {"name": 'Shelter Z', "capacity": 60,  "available_beds": 40, "distance": 2.0, "accessibility": 'difficult',  "elevation_level": 'medium', "proximity_to_water": 'moderate',   "medical_facility": 'basic', "latitude": 20.3125, "longitude": 85.8368},
]


class ShelterRepository:
    def __init__(self, _db_path: str):
        pass

    def fetch_dataset_info(self) -> dict:
        dataset_info = {
            "source_type": "demo",
            "dataset_name": "Built-in demo shelters",
            "record_count": len(BUILTIN_DEMO_RECORDS),
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
            pass

        try:
            count = Shelter.query.count()
            if count > 0:
                dataset_info["record_count"] = count
                demo_count = Shelter.query.filter(Shelter.name.like("Shelter %")).count()
                dataset_info["is_demo"] = demo_count == dataset_info["record_count"]
                if not dataset_info["is_demo"]:
                    dataset_info["source_type"] = "custom"
                    dataset_info["dataset_name"] = "Imported shelter dataset"
        except Exception:
            pass

        return dataset_info

    def fetch_candidates(self, min_beds: int, max_distance: float) -> Tuple[List[dict], bool]:
        db_records = []
        if Shelter is not None:
            try:
                # 1. Try exact requested constraints (min beds & max distance)
                strict = (
                    Shelter.query.filter(Shelter.available_beds >= min_beds, Shelter.distance <= max_distance)
                    .order_by(Shelter.distance.asc())
                    .all()
                )
                if strict:
                    return [asdict(s.to_record()) for s in strict], False

                # 2. Expanded search: Relax max_distance constraint
                expanded = (
                    Shelter.query.filter(Shelter.available_beds >= min_beds)
                    .order_by(Shelter.distance.asc())
                    .all()
                )
                if expanded:
                    return [asdict(s.to_record()) for s in expanded], True

                # 3. Fallback: Any available beds
                all_beds = (
                    Shelter.query.filter(Shelter.available_beds > 0)
                    .order_by(Shelter.distance.asc())
                    .all()
                )
                if all_beds:
                    return [asdict(s.to_record()) for s in all_beds], True

                db_all = Shelter.query.order_by(Shelter.distance.asc()).all()
                if db_all:
                    return [asdict(s.to_record()) for s in db_all], True
            except Exception:
                pass

        # In-memory fallback if DB is uninitialized on serverless environment
        strict_demo = [r for r in BUILTIN_DEMO_RECORDS if r["available_beds"] >= min_beds and r["distance"] <= max_distance]
        if strict_demo:
            return strict_demo, False

        expanded_demo = [r for r in BUILTIN_DEMO_RECORDS if r["available_beds"] >= min_beds]
        if expanded_demo:
            return expanded_demo, True

        return BUILTIN_DEMO_RECORDS, True
