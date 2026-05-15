# Defines fuzzy membership functions and a compact rule base.

from functools import lru_cache

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


@lru_cache(maxsize=1)
def _build_control_system():
    distance = ctrl.Antecedent(np.arange(0, 21, 1), "distance")
    distance["near"] = fuzz.trapmf(distance.universe, [0, 0, 3, 7])
    distance["medium"] = fuzz.trimf(distance.universe, [4, 9, 14])
    distance["far"] = fuzz.trapmf(distance.universe, [11, 15, 20, 20])

    capacity = ctrl.Antecedent(np.arange(0, 101, 1), "capacity")
    capacity["low"] = fuzz.trapmf(capacity.universe, [0, 0, 20, 40])
    capacity["medium"] = fuzz.trimf(capacity.universe, [30, 55, 80])
    capacity["high"] = fuzz.trapmf(capacity.universe, [65, 85, 100, 100])

    accessibility = ctrl.Antecedent(np.arange(0, 11, 1), "accessibility")
    accessibility["low"] = fuzz.trapmf(accessibility.universe, [0, 0, 2, 4])
    accessibility["medium"] = fuzz.trimf(accessibility.universe, [3, 5, 7])
    accessibility["high"] = fuzz.trapmf(accessibility.universe, [6, 8, 10, 10])

    elevation = ctrl.Antecedent(np.arange(0, 11, 1), "elevation")
    elevation["low"] = fuzz.trapmf(elevation.universe, [0, 0, 2, 4])
    elevation["medium"] = fuzz.trimf(elevation.universe, [3, 5, 7])
    elevation["high"] = fuzz.trapmf(elevation.universe, [6, 8, 10, 10])

    proximity = ctrl.Antecedent(np.arange(0, 11, 1), "proximity")
    proximity["very_close"] = fuzz.trapmf(proximity.universe, [0, 0, 1, 3])
    proximity["moderate"] = fuzz.trimf(proximity.universe, [2, 5, 8])
    proximity["far"] = fuzz.trapmf(proximity.universe, [7, 9, 10, 10])

    medical = ctrl.Antecedent(np.arange(0, 11, 1), "medical")
    medical["none"] = fuzz.trapmf(medical.universe, [0, 0, 1, 3])
    medical["basic"] = fuzz.trimf(medical.universe, [2, 5, 7])
    medical["advanced"] = fuzz.trapmf(medical.universe, [6, 8, 10, 10])

    suitability = ctrl.Consequent(np.arange(0, 101, 1), "suitability")
    suitability["very_low"] = fuzz.trapmf(suitability.universe, [0, 0, 10, 25])
    suitability["low"] = fuzz.trimf(suitability.universe, [15, 30, 45])
    suitability["medium"] = fuzz.trimf(suitability.universe, [40, 55, 70])
    suitability["high"] = fuzz.trimf(suitability.universe, [65, 78, 90])
    suitability["excellent"] = fuzz.trapmf(suitability.universe, [85, 93, 100, 100])

    rules = [
        ctrl.Rule(
            distance["near"]
            & capacity["high"]
            & accessibility["high"]
            & elevation["high"]
            & proximity["far"]
            & medical["advanced"],
            suitability["excellent"],
        ),
        ctrl.Rule(
            distance["near"]
            & capacity["high"]
            & accessibility["high"]
            & elevation["high"]
            & proximity["moderate"]
            & medical["advanced"],
            suitability["high"],
        ),
        ctrl.Rule(
            distance["near"]
            & capacity["medium"]
            & accessibility["high"]
            & elevation["high"]
            & proximity["moderate"]
            & medical["advanced"],
            suitability["high"],
        ),
        ctrl.Rule(
            distance["medium"]
            & capacity["medium"]
            & accessibility["medium"]
            & elevation["medium"]
            & proximity["moderate"]
            & medical["basic"],
            suitability["medium"],
        ),
        ctrl.Rule(
            distance["near"]
            & capacity["low"]
            & accessibility["high"]
            & elevation["high"]
            & (medical["basic"] | medical["advanced"]),
            suitability["medium"],
        ),
        ctrl.Rule(
            distance["far"] & capacity["low"],
            suitability["low"],
        ),
        ctrl.Rule(
            accessibility["low"] & distance["far"],
            suitability["low"],
        ),
        ctrl.Rule(
            elevation["low"] & proximity["very_close"],
            suitability["very_low"],
        ),
        ctrl.Rule(
            elevation["low"] & medical["none"],
            suitability["low"],
        ),
        ctrl.Rule(
            proximity["very_close"] & medical["none"] & accessibility["low"],
            suitability["very_low"],
        ),
        ctrl.Rule(
            capacity["high"] & elevation["high"] & proximity["far"],
            suitability["high"],
        ),
        ctrl.Rule(
            capacity["medium"] & accessibility["medium"] & elevation["high"],
            suitability["medium"],
        ),
        ctrl.Rule(
            distance["near"] & accessibility["high"] & medical["advanced"],
            suitability["high"],
        ),
        ctrl.Rule(
            distance["medium"] & accessibility["medium"] & medical["advanced"],
            suitability["medium"],
        ),
        ctrl.Rule(
            capacity["low"] & accessibility["low"],
            suitability["low"],
        ),
        ctrl.Rule(
            elevation["medium"] & proximity["moderate"] & medical["basic"],
            suitability["medium"],
        ),
        ctrl.Rule(
            accessibility["high"] & elevation["high"] & medical["advanced"],
            suitability["high"],
        ),
        ctrl.Rule(
            distance["far"] & proximity["very_close"],
            suitability["low"],
        ),
        # Narrower fallback: near/medium distance with decent capacity & accessibility → medium
        # (replaces the removed overbroad rule that fired for ALL shelters and corrupted scores)
        ctrl.Rule(
            (distance["near"] | distance["medium"])
            & (capacity["medium"] | capacity["high"])
            & (accessibility["medium"] | accessibility["high"]),
            suitability["medium"],
        ),
    ]

    return ctrl.ControlSystem(rules)


def get_fuzzy_simulator(
    capacity_val,
    distance_val,
    accessibility_val,
    elevation_val,
    proximity_val,
    medical_val,
):
    system = _build_control_system()
    sim = ctrl.ControlSystemSimulation(system)

    sim.input["capacity"] = capacity_val
    sim.input["distance"] = distance_val
    sim.input["accessibility"] = accessibility_val
    sim.input["elevation"] = elevation_val
    sim.input["proximity"] = proximity_val
    sim.input["medical"] = medical_val

    try:
        sim.compute()
        return sim.output["suitability"]
    except Exception:
        # Degenerate case: no rules fired for this input combination.
        # Return a low-but-non-zero fallback so the shelter still appears
        # in ranked output rather than crashing the whole request.
        return 10.0
