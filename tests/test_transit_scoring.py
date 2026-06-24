import pandas as pd

from cityfit.lifestyle.transit_scoring import (
    add_transit_scores,
    calculate_transit_score,
    score_transit_count,
)


def test_score_transit_count_uses_log_scale_and_caps_at_100():
    assert score_transit_count(0, 10) == 0
    assert round(score_transit_count(10, 10), 1) == 100.0
    assert round(score_transit_count(100, 10), 1) == 100.0
    assert 0 < score_transit_count(3, 10) < 100


def test_calculate_transit_score_weights_multiple_transit_modes():
    row = pd.Series(
        {
            "bus_stop_count": 2000,
            "rail_station_count": 250,
            "metro_tram_count": 400,
            "ferry_aerialway_count": 40,
            "transport_hub_count": 80,
        }
    )

    assert calculate_transit_score(row) == 100.0


def test_add_transit_scores_merges_counts_onto_cities():
    cities_df = pd.DataFrame(
        [
            {"city": "Transit City", "country": "Example"},
            {"city": "Car City", "country": "Example"},
        ]
    )
    transit_counts_df = pd.DataFrame(
        [
            {
                "city": "Transit City",
                "country": "Example",
                "bus_stop_count": 2000,
                "rail_station_count": 250,
                "metro_tram_count": 400,
                "ferry_aerialway_count": 40,
                "transport_hub_count": 80,
            },
            {
                "city": "Car City",
                "country": "Example",
                "bus_stop_count": 1,
                "rail_station_count": 0,
                "metro_tram_count": 0,
                "ferry_aerialway_count": 0,
                "transport_hub_count": 0,
            },
        ]
    )

    scored_df = add_transit_scores(cities_df, transit_counts_df)

    assert scored_df.loc[0, "transit_score"] == 100.0
    assert scored_df.loc[1, "transit_score"] < 10.0
