import pandas as pd

from cityfit.api.schemas import UserProfile
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.explanations import explain_city_rank
from cityfit.features.filters import filter_by_country, filter_by_region
from cityfit.features.scoring import add_cityfit_rank, calculate_cityfit_score, rank_cities
from cityfit.features.weights import build_weights

def get_ranked_cities(profile: UserProfile):
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    scored_df = calculate_cityfit_score(raw_df, build_weights(profile))
    ranked_df = add_cityfit_rank(scored_df)

    ranked_df = filter_by_region(ranked_df, profile.region)
    ranked_df = filter_by_country(ranked_df, profile.country)

    return ranked_df

def add_city_explanations(df: pd.DataFrame) -> pd.DataFrame:
    """Add human-readable explanation text for each city row."""
    explained_df = df.copy()
    explained_df["explanation"] = explained_df.apply(explain_city_rank, axis=1)

    return explained_df

def get_top_city_recommendations(profile: UserProfile) -> pd.DataFrame:
    """Return top ranked cities with explanations."""
    ranked_df = get_ranked_cities(profile)
    top_df = rank_cities(ranked_df, top_n=profile.top_n)

    return add_city_explanations(top_df)