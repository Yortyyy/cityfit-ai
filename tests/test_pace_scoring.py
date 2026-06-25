import pandas as pd

from cityfit.lifestyle.pace_scoring import (
    add_pace_of_life,
    calculate_pace_intensity_score,
    calculate_cultural_pace_baseline,
    classify_pace_of_life,
    score_traffic_pressure,
)


def test_score_traffic_pressure_scales_and_caps_commute_index():
    assert score_traffic_pressure(22) == 0.0
    assert score_traffic_pressure(55) == 100.0
    assert score_traffic_pressure(70) == 100.0
    assert 0 < score_traffic_pressure(35) < 100


def test_classify_pace_of_life_uses_preference_categories():
    assert classify_pace_of_life(30) == "slow"
    assert classify_pace_of_life(60) == "moderate"
    assert classify_pace_of_life(85) == "fast"


def test_calculate_cultural_pace_baseline_uses_country_and_city_context():
    florence = pd.Series(
        {
            "city": "Florence",
            "country": "Italy",
            "region": "Europe",
        }
    )
    milan = pd.Series(
        {
            "city": "Milan",
            "country": "Italy",
            "region": "Europe",
        }
    )
    seoul = pd.Series(
        {
            "city": "Seoul",
            "country": "South Korea",
            "region": "Asia",
        }
    )

    assert calculate_cultural_pace_baseline(florence) < 45
    assert calculate_cultural_pace_baseline(milan) > calculate_cultural_pace_baseline(
        florence
    )
    assert calculate_cultural_pace_baseline(seoul) > 75


def test_calculate_pace_intensity_weights_culture_more_than_city_activity():
    fast_row = pd.Series(
        {
            "cultural_pace_baseline": 78,
            "traffic_pressure_score": 100,
            "nightlife_score": 90,
        }
    )
    slow_row = pd.Series(
        {
            "cultural_pace_baseline": 35,
            "traffic_pressure_score": 100,
            "nightlife_score": 90,
        }
    )

    assert calculate_pace_intensity_score(fast_row) > 80
    assert calculate_pace_intensity_score(slow_row) < 55


def test_add_pace_of_life_merges_traffic_and_labels_cities():
    lifestyle_df = pd.DataFrame(
        [
            {
                "city": "Busy City",
                "country": "South Korea",
                "region": "Asia",
                "nightlife_score": 90,
            },
            {
                "city": "Florence",
                "country": "Italy",
                "region": "Europe",
                "nightlife_score": 90,
            },
        ]
    )
    city_features_df = pd.DataFrame(
        [
            {
                "city": "Busy City",
                "country": "South Korea",
                "traffic_commute_index": 60,
            },
            {
                "city": "Florence",
                "country": "Italy",
                "traffic_commute_index": 45,
            },
        ]
    )

    scored_df = add_pace_of_life(lifestyle_df, city_features_df)

    assert scored_df.loc[0, "pace_of_life"] == "fast"
    assert scored_df.loc[1, "pace_of_life"] == "slow"
