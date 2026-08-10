from typing import Dict, List

import numpy as np
from .fuzzy_engine import FuzzyRecommenderEngine

from ..repositories.shelter_repository import ShelterRepository

DISTANCE_MAP = {"near": 3, "medium": 10, "far": 18}
ACCESS_MAP = {"difficult": 2, "moderate": 5, "easy": 8}
ELEVATION_MAP = {"low": 2, "medium": 5, "high": 8}
PROXIMITY_MAP = {"very close": 2, "moderate": 5, "far": 8}
MEDICAL_MAP = {"none": 2, "basic": 5, "advanced": 8}
ACCESS_RANK = {"difficult": 0, "moderate": 1, "easy": 2}


class RecommendationService:
    def __init__(self, db_path: str):
        self.repository = ShelterRepository(db_path)
        self.fuzzy_engine = FuzzyRecommenderEngine()

    def get_dataset_info(self) -> Dict:
        return self.repository.fetch_dataset_info()

    def recommend(
        self,
        num_people: int,
        distance_level: str,
        accessibility_required: str,
        elevation_input: str,
        proximity_input: str,
        medical_input: str,
    ) -> Dict:
        distance_level = _normalize_choice(distance_level, DISTANCE_MAP, "medium")
        accessibility_required = _normalize_choice(accessibility_required, ACCESS_MAP, "moderate")
        elevation_input = _normalize_choice(elevation_input, ELEVATION_MAP, "medium")
        proximity_input = _normalize_choice(proximity_input, PROXIMITY_MAP, "moderate")
        medical_input = _normalize_choice(medical_input, MEDICAL_MAP, "basic")

        max_distance = DISTANCE_MAP.get(distance_level, 10)
        desired_access_num = ACCESS_MAP.get(accessibility_required, 5)
        elevation_num = ELEVATION_MAP.get(elevation_input, 5)
        proximity_num = PROXIMITY_MAP.get(proximity_input, 5)
        medical_num = MEDICAL_MAP.get(medical_input, 5)
        dataset_info = self.get_dataset_info()

        rows = self.repository.fetch_candidates(num_people, max_distance)
        recommendations: List[Dict] = []

        for row in rows:
            shelter_accessibility = row["accessibility"].lower()
            if not _accessibility_matches(shelter_accessibility, accessibility_required):
                continue

            elevation_level = row["elevation_level"].lower()
            proximity_to_water = row["proximity_to_water"].lower()
            medical_facility = row["medical_facility"].lower()

            access_num = int(np.clip(ACCESS_MAP.get(shelter_accessibility, 5), 0, 10))
            elevation_score = int(np.clip(ELEVATION_MAP.get(elevation_level, 5), 0, 10))
            proximity_score = int(np.clip(PROXIMITY_MAP.get(proximity_to_water, 5), 0, 10))
            medical_score = int(np.clip(MEDICAL_MAP.get(medical_facility, 5), 0, 10))

            # Universe for capacity is [0, 100], distance is [0, 20]
            beds = row["available_beds"] if row["available_beds"] is not None else 0
            usable_capacity = int(np.clip(min(max(beds, num_people), 100), 0, 100))
            dist_val = float(np.clip(row["distance"] if row["distance"] is not None else 20, 0, 20))

            try:
                score_val = self.fuzzy_engine.compute_suitability(
                    usable_capacity,
                    dist_val,
                    access_num,
                    elevation_score,
                    proximity_score,
                    medical_score,
                )
                score = float(score_val)
                if np.isnan(score):
                    score = 0.0
            except Exception:
                score = 0.0

            recommendations.append(
                {
                    "name": row["name"],
                    "capacity": row["capacity"],
                    "available_beds": row["available_beds"],
                    "distance": row["distance"],
                    "accessibility": row["accessibility"],
                    "elevation_level": row["elevation_level"],
                    "proximity_to_water": row["proximity_to_water"],
                    "medical_facility": row["medical_facility"],
                    "score": round(score, 2),
                    "distance_match": distance_level,
                    "accessibility_match": shelter_accessibility,
                    "matches_requested_accessibility": _accessibility_matches(
                        shelter_accessibility, accessibility_required
                    ),
                    "available_capacity_score": usable_capacity,
                    "lat": row["latitude"] if row["latitude"] is not None else 20.3000,
                    "lng": row["longitude"] if row["longitude"] is not None else 85.8200,
                }
            )

        recommendations.sort(key=lambda item: item["score"], reverse=True)
        best = recommendations[0] if recommendations else None

        return {
            "filters": {
                "num_people": num_people,
                "distance_level": distance_level,
                "accessibility_required": accessibility_required,
                "elevation_input": elevation_input,
                "proximity_input": proximity_input,
                "medical_input": medical_input,
            },
            "inputs_numeric": {
                "distance": float(DISTANCE_MAP.get(distance_level, 10)),
                "accessibility": int(desired_access_num),
                "elevation": int(elevation_num),
                "proximity": int(proximity_num),
                "medical": int(medical_num),
            },
            "recommendations": recommendations,
            "best": best,
            "dataset": dataset_info,
            "summary": {
                "count": len(recommendations),
                "requested_accessibility": accessibility_required,
                "max_distance_km": max_distance,
            },
        }


def _normalize_choice(value: str, allowed_map: Dict[str, int], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed_map else fallback


def _accessibility_matches(shelter_accessibility: str, requested_accessibility: str) -> bool:
    shelter_rank = ACCESS_RANK.get((shelter_accessibility or "").strip().lower(), -1)
    requested_rank = ACCESS_RANK.get(requested_accessibility, ACCESS_RANK["moderate"])
    return shelter_rank >= requested_rank
