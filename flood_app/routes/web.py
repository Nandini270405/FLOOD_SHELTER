from flask import Blueprint, current_app, render_template, request

from ..schemas.recommendation import CHOICES, parse_form_payload, validate_num_people
from ..services.factory import build_recommendation_service

web_bp = Blueprint("web", __name__)


def _build_service():
    return build_recommendation_service(current_app.config["DB_PATH"])


@web_bp.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        choices=CHOICES,
        data=None,
        dataset_info=_build_service().get_dataset_info(),
        error=None,
    )


@web_bp.route("/recommend", methods=["POST"])
def recommend():
    payload = parse_form_payload(request.form)
    try:
        num_people = validate_num_people(payload.get("num_people", "1"))
    except ValueError:
        return render_template(
            "index.html",
            choices=CHOICES,
            data=None,
            dataset_info=_build_service().get_dataset_info(),
            error="Enter a valid number of people (>= 1).",
        )

    data = _build_service().recommend(
        num_people=num_people,
        distance_level=payload.get("distance_level", "medium"),
        accessibility_required=payload.get("accessibility_required", "moderate"),
        elevation_input=payload.get("elevation_input", "medium"),
        proximity_input=payload.get("proximity_input", "moderate"),
        medical_input=payload.get("medical_input", "basic"),
    )
    return render_template(
        "index.html",
        choices=CHOICES,
        data=data,
        dataset_info=data.get("dataset"),
        error=None,
    )
