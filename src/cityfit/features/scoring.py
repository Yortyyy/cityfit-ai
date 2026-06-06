import pandas as pd

from cityfit.features.transformations import add_affordability_features


def calculate_cityfit_score(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    Calculate a personalized CityFit score.

    Uses transformed 0-100 feature scores so user priorities can meaningfully
    shift city rankings.
    """
    scored = add_affordability_features(df.copy())

    positive_score = (
        scored["qol_score"] * weights["numbeo_quality_of_life"]
        + scored["purchasing_power_score"] * weights["purchasing_power"]
        + scored["safety_score"] * weights["safety"]
        + scored["healthcare_score"] * weights["healthcare"]
        + scored["climate_score"] * weights["climate"]
    )

    negative_score = (
        scored["affordability_score"] * weights["cost_penalty"]
        + scored["housing_affordability_score"] * weights["housing_penalty"]
        + scored["low_pollution_score"] * weights["pollution_penalty"]
        + scored["low_traffic_score"] * weights["traffic_penalty"]
    )

    scored["cityfit_score"] = positive_score + negative_score

    return scored


def add_cityfit_rank(df: pd.DataFrame) -> pd.DataFrame:
    """Add rank columns for Numbeo baseline and personalized CityFit score."""
    ranked = df.copy()

    ranked["numbeo_qol_rank"] = ranked["numbeo_quality_of_life_index"].rank(
        ascending=False,
        method="min",
    )

    ranked["cityfit_rank"] = ranked["cityfit_score"].rank(
        ascending=False,
        method="min",
    )

    ranked["rank_difference"] = ranked["numbeo_qol_rank"] - ranked["cityfit_rank"]

    return ranked.sort_values("cityfit_rank").reset_index(drop=True)


def rank_cities(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Return the top N cities by CityFit score."""
    return (
        df.sort_values("cityfit_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )