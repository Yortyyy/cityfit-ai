import pandas as pd


def add_affordability_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived city-level affordability and quality features."""
    features = df.copy()

    features["quality_per_cost"] = (
        features["numbeo_quality_of_life_index"]
        / features["cost_of_living_index"]
    )

    features["purchasing_power_per_cost"] = (
        features["purchasing_power_index"]
        / features["cost_of_living_index"]
    )

    features["safety_healthcare_avg"] = (
        features["safety_index"] + features["healthcare_index"]
    ) / 2

    features["low_pollution_score"] = 100 - features["pollution_index"]

    features["low_traffic_score"] = 100 - features["traffic_commute_index"]

    return features