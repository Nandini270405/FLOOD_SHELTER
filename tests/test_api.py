import pytest

def test_recommend_api(client, seed_data):
    payload = {
        "num_people": 1,
        "distance_level": "medium",
        "accessibility_required": "moderate",
        "elevation_input": "medium",
        "proximity_input": "moderate",
        "medical_input": "basic"
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert data["recommendations"][0]["name"] == "Test Shelter"

def test_recommend_api_no_candidates(client, db):
    # No data seeded
    payload = {
        "num_people": 1
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["recommendations"]) == 0
