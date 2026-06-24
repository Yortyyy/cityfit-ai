import pandas as pd

from cityfit.lifestyle.food_scene_scoring import (
    add_food_scene_scores,
    calculate_food_scene_score,
    score_food_count,
)


def test_score_food_count_uses_log_scale_and_caps_at_100():
    assert score_food_count(0, 10) == 0
    assert round(score_food_count(10, 10), 1) == 100.0
    assert round(score_food_count(100, 10), 1) == 100.0
    assert 0 < score_food_count(3, 10) < 100


def test_calculate_food_scene_score_weights_food_venues_most():
    restaurant_heavy = pd.Series(
        {
            "cafe_count": 2500,
            "grocery_count": 0,
        }
    )
    food_shop_heavy = pd.Series(
        {
            "cafe_count": 0,
            "grocery_count": 1800,
        }
    )

    assert calculate_food_scene_score(restaurant_heavy) > (
        calculate_food_scene_score(food_shop_heavy)
    )


def test_add_food_scene_scores_merges_counts_onto_cities():
    cities_df = pd.DataFrame(
        [
            {"city": "Food City", "country": "Example"},
            {"city": "Quiet City", "country": "Example"},
        ]
    )
    food_counts_df = pd.DataFrame(
        [
            {
                "city": "Food City",
                "country": "Example",
                "cafe_count": 20000,
                "grocery_count": 7000,
            },
            {
                "city": "Quiet City",
                "country": "Example",
                "cafe_count": 1,
                "grocery_count": 1,
            },
        ]
    )

    scored_df = add_food_scene_scores(cities_df, food_counts_df)

    assert scored_df.loc[0, "food_scene_score"] == 100.0
    assert scored_df.loc[1, "food_scene_score"] < 15.0
