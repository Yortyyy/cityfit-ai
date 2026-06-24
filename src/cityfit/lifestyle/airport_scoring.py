from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

import numpy as np
import pandas as pd


EARTH_RADIUS_KM = 6371.0

SUPPORTED_AIRPORT_TYPES = {
    "large_airport": {
        "distance_score_anchors": [
            (0.0, 100.0),
            (15.0, 96.0),
            (30.0, 90.0),
            (60.0, 78.0),
            (100.0, 62.0),
            (160.0, 38.0),
            (260.0, 0.0),
        ],
    },
    "medium_airport": {
        "distance_score_anchors": [
            (0.0, 75.0),
            (15.0, 72.0),
            (30.0, 66.0),
            (60.0, 50.0),
            (100.0, 28.0),
            (160.0, 0.0),
        ],
    },
}


@dataclass(frozen=True)
class NearestAirportScore:
    airport_score: float
    nearest_airport_name: str | None
    nearest_airport_type: str | None
    nearest_airport_distance_km: float | None
    airport_distance_score: float | None
    airport_connectivity_score: float | None
    airport_passenger_score: float | None
    airport_direct_destination_count: int | None
    airport_route_count: int | None
    airport_annual_passengers: int | None


def _clean_code(value: object) -> str | None:
    if pd.isna(value):
        return None

    code = str(value).strip().upper()

    if not code or code == "\\N":
        return None

    return code


def haversine_distance_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    latitude_delta = radians(latitude_b - latitude_a)
    longitude_delta = radians(longitude_b - longitude_a)
    latitude_a_rad = radians(latitude_a)
    latitude_b_rad = radians(latitude_b)

    value = (
        sin(latitude_delta / 2) ** 2
        + cos(latitude_a_rad) * cos(latitude_b_rad) * sin(longitude_delta / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * asin(sqrt(value))


def score_airport_access(distance_km: float, airport_type: str) -> float:
    if airport_type not in SUPPORTED_AIRPORT_TYPES:
        return 0.0

    anchors = SUPPORTED_AIRPORT_TYPES[airport_type]["distance_score_anchors"]

    if distance_km <= anchors[0][0]:
        return anchors[0][1]

    for index in range(1, len(anchors)):
        previous_distance, previous_score = anchors[index - 1]
        next_distance, next_score = anchors[index]

        if distance_km <= next_distance:
            distance_share = (distance_km - previous_distance) / (
                next_distance - previous_distance
            )

            return previous_score + distance_share * (next_score - previous_score)

    return anchors[-1][1]


def score_route_connectivity(direct_destination_count: int | float | None) -> float | None:
    if direct_destination_count is None or pd.isna(direct_destination_count):
        return None

    direct_destination_count = max(float(direct_destination_count), 0.0)

    return min(
        np.log1p(direct_destination_count) / np.log1p(220.0) * 100.0,
        100.0,
    )


def score_passenger_volume(annual_passengers: int | float | None) -> float | None:
    if annual_passengers is None or pd.isna(annual_passengers):
        return None

    annual_passengers = max(float(annual_passengers), 0.0)

    return min(
        np.log1p(annual_passengers) / np.log1p(110_000_000.0) * 100.0,
        100.0,
    )


def _optional_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None

    return int(value)


def combine_airport_score(
    distance_score: float,
    connectivity_score: float | None,
    passenger_score: float | None,
) -> float:
    importance_components = []

    if connectivity_score is not None:
        importance_components.append((connectivity_score, 0.65))

    if passenger_score is not None:
        importance_components.append((passenger_score, 0.35))

    if not importance_components:
        return distance_score

    total_weight = sum(weight for _, weight in importance_components)
    importance_score = (
        sum(score * weight for score, weight in importance_components) / total_weight
    )

    return distance_score * (0.55 + 0.45 * importance_score / 100.0)


def build_route_connectivity(routes_df: pd.DataFrame) -> pd.DataFrame:
    route_columns = [
        "airline",
        "airline_id",
        "source_airport_code",
        "source_airport_id",
        "destination_airport_code",
        "destination_airport_id",
        "codeshare",
        "stops",
        "equipment",
    ]

    routes = routes_df.copy()

    if list(routes.columns) != route_columns:
        routes.columns = route_columns[: len(routes.columns)]

    required_columns = {
        "airline",
        "source_airport_code",
        "destination_airport_code",
        "stops",
    }
    missing_columns = required_columns - set(routes.columns)

    if missing_columns:
        raise ValueError(f"Route data is missing columns: {sorted(missing_columns)}")

    routes["source_airport_code"] = routes["source_airport_code"].map(_clean_code)
    routes["destination_airport_code"] = routes["destination_airport_code"].map(
        _clean_code
    )
    routes["airline"] = routes["airline"].map(_clean_code)
    routes["stops"] = pd.to_numeric(routes["stops"], errors="coerce").fillna(0)
    routes = routes[
        routes["source_airport_code"].notna()
        & routes["destination_airport_code"].notna()
        & (routes["stops"] == 0)
    ].copy()

    connectivity = (
        routes.groupby("source_airport_code")
        .agg(
            route_count=("destination_airport_code", "size"),
            direct_destination_count=("destination_airport_code", "nunique"),
            airline_count=("airline", "nunique"),
        )
        .reset_index()
        .rename(columns={"source_airport_code": "airport_code"})
    )

    return connectivity


def prepare_airports(airports_df: pd.DataFrame) -> pd.DataFrame:
    airports = airports_df.rename(
        columns={
            "latitude_deg": "latitude",
            "longitude_deg": "longitude",
        }
    ).copy()

    required_columns = {"name", "type", "latitude", "longitude"}
    missing_columns = required_columns - set(airports.columns)

    if missing_columns:
        raise ValueError(f"Airport data is missing columns: {sorted(missing_columns)}")

    airports = airports[airports["type"].isin(SUPPORTED_AIRPORT_TYPES)].copy()
    airports["latitude"] = pd.to_numeric(airports["latitude"], errors="coerce")
    airports["longitude"] = pd.to_numeric(airports["longitude"], errors="coerce")
    airports = airports.dropna(subset=["latitude", "longitude"])
    airports["iata_code"] = airports.get("iata_code", pd.Series(index=airports.index)).map(
        _clean_code
    )
    airports["gps_code"] = airports.get("gps_code", pd.Series(index=airports.index)).map(
        _clean_code
    )

    return airports.reset_index(drop=True)


def add_airport_importance_metrics(
    airports_df: pd.DataFrame,
    route_connectivity_df: pd.DataFrame | None = None,
    passenger_volume_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    airports = airports_df.copy()
    airports["route_count"] = pd.NA
    airports["direct_destination_count"] = pd.NA
    airports["airline_count"] = pd.NA
    airports["annual_passengers"] = pd.NA

    for code_column in ["iata_code", "gps_code"]:
        if code_column not in airports.columns:
            airports[code_column] = pd.NA

    if route_connectivity_df is not None and not route_connectivity_df.empty:
        connectivity = route_connectivity_df.copy()
        required_columns = {
            "airport_code",
            "route_count",
            "direct_destination_count",
            "airline_count",
        }
        missing_columns = required_columns - set(connectivity.columns)

        if missing_columns:
            raise ValueError(
                "Route connectivity data is missing columns: "
                f"{sorted(missing_columns)}"
            )

        for code_column in ["iata_code", "gps_code"]:
            airports = airports.merge(
                connectivity,
                left_on=code_column,
                right_on="airport_code",
                how="left",
                suffixes=("", f"_{code_column}"),
            )

            for metric in [
                "route_count",
                "direct_destination_count",
                "airline_count",
            ]:
                airports[metric] = airports[metric].where(
                    airports[metric].notna(),
                    airports[f"{metric}_{code_column}"],
                )

            airports = airports.drop(
                columns=[
                    "airport_code",
                    f"route_count_{code_column}",
                    f"direct_destination_count_{code_column}",
                    f"airline_count_{code_column}",
                ],
                errors="ignore",
            )

    if passenger_volume_df is not None and not passenger_volume_df.empty:
        passenger_volume = passenger_volume_df.copy()
        required_columns = {"airport_code", "annual_passengers"}
        missing_columns = required_columns - set(passenger_volume.columns)

        if missing_columns:
            raise ValueError(
                "Passenger volume data is missing columns: "
                f"{sorted(missing_columns)}"
            )

        passenger_volume["airport_code"] = passenger_volume["airport_code"].map(
            _clean_code
        )
        passenger_volume["annual_passengers"] = pd.to_numeric(
            passenger_volume["annual_passengers"],
            errors="coerce",
        )
        passenger_volume = passenger_volume.dropna(
            subset=["airport_code", "annual_passengers"]
        )

        for code_column in ["iata_code", "gps_code"]:
            airports = airports.merge(
                passenger_volume[["airport_code", "annual_passengers"]],
                left_on=code_column,
                right_on="airport_code",
                how="left",
                suffixes=("", f"_{code_column}"),
            )
            airports["annual_passengers"] = airports["annual_passengers"].where(
                airports["annual_passengers"].notna(),
                airports[f"annual_passengers_{code_column}"],
            )
            airports = airports.drop(
                columns=["airport_code", f"annual_passengers_{code_column}"],
                errors="ignore",
            )

    numeric_columns = [
        "route_count",
        "direct_destination_count",
        "airline_count",
        "annual_passengers",
    ]
    for column in numeric_columns:
        airports[column] = pd.to_numeric(airports[column], errors="coerce")

    if "scheduled_service" in airports.columns:
        airports = airports[
            (airports["scheduled_service"].fillna("no") == "yes")
            | (airports["direct_destination_count"] > 0)
            | airports["annual_passengers"].notna()
        ].copy()

    return airports


def score_city_airport_access(
    city_latitude: float,
    city_longitude: float,
    airports_df: pd.DataFrame,
) -> NearestAirportScore:
    best_score = 0.0
    nearest_name = None
    nearest_type = None
    nearest_distance = None
    best_distance_score = None
    best_connectivity_score = None
    best_passenger_score = None
    best_direct_destination_count = None
    best_route_count = None
    best_annual_passengers = None

    for airport in airports_df.itertuples(index=False):
        distance_km = haversine_distance_km(
            city_latitude,
            city_longitude,
            float(airport.latitude),
            float(airport.longitude),
        )
        distance_score = score_airport_access(distance_km, str(airport.type))
        connectivity_score = score_route_connectivity(
            getattr(airport, "direct_destination_count", None)
        )
        passenger_score = score_passenger_volume(
            getattr(airport, "annual_passengers", None)
        )
        score = combine_airport_score(
            distance_score,
            connectivity_score,
            passenger_score,
        )

        if score > best_score:
            best_score = score
            nearest_name = str(airport.name)
            nearest_type = str(airport.type)
            nearest_distance = distance_km
            best_distance_score = distance_score
            best_connectivity_score = connectivity_score
            best_passenger_score = passenger_score
            best_direct_destination_count = _optional_int(
                getattr(airport, "direct_destination_count", None)
            )
            best_route_count = _optional_int(getattr(airport, "route_count", None))
            best_annual_passengers = _optional_int(
                getattr(airport, "annual_passengers", None)
            )

    return NearestAirportScore(
        airport_score=round(best_score, 1),
        nearest_airport_name=nearest_name,
        nearest_airport_type=nearest_type,
        nearest_airport_distance_km=(
            round(nearest_distance, 1) if nearest_distance is not None else None
        ),
        airport_distance_score=(
            round(best_distance_score, 1) if best_distance_score is not None else None
        ),
        airport_connectivity_score=(
            round(best_connectivity_score, 1)
            if best_connectivity_score is not None
            else None
        ),
        airport_passenger_score=(
            round(best_passenger_score, 1) if best_passenger_score is not None else None
        ),
        airport_direct_destination_count=best_direct_destination_count,
        airport_route_count=best_route_count,
        airport_annual_passengers=best_annual_passengers,
    )


def add_airport_scores(
    cities_df: pd.DataFrame,
    airports_df: pd.DataFrame,
    route_connectivity_df: pd.DataFrame | None = None,
    passenger_volume_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    required_city_columns = {"city", "country", "latitude", "longitude"}
    missing_city_columns = required_city_columns - set(cities_df.columns)

    if missing_city_columns:
        raise ValueError(
            f"City data is missing columns: {sorted(missing_city_columns)}"
        )

    airports = add_airport_importance_metrics(
        prepare_airports(airports_df),
        route_connectivity_df=route_connectivity_df,
        passenger_volume_df=passenger_volume_df,
    )
    scored_cities = cities_df.copy()

    scores = [
        score_city_airport_access(
            float(city.latitude),
            float(city.longitude),
            airports,
        )
        for city in scored_cities.itertuples(index=False)
    ]

    scored_cities["airport_score"] = [score.airport_score for score in scores]
    scored_cities["nearest_airport_name"] = [
        score.nearest_airport_name for score in scores
    ]
    scored_cities["nearest_airport_type"] = [
        score.nearest_airport_type for score in scores
    ]
    scored_cities["nearest_airport_distance_km"] = [
        score.nearest_airport_distance_km for score in scores
    ]
    scored_cities["airport_distance_score"] = [
        score.airport_distance_score for score in scores
    ]
    scored_cities["airport_connectivity_score"] = [
        score.airport_connectivity_score for score in scores
    ]
    scored_cities["airport_passenger_score"] = [
        score.airport_passenger_score for score in scores
    ]
    scored_cities["airport_direct_destination_count"] = [
        score.airport_direct_destination_count for score in scores
    ]
    scored_cities["airport_route_count"] = [
        score.airport_route_count for score in scores
    ]
    scored_cities["airport_annual_passengers"] = [
        score.airport_annual_passengers for score in scores
    ]

    return scored_cities
