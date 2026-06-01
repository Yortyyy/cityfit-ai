import pandas as pd

from cityfit.features.scoring import calculate_cityfit_score, add_cityfit_rank
from cityfit.features.user_profiles import REMOTE_WORKER_WEIGHTS


def test_calculate_cityfit_score_adds_score_column():
    df = pd.DataFrame(
        {
            "city": ["A", "B"],
            "country": ["X", "Y"],
            "numbeo_quality_of_life_index": [180, 150],
            "purchasing_power_index": [100, 80],
            "safety_index": [80, 60],
            "healthcare_index": [75, 70],
            "climate_index": [90, 70],
            "cost_of_living_index": [60, 90],
            "property_price_to_income_ratio": [8, 12],
            "pollution_index": [20, 50],
            "traffic_commute_index": [30, 45],
        }
    )

    scored = calculate_cityfit_score(df, REMOTE_WORKER_WEIGHTS)

    assert "cityfit_score" in scored.columns
    assert scored["cityfit_score"].notna().all()


def test_add_cityfit_rank_adds_rank_columns():
    df = pd.DataFrame(
        {
            "city": ["A", "B"],
            "country": ["X", "Y"],
            "numbeo_quality_of_life_index": [180, 150],
            "cityfit_score": [100, 80],
        }
    )

    ranked = add_cityfit_rank(df)

    assert "numbeo_qol_rank" in ranked.columns
    assert "cityfit_rank" in ranked.columns
    assert "rank_difference" in ranked.columns