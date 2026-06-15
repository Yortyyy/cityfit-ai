import pandas as pd

from cityfit.api.schemas import UserProfile
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.explanations import explain_city_rank
from cityfit.features.filters import filter_by_country, filter_by_region
from cityfit.features.scoring import calculate_cityfit_score, rank_cities
from cityfit.features.weights import build_weights

def get_ranked_cities(profile: UserProfile):
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    baseline_profile = UserProfile(
        priority_purchasing_power=1.0,
        priority_safety=1.0,
        priority_healthcare=1.0,
        priority_climate=1.0,
        priority_low_cost=1.0,
        priority_housing=1.0,
        priority_low_pollution=1.0,
        priority_low_traffic=1.0,
        remote_worker=False,
    )

    baseline_df = rank_cities(
        calculate_cityfit_score(raw_df, build_weights(baseline_profile))
    )

    personalized_df = rank_cities(
        calculate_cityfit_score(raw_df, build_weights(profile))
    )

    baseline_ranks = baseline_df[
        ["city", "country", "cityfit_rank", "cityfit_score"]
    ].rename(
        columns={
            "cityfit_rank": "baseline_cityfit_rank",
            "cityfit_score": "baseline_cityfit_score",
        }
    )

    ranked_df = personalized_df.merge(
        baseline_ranks,
        on=["city", "country"],
        how="left",
    )

    ranked_df["rank_difference"] = (
        ranked_df["baseline_cityfit_rank"] - ranked_df["cityfit_rank"]
    )

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
    top_df = ranked_df.head(profile.top_n).copy()

    return add_city_explanations(top_df)
