import re

import pandas as pd

from cityfit.api.schemas import UserProfile
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.explanations import explain_city_rank
from cityfit.features.scoring import add_cityfit_rank, calculate_cityfit_score, rank_cities
from cityfit.features.transformations import add_affordability_features
from cityfit.features.weights import build_weights


def get_ranked_city_data(profile: UserProfile) -> pd.DataFrame:
    """Load, validate, score, and rank city data for a user profile."""
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    features_df = add_affordability_features(raw_df)
    scored_df = calculate_cityfit_score(features_df, build_weights(profile))
    ranked_df = add_cityfit_rank(scored_df)

    ranked_df["explanation"] = ranked_df.apply(explain_city_rank, axis=1)

    return ranked_df


def rank_city_recommendations(profile: UserProfile, top_n: int = 10) -> list[dict]:
    """Return top ranked city recommendations."""
    ranked_df = get_ranked_city_data(profile)
    top_df = rank_cities(ranked_df, top_n=top_n)

    return top_df.to_dict(orient="records")


def get_city_metrics(city: str, profile: UserProfile) -> dict | None:
    """Return one city's scored metrics."""
    ranked_df = get_ranked_city_data(profile)

    match = ranked_df[ranked_df["city"].str.lower() == city.lower()]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def compare_cities(cities: list[str], profile: UserProfile) -> list[dict]:
    """Return scored metrics for selected cities."""
    ranked_df = get_ranked_city_data(profile)

    normalized_cities = {city.lower() for city in cities}

    comparison_df = ranked_df[
        ranked_df["city"].str.lower().isin(normalized_cities)
    ].sort_values("cityfit_rank")

    return comparison_df.to_dict(orient="records")


def extract_city_names(question: str, available_cities: list[str]) -> list[str]:
    """
    Simple city extraction from the user's question.

    This is intentionally deterministic for now. Later, an LLM or structured parser
    can replace this.
    """
    found_cities = []

    question_lower = question.lower()

    for city in available_cities:
        pattern = r"\b" + re.escape(city.lower()) + r"\b"

        if re.search(pattern, question_lower):
            found_cities.append(city)

    return found_cities


def get_available_cities() -> list[str]:
    """Return all available city names."""
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    return sorted(raw_df["city"].dropna().unique().tolist())