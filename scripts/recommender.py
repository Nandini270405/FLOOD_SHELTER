from flood_app import recommend_shelters as recommend_shelters_via_service


def recommend_shelters(
    num_people: int,
    distance_level: str,
    accessibility_required: str,
    elevation_input: str,
    proximity_input: str,
    medical_input: str,
):
    return recommend_shelters_via_service(
        num_people=num_people,
        distance_level=distance_level,
        accessibility_required=accessibility_required,
        elevation_input=elevation_input,
        proximity_input=proximity_input,
        medical_input=medical_input,
    )
