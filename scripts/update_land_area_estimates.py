from __future__ import annotations

import argparse
import json
import math
import urllib.request
from pathlib import Path
from typing import Iterable

import pandas as pd

from cityfit.lifestyle.land_area import (
    DEFAULT_OSM_QUERY_RADIUS_METERS,
    circle_area_km2,
)


CITY_COORDINATES_PATH = Path("data/reference/city_coordinates.csv")
LAND_GEOJSON_PATH = Path("data/reference/ne_10m_land.geojson")
LAND_AREA_ESTIMATES_PATH = Path("data/reference/city_land_area_estimates.csv")
LAND_GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_10m_land.geojson"
)
OSM_COUNT_CACHE_PATHS = [
    Path("data/reference/osm_daily_life_counts.csv"),
    Path("data/reference/osm_culture_counts.csv"),
    Path("data/reference/osm_transit_counts.csv"),
    Path("data/reference/osm_outdoors_counts.csv"),
    Path("data/reference/osm_nightlife_counts.csv"),
]


def download_land_geojson(
    output_path: Path = LAND_GEOJSON_PATH,
    source_url: str = LAND_GEOJSON_URL,
) -> None:
    if output_path.exists():
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(source_url, timeout=120) as response:
        output_path.write_bytes(response.read())


def calculate_bbox(ring: list[list[float]]) -> tuple[float, float, float, float]:
    longitudes = [point[0] for point in ring]
    latitudes = [point[1] for point in ring]

    return min(longitudes), min(latitudes), max(longitudes), max(latitudes)


def point_in_ring(longitude: float, latitude: float, ring: list[list[float]]) -> bool:
    inside = False
    previous_longitude, previous_latitude = ring[-1]

    for current_longitude, current_latitude in ring:
        crosses_latitude = (current_latitude > latitude) != (
            previous_latitude > latitude
        )

        if crosses_latitude:
            intersection_longitude = (
                (previous_longitude - current_longitude)
                * (latitude - current_latitude)
                / (previous_latitude - current_latitude)
                + current_longitude
            )

            if longitude < intersection_longitude:
                inside = not inside

        previous_longitude, previous_latitude = current_longitude, current_latitude

    return inside


def point_in_polygon(
    longitude: float,
    latitude: float,
    polygon: list[list[list[float]]],
) -> bool:
    outer_ring = polygon[0]

    if not point_in_ring(longitude, latitude, outer_ring):
        return False

    return not any(point_in_ring(longitude, latitude, hole) for hole in polygon[1:])


def iter_geojson_polygons(geojson: dict) -> Iterable[list[list[list[float]]]]:
    for feature in geojson.get("features", []):
        geometry = feature.get("geometry", {})
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        if geometry_type == "Polygon":
            yield coordinates
        elif geometry_type == "MultiPolygon":
            yield from coordinates


def load_land_polygons(
    land_geojson_path: Path = LAND_GEOJSON_PATH,
) -> list[dict]:
    with land_geojson_path.open("r", encoding="utf-8") as file:
        geojson = json.load(file)

    polygons = []

    for polygon in iter_geojson_polygons(geojson):
        polygons.append(
            {
                "bbox": calculate_bbox(polygon[0]),
                "polygon": polygon,
            }
        )

    return polygons


def is_land_point(
    longitude: float,
    latitude: float,
    land_polygons: list[dict],
) -> bool:
    for land_polygon in land_polygons:
        min_lon, min_lat, max_lon, max_lat = land_polygon["bbox"]

        if not (min_lon <= longitude <= max_lon and min_lat <= latitude <= max_lat):
            continue

        if point_in_polygon(longitude, latitude, land_polygon["polygon"]):
            return True

    return False


def iter_sample_points(
    latitude: float,
    longitude: float,
    radius_km: float,
    sample_spacing_km: float,
) -> Iterable[tuple[float, float]]:
    latitude_km = 111.32
    longitude_km = max(111.32 * math.cos(math.radians(latitude)), 1.0)
    step = max(float(sample_spacing_km), 0.25)
    steps = range(math.floor(-radius_km / step), math.ceil(radius_km / step) + 1)

    for x_index in steps:
        x_km = x_index * step

        for y_index in steps:
            y_km = y_index * step

            if x_km**2 + y_km**2 > radius_km**2:
                continue

            yield (
                longitude + (x_km / longitude_km),
                latitude + (y_km / latitude_km),
            )


def estimate_city_land_area(
    latitude: float,
    longitude: float,
    land_polygons: list[dict],
    radius_meters: int = DEFAULT_OSM_QUERY_RADIUS_METERS,
    sample_spacing_km: float = 1.0,
) -> dict:
    radius_km = radius_meters / 1000.0
    total_points = 0
    land_points = 0

    for sample_longitude, sample_latitude in iter_sample_points(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        sample_spacing_km=sample_spacing_km,
    ):
        total_points += 1

        if is_land_point(sample_longitude, sample_latitude, land_polygons):
            land_points += 1

    if total_points == 0:
        land_share = 1.0
    else:
        land_share = land_points / total_points

    return {
        "land_share": round(land_share, 4),
        "land_area_km2": round(circle_area_km2(radius_meters) * land_share, 2),
        "sample_point_count": total_points,
        "land_sample_point_count": land_points,
    }


def build_land_area_estimates(
    city_df: pd.DataFrame,
    land_polygons: list[dict],
    radius_meters: int = DEFAULT_OSM_QUERY_RADIUS_METERS,
    sample_spacing_km: float = 1.0,
) -> pd.DataFrame:
    rows = []

    for city in city_df.itertuples(index=False):
        estimate = estimate_city_land_area(
            latitude=float(city.latitude),
            longitude=float(city.longitude),
            land_polygons=land_polygons,
            radius_meters=radius_meters,
            sample_spacing_km=sample_spacing_km,
        )
        rows.append(
            {
                "city": city.city,
                "country": city.country,
                "latitude": float(city.latitude),
                "longitude": float(city.longitude),
                "radius_meters": radius_meters,
                **estimate,
            }
        )

    return pd.DataFrame(rows)


def update_osm_count_cache_with_land_area(
    cache_path: Path,
    land_area_df: pd.DataFrame,
) -> bool:
    if not cache_path.exists():
        return False

    cache_df = pd.read_csv(cache_path)

    if cache_df.empty:
        return False

    cache_df = cache_df.drop(columns=["land_area_km2"], errors="ignore")
    land_columns = ["city", "country", "land_area_km2"]
    updated_df = cache_df.merge(
        land_area_df[land_columns],
        on=["city", "country"],
        how="left",
    )
    updated_df.to_csv(cache_path, index=False)

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate usable land area within each CityFit OSM scoring radius."
    )
    parser.add_argument("--sample-spacing-km", type=float, default=1.0)
    parser.add_argument("--radius-meters", type=int, default=DEFAULT_OSM_QUERY_RADIUS_METERS)
    parser.add_argument("--land-geojson-path", type=Path, default=LAND_GEOJSON_PATH)
    parser.add_argument("--land-geojson-url", default=LAND_GEOJSON_URL)
    parser.add_argument("--output-path", type=Path, default=LAND_AREA_ESTIMATES_PATH)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download_land_geojson(
        output_path=args.land_geojson_path,
        source_url=args.land_geojson_url,
    )
    land_polygons = load_land_polygons(args.land_geojson_path)
    city_df = pd.read_csv(CITY_COORDINATES_PATH)
    land_area_df = build_land_area_estimates(
        city_df=city_df,
        land_polygons=land_polygons,
        radius_meters=args.radius_meters,
        sample_spacing_km=args.sample_spacing_km,
    )

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    land_area_df.to_csv(args.output_path, index=False)

    updated_caches = [
        cache_path
        for cache_path in OSM_COUNT_CACHE_PATHS
        if update_osm_count_cache_with_land_area(cache_path, land_area_df)
    ]

    print(
        f"Wrote {len(land_area_df)} land-area estimates to {args.output_path}."
    )

    if updated_caches:
        print("Updated OSM count caches:")
        for cache_path in updated_caches:
            print(f"- {cache_path}")
    else:
        print("No OSM count caches were updated.")


if __name__ == "__main__":
    main()
