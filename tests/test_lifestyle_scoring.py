import pandas as pd

from cityfit.lifestyle.lifestyle_scoring import (
    add_lifestyle_scores,
    calculate_lifestyle_score,
)


def test_calculate_lifestyle_score_uses_default_weights():
    row = pd.Series(
        {
            "daily_life_score": 100,
            "food_scene_score": 100,
            "culture_score": 100,
            "outdoors_score": 0,
            "transit_score": 0,
            "airport_score": 0,
            "nightlife_score": 0,
        }
    )

    assert calculate_lifestyle_score(row) == 50.0


def test_calculate_lifestyle_score_honors_priority_multipliers():
    row = pd.Series(
        {
            "daily_life_score": 100,
            "food_scene_score": 0,
            "culture_score": 0,
            "outdoors_score": 0,
            "transit_score": 0,
            "airport_score": 0,
            "nightlife_score": 0,
        }
    )

    default_score = calculate_lifestyle_score(row)
    personalized_score = calculate_lifestyle_score(
        row,
        priority_multipliers={
            "priority_daily_life": 2.0,
            "priority_food_scene": 0.0,
            "priority_culture": 0.0,
            "priority_outdoors": 0.0,
            "priority_transit": 0.0,
            "priority_airport": 0.0,
            "priority_nightlife": 0.0,
        },
    )

    assert personalized_score > default_score
    assert personalized_score == 100.0


def test_add_lifestyle_scores_fills_lifestyle_score_column():
    lifestyle_df = pd.DataFrame(
        [
            {
                "city": "Lifestyle City",
                "country": "Example",
                "daily_life_score": 80,
                "food_scene_score": 80,
                "culture_score": 80,
                "outdoors_score": 80,
                "transit_score": 80,
                "airport_score": 80,
                "nightlife_score": 80,
            }
        ]
    )

    scored_df = add_lifestyle_scores(lifestyle_df)

    assert scored_df.loc[0, "lifestyle_score"] == 80.0
