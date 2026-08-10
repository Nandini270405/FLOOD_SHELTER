from recommender import recommend_shelters
from flood_app.schemas.recommendation import CHOICES, validate_num_people


def prompt_positive_int(prompt):
    while True:
        raw_value = input(prompt).strip()
        try:
            value = validate_num_people(raw_value)
            return value
        except ValueError:
            print("Invalid input. Enter a positive whole number (example: 4).")


def prompt_choice(prompt, options):
    allowed = "/".join(options)
    while True:
        value = input(f"{prompt} ({allowed}): ").strip().lower()
        if value in options:
            return value
        print(f"Choose one of: {allowed}.")


def main():
    num_people = prompt_positive_int("Enter number of people: ")
    distance_level = prompt_choice("How far can you travel?", CHOICES["distance_level"])
    accessibility_required = prompt_choice("Accessibility needed?", CHOICES["accessibility_required"])
    elevation_input = prompt_choice("Your elevation level?", CHOICES["elevation_input"])
    proximity_input = prompt_choice("How close to water?", CHOICES["proximity_input"])
    medical_input = prompt_choice("Medical support needed?", CHOICES["medical_input"])

    data = recommend_shelters(
        num_people=num_people,
        distance_level=distance_level,
        accessibility_required=accessibility_required,
        elevation_input=elevation_input,
        proximity_input=proximity_input,
        medical_input=medical_input,
    )

    if not data["recommendations"]:
        print("\nNo shelters matched your criteria.")
        return

    print("\nRanked shelters:\n")
    for shelter in data["recommendations"]:
        print(
            f"{shelter['name']}: score={shelter['score']}, "
            f"distance={shelter['distance']} km, beds={shelter['available_beds']}, "
            f"access={shelter['accessibility']}"
        )

    best = data["best"]
    print(f"\nBest match: {best['name']} (score {best['score']})")


if __name__ == "__main__":
    main()
