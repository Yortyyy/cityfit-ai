import pandas as pd

from cityfit.lifestyle.land_area import (
    DEFAULT_OSM_QUERY_RADIUS_METERS,
    MAX_LAND_DENSITY_MULTIPLIER,
    circle_area_km2,
    get_land_area_km2,
    normalize_count_for_land_area,
)


def test_circle_area_uses_query_radius():
    assert round(circle_area_km2(DEFAULT_OSM_QUERY_RADIUS_METERS), 1) == 201.1


def test_get_land_area_falls_back_to_full_circle_area():
    row = pd.Series({})

    assert round(get_land_area_km2(row), 1) == 201.1


def test_normalize_count_for_land_area_boosts_partial_land_radius():
    full_area = circle_area_km2()
    normalized_count = normalize_count_for_land_area(
        count=10,
        land_area_km2=full_area / 2,
    )

    assert round(normalized_count, 1) == 20.0


def test_normalize_count_for_land_area_caps_extreme_density_multiplier():
    normalized_count = normalize_count_for_land_area(
        count=10,
        land_area_km2=1,
    )

    assert normalized_count == 10 * MAX_LAND_DENSITY_MULTIPLIER
