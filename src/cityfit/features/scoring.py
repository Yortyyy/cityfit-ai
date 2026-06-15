import pandas as pd

from cityfit.features.transformations import add_cityfit_features


def calculate_cityfit_score(
    df: pd.DataFrame,
    weights: dict,
    personalization_strength: float = 0.7,
) -> pd.DataFrame:
    """
    Calculate CityFit score.

    CityFit combines a source quality-of-life baseline with a weighted priority
    adjustment. The adjustment is normalized by total priority weight so
    default and personalized scores remain comparable.
    """
    global_score_scaler = 1.25

    scored = add_cityfit_features(df.copy())

    priority_features = {
        "purchasing_power": "purchasing_power_score",
        "affordability": "affordability_score",
        "safety": "safety_score",
        "healthcare": "healthcare_score",
        "housing_affordability": "housing_affordability_score",
        "low_traffic": "low_traffic_score",
        "climate": "climate_score",
        "low_pollution": "low_pollution_score",
    }

    total_weight = sum(
        weights.get(priority, 0)
        for priority in priority_features
    )

    if total_weight == 0:
        total_weight = 1

    weighted_priority_score = sum(
        scored[column] * weights.get(priority, 0)
        for priority, column in priority_features.items()
    ) / total_weight

    scored["personalization_adjustment"] = weighted_priority_score

    scored["cityfit_score"] = (
        scored["numbeo_quality_of_life_index"] * (1 - personalization_strength)
        + scored["personalization_adjustment"] * personalization_strength
    )

    scored["cityfit_score"] = (
        scored["cityfit_score"] * global_score_scaler
    ).round(1)

    return scored


def rank_cities(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.copy()

    ranked["cityfit_rank"] = (
        ranked["cityfit_score"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    return ranked.sort_values(
        ["cityfit_rank", "cityfit_score", "city", "country"],
        ascending=[True, False, True, True],
    ).reset_index(drop=True)