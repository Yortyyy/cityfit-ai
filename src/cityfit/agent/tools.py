import re

import pandas as pd

from cityfit.api.schemas import UserProfile
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.filters import filter_by_country, filter_by_region
from cityfit.features.scoring import rank_cities
from cityfit.recommendations.service import add_city_explanations, get_ranked_cities


def get_ranked_city_data(profile: UserProfile) -> pd.DataFrame:
    """Return ranked city data with explanations for a user profile."""
    ranked_df = get_ranked_cities(profile)

    return add_city_explanations(ranked_df)


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
    """Return scored metrics for selected cities in the same order requested."""
    ranked_df = get_ranked_city_data(profile)

    requested_order = {city.lower(): index for index, city in enumerate(cities)}

    comparison_df = ranked_df[
        ranked_df["city"].str.lower().isin(requested_order.keys())
    ].copy()

    comparison_df["requested_order"] = (
        comparison_df["city"].str.lower().map(requested_order)
    )

    comparison_df = comparison_df.sort_values("requested_order")

    return comparison_df.drop(columns=["requested_order"]).to_dict(orient="records")


def extract_city_names(question: str, available_cities: list[str]) -> list[str]:
    """Extract city names in the order they appear in the question."""
    matches = []
    question_lower = question.lower()

    for city in available_cities:
        pattern = r"\b" + re.escape(city.lower()) + r"\b"
        match = re.search(pattern, question_lower)

        if match:
            matches.append((match.start(), city))

    return [city for _, city in sorted(matches)]


def get_available_cities(profile: UserProfile | None = None) -> list[str]:
    """Return available city names, optionally filtered by profile."""
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    if profile:
        raw_df = filter_by_region(raw_df, profile.region)
        raw_df = filter_by_country(raw_df, profile.country)

    return sorted(raw_df["city"].dropna().unique().tolist())