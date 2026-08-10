from flood_app import create_app
from flood_app.services.factory import recommend_shelters

app = create_app()
with app.app_context():
    try:
        data = recommend_shelters(
            num_people=1,
            distance_level="medium",
            accessibility_required="moderate",
            elevation_input="medium",
            proximity_input="moderate",
            medical_input="basic",
        )
        print("Success!")
        print(f"Found {len(data['recommendations'])} shelters.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
