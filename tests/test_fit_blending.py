import pandas as pd

from cityfit.features.fit_blending import (
    calculate_blended_cityfit_score,
    scale_lifestyle_score_to_cityfit_scale,
)


def test_scale_lifestyle_score_to_cityfit_scale_sets_median_near_100():
    scores = pd.Series([40, 60, 70, 80, 90])
    scaled_scores = scale_lifestyle_score_to_cityfit_scale(scores)

    assert scaled_scores.iloc[2] == 100.0
    assert scaled_scores.iloc[0] < 100.0
    assert scaled_scores.iloc[-1] > 100.0


def test_calculate_blended_cityfit_score_uses_old_cityfit_scale_layers():
    df = pd.DataFrame(
        [
            {"city": "Practical City", "practical_score": 200, "lifestyle_score": 40},
            {"city": "Lifestyle City", "practical_score": 100, "lifestyle_score": 90},
        ]
    )

    scored_df = calculate_blended_cityfit_score(df)

    assert "lifestyle_fit_score" in scored_df.columns
    expected_scores = (
        scored_df["practical_score"] + scored_df["lifestyle_fit_score"]
    ) / 2

    assert (
        scored_df["cityfit_score"].round(1)
        == expected_scores.round(1)
    ).all()


def test_calculate_blended_cityfit_score_supports_lifestyle_only():
    df = pd.DataFrame(
        [
            {"city": "A", "practical_score": 200, "lifestyle_score": 40},
            {"city": "B", "practical_score": 100, "lifestyle_score": 90},
        ]
    )

    scored_df = calculate_blended_cityfit_score(
        df,
        practical_fit_weight=0,
        lifestyle_fit_weight=1,
    )

    assert (
        scored_df["cityfit_score"].round(1)
        == scored_df["lifestyle_fit_score"].round(1)
    ).all()


def test_calculate_blended_cityfit_score_supports_practical_only():
    df = pd.DataFrame(
        [
            {"city": "A", "practical_score": 200, "lifestyle_score": 40},
            {"city": "B", "practical_score": 100, "lifestyle_score": 90},
        ]
    )

    scored_df = calculate_blended_cityfit_score(
        df,
        practical_fit_weight=1,
        lifestyle_fit_weight=0,
    )

    assert scored_df["cityfit_score"].tolist() == [200.0, 100.0]


def test_calculate_blended_cityfit_score_falls_back_to_practical_if_both_weights_zero():
    df = pd.DataFrame(
        [
            {"city": "A", "practical_score": 200, "lifestyle_score": 40},
            {"city": "B", "practical_score": 100, "lifestyle_score": 90},
        ]
    )

    scored_df = calculate_blended_cityfit_score(
        df,
        practical_fit_weight=0,
        lifestyle_fit_weight=0,
    )

    assert scored_df["cityfit_score"].tolist() == [200.0, 100.0]
