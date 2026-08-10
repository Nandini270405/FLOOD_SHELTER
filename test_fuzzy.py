import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

try:
    distance = ctrl.Antecedent(np.arange(0, 21, 1), "distance")
    distance["near"] = fuzz.trapmf(distance.universe, [0, 0, 3, 7])
    print("Success: skfuzzy and numpy are compatible.")
except Exception as e:
    print(f"Failure: {e}")
    import traceback
    traceback.print_exc()
