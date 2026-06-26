from __future__ import annotations

import numpy as np
import pandas as pd

from cityfit.lifestyle.land_area import get_land_area_km2, normalize_count_for_land_area


DAILY_LIFE_CATEGORIES = {
    "grocery_count": {
        "target_count": 1500,
        "weight": 0.22,
    },
    "pharmacy_count": {
        "target_count": 300,
        "weight": 0.16,
    },
    "cafe_count": {
        "target_count": 2000,
        "weight": 0.16,
    },
    "fitness_count": {
        "target_count": 120,
        "weight": 0.12,
    },
    "park_count": {
        "target_count": 80,
        "weight": 0.14,
    },
    "basic_services_count": {
        "target_count": 600,
        "weight": 0.10,
    },
    "healthcare_essentials_count": {
        "target_count": 500,
        "weight": 0.10,
    },
}


def score_category_count(count: int | float, target_count: int | float) -> float:
    count = max(float(count), 0.0)
    target_count = max(float(target_count), 1.0)

    return min(np.log1p(count) / np.log1p(target_count) * 100.0, 100.0)


def calculate_daily_life_score(row: pd.Series) -> float:
    weighted_score = 0.0
    total_weight = 0.0
    land_area_km2 = get_land_area_km2(row)

    for column, settings in DAILY_LIFE_CATEGORIES.items():
        if column not in row or pd.isna(row[column]):
            continue

        category_score = score_category_count(
            normalize_count_for_land_area(row[column], land_area_km2),
            settings["target_count"],
        )
        weight = settings["weight"]

        weighted_score += category_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_score / total_weight, 1)


def add_daily_life_scores(
    cities_df: pd.DataFrame,
    amenity_counts_df: pd.DataFrame,
) -> pd.DataFrame:
    required_city_columns = {"city", "country"}
    required_count_columns = {"city", "country", *DAILY_LIFE_CATEGORIES.keys()}
    optional_merge_columns = []

    if "land_area_km2" not in cities_df.columns:
        optional_merge_columns.append("land_area_km2")

    merge_columns = [
        column for column in [*required_count_columns, *optional_merge_columns]
        if column in amenity_counts_df.columns
    ]

    missing_city_columns = required_city_columns - set(cities_df.columns)
    missing_count_columns = required_count_columns - set(amenity_counts_df.columns)

    if missing_city_columns:
        raise ValueError(
            f"City data is missing columns: {sorted(missing_city_columns)}"
        )

    if missing_count_columns:
        raise ValueError(
            f"Amenity count data is missing columns: {sorted(missing_count_columns)}"
        )

    scored_df = cities_df.merge(
        amenity_counts_df[merge_columns],
        on=["city", "country"],
        how="left",
    )

    for column in DAILY_LIFE_CATEGORIES:
        scored_df[column] = pd.to_numeric(scored_df[column], errors="coerce").fillna(0)

    scored_df["daily_life_score"] = scored_df.apply(
        calculate_daily_life_score,
        axis=1,
    )

    return scored_df
