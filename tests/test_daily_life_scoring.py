import pandas as pd

from cityfit.lifestyle.daily_life_scoring import (
    add_daily_life_scores,
    calculate_daily_life_score,
    score_category_count,
)


def test_score_category_count_uses_log_scale_and_caps_at_100():
    assert score_category_count(0, 10) == 0
    assert round(score_category_count(10, 10), 1) == 100.0
    assert round(score_category_count(100, 10), 1) == 100.0
    assert 0 < score_category_count(3, 10) < 100


def test_calculate_daily_life_score_weights_amenity_categories():
    row = pd.Series(
        {
            "grocery_count": 35,
            "pharmacy_count": 300,
            "cafe_count": 2000,
            "fitness_count": 120,
            "park_count": 80,
            "basic_services_count": 600,
            "healthcare_essentials_count": 500,
        }
    )

    assert calculate_daily_life_score(row) < 100.0


def test_add_daily_life_scores_merges_counts_onto_cities():
    cities_df = pd.DataFrame(
        [
            {"city": "Walkable", "country": "Example"},
            {"city": "Sparse", "country": "Example"},
        ]
    )
    amenity_counts_df = pd.DataFrame(
        [
            {
                "city": "Walkable",
                "country": "Example",
                "grocery_count": 1500,
                "pharmacy_count": 300,
                "cafe_count": 2000,
                "fitness_count": 120,
                "park_count": 80,
                "basic_services_count": 600,
                "healthcare_essentials_count": 500,
            },
            {
                "city": "Sparse",
                "country": "Example",
                "grocery_count": 1,
                "pharmacy_count": 0,
                "cafe_count": 1,
                "fitness_count": 0,
                "park_count": 1,
                "basic_services_count": 0,
                "healthcare_essentials_count": 0,
            },
        ]
    )

    scored_df = add_daily_life_scores(cities_df, amenity_counts_df)

    assert scored_df.loc[0, "daily_life_score"] == 100.0
    assert scored_df.loc[1, "daily_life_score"] < 25.0
