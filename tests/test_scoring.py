import pandas as pd

from cityfit.features.scoring import (
    add_cityfit_rank,
    calculate_cityfit_score,
    rank_cities,
)
from cityfit.features.user_profiles import REMOTE_WORKER_WEIGHTS


def make_scoring_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["A", "B", "C"],
            "country": ["X", "Y", "Z"],
            "numbeo_quality_of_life_index": [180.0, 150.0, 120.0],
            "purchasing_power_index": [100.0, 80.0, 60.0],
            "safety_index": [80.0, 60.0, 40.0],
            "healthcare_index": [75.0, 70.0, 55.0],
            "climate_index": [90.0, 70.0, 60.0],
            "cost_of_living_index": [60.0, 90.0, 100.0],
            "property_price_to_income_ratio": [8.0, 12.0, 15.0],
            "pollution_index": [20.0, 50.0, 70.0],
            "traffic_commute_index": [30.0, 45.0, 60.0],
        }
    )


def test_calculate_cityfit_score_adds_score_column():
    df = make_scoring_df()

    scored = calculate_cityfit_score(df, REMOTE_WORKER_WEIGHTS)

    assert "cityfit_score" in scored.columns
    assert scored["cityfit_score"].notna().all()


def test_add_cityfit_rank_adds_rank_columns():
    df = make_scoring_df()
    scored = calculate_cityfit_score(df, REMOTE_WORKER_WEIGHTS)

    ranked = add_cityfit_rank(scored)

    assert "numbeo_qol_rank" in ranked.columns
    assert "cityfit_rank" in ranked.columns
    assert "rank_difference" in ranked.columns


def test_rank_cities_returns_top_n_sorted_by_cityfit_score():
    df = make_scoring_df()
    scored = calculate_cityfit_score(df, REMOTE_WORKER_WEIGHTS)

    top = rank_cities(scored, top_n=2)

    assert len(top) == 2
    assert top["cityfit_score"].iloc[0] >= top["cityfit_score"].iloc[1]