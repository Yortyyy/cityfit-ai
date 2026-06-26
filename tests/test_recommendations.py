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
    assert (ranked_df["lifestyle_score"] == ranked_df["baseline_lifestyle_score"]).all()

def test_rank_difference_compares_personalized_rank_to_baseline_rank():
    profile = UserProfile(
        priority_purchasing_power=2.0,
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

    expected_rank_difference = (
        ranked_df["baseline_cityfit_rank"] - ranked_df["cityfit_rank"]
    )

    assert (ranked_df["rank_difference"] == expected_rank_difference).all()


def test_lifestyle_priorities_can_drive_lifestyle_only_cityfit_score():
    baseline_profile = UserProfile(top_n=500)
    outdoors_profile = UserProfile(
        priority_daily_life=0.0,
        priority_food_scene=0.0,
        priority_culture=0.0,
        priority_outdoors=2.0,
        priority_transit=0.0,
        priority_airport=0.0,
        priority_nightlife=0.0,
        priority_practical_fit=0.0,
        priority_lifestyle_fit=1.0,
        top_n=500,
    )

    baseline_df = get_ranked_cities(baseline_profile)
    outdoors_df = get_ranked_cities(outdoors_profile)
    merged_df = baseline_df[["city", "country", "lifestyle_score"]].merge(
        outdoors_df[["city", "country", "lifestyle_score", "outdoors_score"]],
        on=["city", "country"],
        suffixes=("_baseline", "_outdoors"),
    )

    assert (
        merged_df["lifestyle_score_outdoors"].round(1)
        == merged_df["outdoors_score"].round(1)
    ).all()
    assert (
        merged_df["lifestyle_score_baseline"]
        != merged_df["lifestyle_score_outdoors"]
    ).any()
    assert (
        outdoors_df["cityfit_score"].round(1)
        == outdoors_df["lifestyle_fit_score"].round(1)
    ).all()


def test_practical_fit_only_ignores_lifestyle_score_in_cityfit_score():
    practical_profile = UserProfile(
        priority_practical_fit=1.0,
        priority_lifestyle_fit=0.0,
        top_n=500,
    )

    ranked_df = get_ranked_cities(practical_profile)

    assert (
        ranked_df["cityfit_score"].round(1)
        == ranked_df["practical_score"].round(1)
    ).all()
