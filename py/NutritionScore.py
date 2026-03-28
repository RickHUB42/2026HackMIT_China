import math
from typing import Dict

def calculate_nutrition_score(
    gender: str,
    calcium: float = 0.0,
    cho: float = 0.0,
    protein: float = 0.0,
    vitamin_a: float = 0.0,
    vitamin_c: float = 0.0,
    vitamin_d: float = 0.0,
    vitamin_e: float = 0.0,
    thiamin: float = 0.0,
    riboflavin: float = 0.0,
    niacin: float = 0.0,
    vitamin_b6: float = 0.0,
    folate: float = 0.0,
    vitamin_b12: float = 0.0,
    copper: float = 0.0,
    iodine: float = 0.0,
    iron: float = 0.0,
    magnesium: float = 0.0,
    molybdenum: float = 0.0,
    phosphorus: float = 0.0,
    selenium: float = 0.0,
    zinc: float = 0.0,
    fat: float = 0.0
) -> float:
    """
    Calculate a nutrition score based on closeness to reference values.

    Parameters
    ----------
    gender : str
        "Male" or "Female"
    other params : float
        Nutrient intake values. Default is 0.0.

    Returns
    -------
    float
        Nutrition score in range roughly [0, 1000].
    """

    gender_normalized = gender.strip().lower()
    if gender_normalized not in {"male", "female"}:
        raise ValueError("gender must be 'Male' or 'Female'")

    # Reference table
    reference_table: Dict[str, Dict[str, float]] = {
        "male": {
            "calcium": 800.0,
            "cho": 100.0,
            "protein": 0.66,
            "vitamin_a": 625.0,
            "vitamin_c": 75.0,
            "vitamin_d": 10.0,
            "vitamin_e": 12.0,
            "thiamin": 1.0,
            "riboflavin": 1.1,
            "niacin": 12.0,
            "vitamin_b6": 1.1,
            "folate": 320.0,
            "vitamin_b12": 2.0,
            "copper": 700.0,
            "iodine": 95.0,
            "iron": 6.0,
            "magnesium": 330.0,
            "molybdenum": 34.0,
            "phosphorus": 580.0,
            "selenium": 45.0,
            "zinc": 9.4,
            "fat": 50.0,
        },
        "female": {
            "calcium": 800.0,
            "cho": 100.0,
            "protein": 0.66,
            "vitamin_a": 500.0,
            "vitamin_c": 60.0,
            "vitamin_d": 10.0,
            "vitamin_e": 12.0,
            "thiamin": 0.9,
            "riboflavin": 0.9,
            "niacin": 11.0,
            "vitamin_b6": 1.1,
            "folate": 320.0,
            "vitamin_b12": 2.0,
            "copper": 700.0,
            "iodine": 95.0,
            "iron": 8.1,
            "magnesium": 255.0,
            "molybdenum": 34.0,
            "phosphorus": 580.0,
            "selenium": 45.0,
            "zinc": 6.8,
            "fat": 50.0,
        },
    }

    # Different weights for each nutrient
    # Total does not need to be 100; we will normalize later
    weights: Dict[str, float] = {
        "calcium": 6.0,
        "cho": 5.0,
        "protein": 9.0,
        "vitamin_a": 4.0,
        "vitamin_c": 5.0,
        "vitamin_d": 8.0,
        "vitamin_e": 3.0,
        "thiamin": 3.0,
        "riboflavin": 3.0,
        "niacin": 3.0,
        "vitamin_b6": 4.0,
        "folate": 5.0,
        "vitamin_b12": 5.0,
        "copper": 2.0,
        "iodine": 4.0,
        "iron": 8.0,
        "magnesium": 7.0,
        "molybdenum": 2.0,
        "phosphorus": 4.0,
        "selenium": 4.0,
        "zinc": 5.0,
        "fat": 7.0,
    }

    inputs: Dict[str, float] = {
        "calcium": calcium,
        "cho": cho,
        "protein": protein,
        "vitamin_a": vitamin_a,
        "vitamin_c": vitamin_c,
        "vitamin_d": vitamin_d,
        "vitamin_e": vitamin_e,
        "thiamin": thiamin,
        "riboflavin": riboflavin,
        "niacin": niacin,
        "vitamin_b6": vitamin_b6,
        "folate": folate,
        "vitamin_b12": vitamin_b12,
        "copper": copper,
        "iodine": iodine,
        "iron": iron,
        "magnesium": magnesium,
        "molybdenum": molybdenum,
        "phosphorus": phosphorus,
        "selenium": selenium,
        "zinc": zinc,
        "fat": fat,
    }

    reference = reference_table[gender_normalized]

    # Penalty strength:
    # larger k -> score drops faster when away from target
    k = 2.5

    weighted_score_sum = 0.0
    weight_sum = 0.0

    for nutrient, actual in inputs.items():
        target = reference[nutrient]
        weight = weights[nutrient]

        # avoid division by zero, though table values are all > 0
        if target <= 0:
            continue

        # relative error: symmetric for too low / too high
        relative_error = abs(actual - target) / target

        # score in [0, 1], best at actual == target
        nutrient_score = math.exp(-k * relative_error)

        weighted_score_sum += nutrient_score * weight
        weight_sum += weight

    if weight_sum == 0:
        return 0.0

    final_score = (weighted_score_sum / weight_sum) * 1000.0
    return float(round(final_score, 4))