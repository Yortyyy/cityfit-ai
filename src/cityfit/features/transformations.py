import pandas as pd


def min_max_scale(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(50.0, index=series.index)

    scaled = (series - min_value) / (max_value - min_value) * 100

    if not higher_is_better:
        scaled = 100 - scaled

    return scaled


def add_cityfit_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add helper feature scores used for CityFit personalization.

    These are not the final CityFit score.
    Numbeo's Quality of Life Index remains the baseline.
    """
    features = df.copy()

    features["purchasing_power_score"] = min_max_scale(
        features["purchasing_power_index"],
        higher_is_better=True,
    )

    features["safety_score"] = min_max_scale(
        features["safety_index"],
        higher_is_better=True,
    )

    features["healthcare_score"] = min_max_scale(
        features["healthcare_index"],
        higher_is_better=True,
    )

    features["climate_score"] = min_max_scale(
        features["climate_index"],
        higher_is_better=True,
    )

    features["affordability_score"] = min_max_scale(
        features["cost_of_living_index"],
        higher_is_better=False,
    )

    features["housing_affordability_score"] = min_max_scale(
        features["property_price_to_income_ratio"],
        higher_is_better=False,
    )

    features["low_pollution_score"] = min_max_scale(
        features["pollution_index"],
        higher_is_better=False,
    )

    features["low_traffic_score"] = min_max_scale(
        features["traffic_commute_index"],
        higher_is_better=False,
    )

    return features