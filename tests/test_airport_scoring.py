import pandas as pd

from cityfit.lifestyle.airport_scoring import (
    add_airport_importance_metrics,
    add_airport_scores,
    build_route_connectivity,
    combine_airport_score,
    haversine_distance_km,
    prepare_airports,
    score_airport_access,
    score_passenger_volume,
    score_route_connectivity,
)


def test_haversine_distance_returns_expected_city_airport_distance():
    distance = haversine_distance_km(
        40.7128,
        -74.0060,
        40.6413,
        -73.7781,
    )

    assert round(distance) == 21


def test_score_airport_access_prefers_large_airports():
    assert score_airport_access(0, "large_airport") == 100
    assert score_airport_access(20, "large_airport") == 94
    assert score_airport_access(20, "medium_airport") == 70
    assert score_airport_access(300, "large_airport") == 0
    assert score_airport_access(20, "small_airport") == 0


def test_route_and_passenger_scores_use_log_scale():
    assert round(score_route_connectivity(0), 1) == 0.0
    assert round(score_route_connectivity(220), 1) == 100.0
    assert round(score_passenger_volume(110_000_000), 1) == 100.0


def test_combine_airport_score_reweights_missing_passenger_volume():
    score_without_passengers = combine_airport_score(
        distance_score=90,
        connectivity_score=50,
        passenger_score=None,
    )
    score_with_passengers = combine_airport_score(
        distance_score=90,
        connectivity_score=50,
        passenger_score=100,
    )

    assert round(score_without_passengers, 1) == 69.8
    assert round(score_with_passengers, 1) == 76.8


def test_build_route_connectivity_counts_direct_destinations_and_airlines():
    routes_df = pd.DataFrame(
        [
            ["AA", "1", "JFK", "1", "LAX", "2", "", "0", "738"],
            ["DL", "2", "JFK", "1", "LAX", "2", "", "0", "320"],
            ["BA", "3", "JFK", "1", "LHR", "3", "", "0", "777"],
            ["AA", "1", "JFK", "1", "DFW", "4", "", "1", "738"],
        ]
    )

    connectivity = build_route_connectivity(routes_df)
    jfk = connectivity[connectivity["airport_code"] == "JFK"].iloc[0]

    assert jfk["route_count"] == 3
    assert jfk["direct_destination_count"] == 2
    assert jfk["airline_count"] == 3


def test_add_airport_importance_metrics_keeps_missing_routes_unknown():
    airports_df = pd.DataFrame(
        [
            {
                "name": "Missing Route Airport",
                "type": "large_airport",
                "latitude": 40.0,
                "longitude": -74.0,
                "iata_code": "AAA",
                "gps_code": "KAAA",
            }
        ]
    )
    route_connectivity_df = pd.DataFrame(
        [
            {
                "airport_code": "BBB",
                "route_count": 12,
                "direct_destination_count": 8,
                "airline_count": 3,
            }
        ]
    )

    airports = add_airport_importance_metrics(
        airports_df,
        route_connectivity_df=route_connectivity_df,
    )

    assert pd.isna(airports.loc[0, "route_count"])
    assert pd.isna(airports.loc[0, "direct_destination_count"])
    assert pd.isna(airports.loc[0, "airline_count"])


def test_prepare_airports_keeps_scheduled_medium_and_large_airports():
    airports_df = pd.DataFrame(
        [
            {
                "name": "Large Scheduled",
                "type": "large_airport",
                "latitude_deg": 1,
                "longitude_deg": 1,
                "scheduled_service": "yes",
            },
            {
                "name": "Medium Unscheduled",
                "type": "medium_airport",
                "latitude_deg": 2,
                "longitude_deg": 2,
                "scheduled_service": "no",
            },
            {
                "name": "Small Scheduled",
                "type": "small_airport",
                "latitude_deg": 3,
                "longitude_deg": 3,
                "scheduled_service": "yes",
            },
        ]
    )

    prepared = prepare_airports(airports_df)

    assert prepared["name"].tolist() == ["Large Scheduled"]


def test_add_airport_scores_does_not_penalize_missing_route_connectivity():
    cities_df = pd.DataFrame(
        [
            {
                "city": "Airport City",
                "country": "Example",
                "latitude": 40.0,
                "longitude": -74.0,
            }
        ]
    )
    airports_df = pd.DataFrame(
        [
            {
                "name": "Missing Route Airport",
                "type": "large_airport",
                "latitude_deg": 40.0,
                "longitude_deg": -74.0,
                "iata_code": "AAA",
                "gps_code": "KAAA",
                "scheduled_service": "yes",
            }
        ]
    )
    route_connectivity_df = pd.DataFrame(
        [
            {
                "airport_code": "BBB",
                "route_count": 12,
                "direct_destination_count": 8,
                "airline_count": 3,
            }
        ]
    )

    scored = add_airport_scores(
        cities_df,
        airports_df,
        route_connectivity_df=route_connectivity_df,
    )

    assert scored.loc[0, "airport_score"] == 100
    assert scored.loc[0, "airport_distance_score"] == 100
    assert pd.isna(scored.loc[0, "airport_connectivity_score"])
    assert pd.isna(scored.loc[0, "airport_direct_destination_count"])
    assert pd.isna(scored.loc[0, "airport_route_count"])


def test_add_airport_scores_scores_each_city():
    cities_df = pd.DataFrame(
        [
            {
                "city": "New York",
                "country": "United States",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
            {
                "city": "Remote",
                "country": "Example",
                "latitude": 0.0,
                "longitude": 0.0,
            },
        ]
    )
    airports_df = pd.DataFrame(
        [
            {
                "name": "John F Kennedy International Airport",
                "type": "large_airport",
                "latitude_deg": 40.6413,
                "longitude_deg": -73.7781,
                "iata_code": "JFK",
                "gps_code": "KJFK",
                "scheduled_service": "yes",
            }
        ]
    )
    route_connectivity_df = pd.DataFrame(
        [
            {
                "airport_code": "JFK",
                "route_count": 100,
                "direct_destination_count": 80,
                "airline_count": 20,
            }
        ]
    )
    passenger_volume_df = pd.DataFrame(
        [
            {
                "airport_code": "JFK",
                "annual_passengers": 62_000_000,
            }
        ]
    )

    scored = add_airport_scores(
        cities_df,
        airports_df,
        route_connectivity_df=route_connectivity_df,
        passenger_volume_df=passenger_volume_df,
    )

    assert scored.loc[0, "airport_score"] > 85
    assert scored.loc[0, "nearest_airport_name"] == (
        "John F Kennedy International Airport"
    )
    assert scored.loc[0, "airport_direct_destination_count"] == 80
    assert scored.loc[0, "airport_annual_passengers"] == 62_000_000
    assert scored.loc[1, "airport_score"] == 0
