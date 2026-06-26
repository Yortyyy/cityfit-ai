from __future__ import annotations

import numpy as np
import pandas as pd

from cityfit.lifestyle.land_area import get_land_area_km2, normalize_count_for_land_area


OUTDOORS_COMPONENTS = {
    "park_green_count": {
        "full_score_count": 80,
        "weight": 0.30,
    },
    "nature_reserve_count": {
        "full_score_count": 50,
        "weight": 0.20,
    },
    "trail_route_count": {
        "full_score_count": 250,
        "weight": 0.17,
    },
    "water_access_count": {
        "full_score_count": 1000,
        "weight": 0.20,
    },
    "viewpoint_peak_count": {
        "full_score_count": 100,
        "weight": 0.13,
    },
}

LEGACY_OUTDOORS_COMPONENTS = {
    "beach_water_count": "water_access_count",
}


def score_outdoors_count(count: int | float, full_score_count: int | float) -> float:
    count = max(float(count), 0.0)
    full_score_count = max(float(full_score_count), 1.0)

    return min(np.log1p(count) / np.log1p(full_score_count) * 100.0, 100.0)


def calculate_outdoors_score(row: pd.Series) -> float:
    weighted_score = 0.0
    total_weight = 0.0
    land_area_km2 = get_land_area_km2(row)

    for column, settings in OUTDOORS_COMPONENTS.items():
        if column not in row or pd.isna(row[column]):
            continue

        component_score = score_outdoors_count(
            normalize_count_for_land_area(row[column], land_area_km2),
            settings["full_score_count"],
        )
        weight = settings["weight"]

        weighted_score += component_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_score / total_weight, 1)


def add_outdoors_scores(
    cities_df: pd.DataFrame,
    outdoors_counts_df: pd.DataFrame,
) -> pd.DataFrame:
    required_city_columns = {"city", "country"}
    outdoors_counts_df = outdoors_counts_df.copy()

    for legacy_column, current_column in LEGACY_OUTDOORS_COMPONENTS.items():
        if current_column not in outdoors_counts_df and legacy_column in outdoors_counts_df:
            outdoors_counts_df[current_column] = outdoors_counts_df[legacy_column]

    required_count_columns = {"city", "country", *OUTDOORS_COMPONENTS.keys()}
    optional_merge_columns = []

    if "land_area_km2" not in cities_df.columns:
        optional_merge_columns.append("land_area_km2")

    merge_columns = [
        column for column in [*required_count_columns, *optional_merge_columns]
        if column in outdoors_counts_df.columns
    ]

    missing_city_columns = required_city_columns - set(cities_df.columns)
    missing_count_columns = required_count_columns - set(outdoors_counts_df.columns)

    if missing_city_columns:
        raise ValueError(
            f"City data is missing columns: {sorted(missing_city_columns)}"
        )

    if missing_count_columns:
        raise ValueError(
            f"Outdoors count data is missing columns: {sorted(missing_count_columns)}"
        )

    scored_df = cities_df.merge(
        outdoors_counts_df[merge_columns],
        on=["city", "country"],
        how="left",
    )

    for column in OUTDOORS_COMPONENTS:
        scored_df[column] = pd.to_numeric(scored_df[column], errors="coerce").fillna(0)

    scored_df["outdoors_score"] = scored_df.apply(
        calculate_outdoors_score,
        axis=1,
    )

    return scored_df
