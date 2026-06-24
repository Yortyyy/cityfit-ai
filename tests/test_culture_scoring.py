import pandas as pd

from cityfit.lifestyle.culture_scoring import (
    add_culture_scores,
    calculate_culture_score,
    score_culture_count,
)


def test_score_culture_count_uses_log_scale_and_caps_at_100():
    assert score_culture_count(0, 10) == 0
    assert round(score_culture_count(10, 10), 1) == 100.0
    assert round(score_culture_count(100, 10), 1) == 100.0
    assert 0 < score_culture_count(3, 10) < 100


def test_calculate_culture_score_weights_multiple_culture_categories():
    row = pd.Series(
        {
            "museum_count": 180,
            "performing_arts_count": 135,
            "gallery_artwork_count": 450,
            "cinema_count": 90,
            "historic_count": 900,
        }
    )

    assert calculate_culture_score(row) == 100.0


def test_add_culture_scores_merges_counts_onto_cities():
    cities_df = pd.DataFrame(
        [
            {"city": "Culture City", "country": "Example"},
            {"city": "Quiet City", "country": "Example"},
        ]
    )
    culture_counts_df = pd.DataFrame(
        [
            {
                "city": "Culture City",
                "country": "Example",
                "museum_count": 180,
                "performing_arts_count": 135,
                "gallery_artwork_count": 450,
                "cinema_count": 90,
                "historic_count": 900,
            },
            {
                "city": "Quiet City",
                "country": "Example",
                "museum_count": 0,
                "performing_arts_count": 1,
                "gallery_artwork_count": 0,
                "cinema_count": 0,
                "historic_count": 1,
            },
        ]
    )

    scored_df = add_culture_scores(cities_df, culture_counts_df)

    assert scored_df.loc[0, "culture_score"] == 100.0
    assert scored_df.loc[1, "culture_score"] < 15.0
