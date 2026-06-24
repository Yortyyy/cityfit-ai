import pandas as pd

from cityfit.lifestyle.outdoors_scoring import (
    add_outdoors_scores,
    calculate_outdoors_score,
    score_outdoors_count,
)


def test_score_outdoors_count_uses_log_scale_and_caps_at_100():
    assert score_outdoors_count(0, 10) == 0
    assert round(score_outdoors_count(10, 10), 1) == 100.0
    assert round(score_outdoors_count(100, 10), 1) == 100.0
    assert 0 < score_outdoors_count(3, 10) < 100


def test_calculate_outdoors_score_weights_multiple_outdoors_categories():
    row = pd.Series(
        {
            "park_green_count": 80,
            "nature_reserve_count": 50,
            "trail_route_count": 250,
            "beach_water_count": 30,
            "viewpoint_peak_count": 100,
        }
    )

    assert calculate_outdoors_score(row) == 100.0


def test_add_outdoors_scores_merges_counts_onto_cities():
    cities_df = pd.DataFrame(
        [
            {"city": "Outdoor City", "country": "Example"},
            {"city": "Paved City", "country": "Example"},
        ]
    )
    outdoors_counts_df = pd.DataFrame(
        [
            {
                "city": "Outdoor City",
                "country": "Example",
                "park_green_count": 80,
                "nature_reserve_count": 50,
                "trail_route_count": 250,
                "beach_water_count": 30,
                "viewpoint_peak_count": 100,
            },
            {
                "city": "Paved City",
                "country": "Example",
                "park_green_count": 1,
                "nature_reserve_count": 0,
                "trail_route_count": 0,
                "beach_water_count": 0,
                "viewpoint_peak_count": 0,
            },
        ]
    )

    scored_df = add_outdoors_scores(cities_df, outdoors_counts_df)

    assert scored_df.loc[0, "outdoors_score"] == 100.0
    assert scored_df.loc[1, "outdoors_score"] < 10.0
