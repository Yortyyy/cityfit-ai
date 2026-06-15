from cityfit.api.schemas import UserProfile

from cityfit.recommendations.service import get_ranked_cities


def test_get_ranked_cities_returns_region_filtered_results():
    profile = UserProfile(region="Asia", top_n=5)

    ranked_df = get_ranked_cities(profile)

    assert len(ranked_df) > 0
    assert all(ranked_df["region"] == "Asia")


def test_default_profile_matches_baseline_ranks_and_scores():
    profile = UserProfile(
        priority_purchasing_power=1.0,
        priority_low_cost=1.0,
        priority_safety=1.0,
        priority_healthcare=1.0,
        priority_housing=1.0,
        priority_low_traffic=1.0,
        priority_climate=1.0,
        priority_low_pollution=1.0,
        remote_worker=False,
        top_n=500,
    )

    ranked_df = get_ranked_cities(profile)

    assert (ranked_df["cityfit_score"] == ranked_df["baseline_cityfit_score"]).all()
    assert (ranked_df["cityfit_rank"] == ranked_df["baseline_cityfit_rank"]).all()
    assert (ranked_df["rank_difference"] == 0).all()
