import pandas as pd


def min_max_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """Scale a metric to a dataset-relative 0-100 score."""
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(50, index=series.index)

    score = (series - min_value) / (max_value - min_value) * 100

    if not higher_is_better:
        score = 100 - score

    return score


def add_affordability_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create dataset-relative 0-100 normalized city scoring features."""
    features = df.copy()

    features["qol_score"] = min_max_score(
        features["numbeo_quality_of_life_index"],
        higher_is_better=True,
    )

    features["purchasing_power_score"] = min_max_score(
        features["purchasing_power_index"],
        higher_is_better=True,
    )

    features["safety_score"] = min_max_score(
        features["safety_index"],
        higher_is_better=True,
    )

    features["healthcare_score"] = min_max_score(
        features["healthcare_index"],
        higher_is_better=True,
    )

    features["climate_score"] = min_max_score(
        features["climate_index"],
        higher_is_better=True,
    )

    features["affordability_score"] = min_max_score(
        features["cost_of_living_index"],
        higher_is_better=False,
    )

    features["housing_affordability_score"] = min_max_score(
        features["property_price_to_income_ratio"],
        higher_is_better=False,
    )

    features["low_pollution_score"] = min_max_score(
        features["pollution_index"],
        higher_is_better=False,
    )

    features["low_traffic_score"] = min_max_score(
        features["traffic_commute_index"],
        higher_is_better=False,
    )

    features["cityfit_score"] = (
    features["qol_score"] * 0.20
    + features["safety_score"] * 0.18
    + features["healthcare_score"] * 0.14
    + features["low_pollution_score"] * 0.14
    + features["low_traffic_score"] * 0.10
    + features["climate_score"] * 0.08
    + features["purchasing_power_score"] * 0.08
    + features["affordability_score"] * 0.04
    + features["housing_affordability_score"] * 0.04
)

    return features