import pandas as pd

from cityfit.lifestyle.nightlife_scoring import (
    add_nightlife_scores,
    calculate_nightlife_score,
    score_nightlife_count,
)


def test_score_nightlife_count_uses_log_scale_and_caps_at_100():
    assert score_nightlife_count(0, 10) == 0
    assert round(score_nightlife_count(10, 10), 1) == 100.0
    assert round(score_nightlife_count(100, 10), 1) == 100.0
    assert 0 < score_nightlife_count(3, 10) < 100


def test_calculate_nightlife_score_weights_multiple_nightlife_categories():
    row = pd.Series(
        {
            "bar_pub_count": 900,
            "club_count": 120,
            "music_venue_count": 160,
            "late_entertainment_count": 80,
        }
    )

    assert calculate_nightlife_score(row) == 100.0


def test_add_nightlife_scores_merges_counts_onto_cities():
    cities_df = pd.DataFrame(
        [
            {"city": "Night City", "country": "Example"},
            {"city": "Sleepy City", "country": "Example"},
        ]
    )
    nightlife_counts_df = pd.DataFrame(
        [
            {
                "city": "Night City",
                "country": "Example",
                "bar_pub_count": 900,
                "club_count": 120,
                "music_venue_count": 160,
                "late_entertainment_count": 80,
            },
            {
                "city": "Sleepy City",
                "country": "Example",
                "bar_pub_count": 1,
                "club_count": 0,
                "music_venue_count": 0,
                "late_entertainment_count": 0,
            },
        ]
    )

    scored_df = add_nightlife_scores(cities_df, nightlife_counts_df)

    assert scored_df.loc[0, "nightlife_score"] == 100.0
    assert scored_df.loc[1, "nightlife_score"] < 10.0
