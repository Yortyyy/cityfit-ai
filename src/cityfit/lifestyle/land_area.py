from __future__ import annotations

import math

import pandas as pd


DEFAULT_OSM_QUERY_RADIUS_METERS = 8_000
MIN_LAND_AREA_KM2 = 1.0
MAX_LAND_DENSITY_MULTIPLIER = 4.0


def circle_area_km2(radius_meters: int | float = DEFAULT_OSM_QUERY_RADIUS_METERS) -> float:
    radius_km = max(float(radius_meters), 0.0) / 1000.0

    return math.pi * radius_km**2


def get_land_area_km2(
    row: pd.Series,
    radius_meters: int | float = DEFAULT_OSM_QUERY_RADIUS_METERS,
) -> float:
    fallback_area = circle_area_km2(radius_meters)

    if "land_area_km2" not in row or pd.isna(row["land_area_km2"]):
        return fallback_area

    return max(float(row["land_area_km2"]), MIN_LAND_AREA_KM2)


def normalize_count_for_land_area(
    count: int | float,
    land_area_km2: int | float | None,
    radius_meters: int | float = DEFAULT_OSM_QUERY_RADIUS_METERS,
) -> float:
    count = max(float(count), 0.0)

    if land_area_km2 is None or pd.isna(land_area_km2):
        return count

    reference_area = circle_area_km2(radius_meters)
    usable_land_area = max(float(land_area_km2), MIN_LAND_AREA_KM2)
    density_multiplier = min(
        reference_area / usable_land_area,
        MAX_LAND_DENSITY_MULTIPLIER,
    )

    return count * density_multiplier
