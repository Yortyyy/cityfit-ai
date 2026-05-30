import pandas as pd


def calculate_cityfit_score(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    Calculate a personalized CityFit score.

    Numbeo's Quality of Life Index is treated as the baseline.
    CityFit adjusts that score based on personalized priorities.
    """
    scored = df.copy()

    positive_score = (
        scored["numbeo_quality_of_life_index"] * weights["numbeo_quality_of_life"]
        + scored["purchasing_power_index"] * weights["purchasing_power"]
        + scored["safety_index"] * weights["safety"]
        + scored["healthcare_index"] * weights["healthcare"]
        + scored["climate_index"] * weights["climate"]
    )

    negative_score = (
        scored["cost_of_living_index"] * weights["cost_penalty"]
        + scored["property_price_to_income_ratio"] * weights["housing_penalty"]
        + scored["pollution_index"] * weights["pollution_penalty"]
        + scored["traffic_commute_index"] * weights["traffic_penalty"]
    )

    scored["cityfit_score"] = positive_score - negative_score

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