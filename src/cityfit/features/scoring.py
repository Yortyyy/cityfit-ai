import pandas as pd

from cityfit.features.transformations import add_cityfit_features


def calculate_cityfit_score(
    df: pd.DataFrame,
    weights: dict,
    personalization_strength: float = 0.20,
) -> pd.DataFrame:
    """
    Calculate personalized CityFit score.

    Numbeo's Quality of Life Index is the baseline.
    CityFit adds a small user-priority adjustment.
    """
    scored = add_cityfit_features(df.copy())

    # TODO - weights[cost of living] or weights [cost penalty]?
    personalization_adjustment = (
        scored["purchasing_power_score"] * weights["purchasing_power"]
        + scored["safety_score"] * weights["safety"]
        + scored["healthcare_score"] * weights["healthcare"]
        + scored["climate_score"] * weights["climate"]
        + scored["affordability_score"] * weights["affordability"]
        + scored["housing_affordability_score"] * weights["housing_affordability"]
        + scored["low_pollution_score"] * weights["low_pollution"]
        + scored["low_traffic_score"] * weights["low_traffic"]
    )

    scored["personalization_adjustment"] = (
        personalization_adjustment * personalization_strength
    )

    scored["cityfit_score"] = (
        scored["numbeo_quality_of_life_index"]
        + scored["personalization_adjustment"]
    )

    return scored


def add_cityfit_rank(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.copy()

    ranked["numbeo_qol_rank"] = ranked["numbeo_quality_of_life_index"].rank(
        ascending=False,
        method="min",
    )

    ranked["cityfit_rank"] = ranked["cityfit_score"].rank(
        ascending=False,
        method="min",
    )

    ranked["rank_difference"] = (
        ranked["numbeo_qol_rank"] - ranked["cityfit_rank"]
    )

    return ranked


def rank_cities(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return (
        df.sort_values("cityfit_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )