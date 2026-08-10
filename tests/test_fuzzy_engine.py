import pytest
from flood_app.services.fuzzy_engine import FuzzyRecommenderEngine

def test_fuzzy_engine_logic():
    engine = FuzzyRecommenderEngine()
    
    # Test a high suitability case
    score_high = engine.compute_suitability(
        capacity_val=90,
        distance_val=2,
        accessibility_val=9,
        elevation_val=9,
        proximity_val=9,
        medical_val=9
    )
    
    # Test a low suitability case
    score_low = engine.compute_suitability(
        capacity_val=10,
        distance_val=18,
        accessibility_val=2,
        elevation_val=2,
        proximity_val=2,
        medical_val=2
    )
    
    assert score_high > score_low
    assert 0 <= score_high <= 100
    assert 0 <= score_low <= 100

def test_fuzzy_engine_caching():
    engine = FuzzyRecommenderEngine()
    score1 = engine.compute_suitability(80, 5, 8, 8, 8, 8)
    score2 = engine.compute_suitability(80, 5, 8, 8, 8, 8)
    assert score1 == score2
