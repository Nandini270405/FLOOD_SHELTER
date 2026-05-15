from flask import Blueprint, current_app, jsonify, request

from ..schemas.recommendation import parse_json_payload, validate_num_people
from ..services.factory import build_recommendation_service

api_bp = Blueprint("api", __name__)


def _build_service():
    return build_recommendation_service(current_app.config["DB_PATH"])


@api_bp.route("/recommend", methods=["POST"])
def recommend():
    payload = parse_json_payload(request)
    try:
        num_people = validate_num_people(payload.get("num_people", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "num_people must be an integer >= 1"}), 400

    try:
        data = _build_service().recommend(
            num_people=num_people,
            distance_level=payload.get("distance_level", "medium"),
            accessibility_required=payload.get("accessibility_required", "moderate"),
            elevation_input=payload.get("elevation_input", "medium"),
            proximity_input=payload.get("proximity_input", "moderate"),
            medical_input=payload.get("medical_input", "basic"),
        )
    except Exception as exc:
        current_app.logger.exception("Recommendation error: %s", exc)
        return jsonify({"error": "Failed to compute recommendations. Check server logs."}), 500

    return jsonify(data)
