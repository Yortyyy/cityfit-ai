from __future__ import annotations

import numpy as np
import pandas as pd


TRANSIT_COMPONENTS = {
    "bus_stop_count": {
        "full_score_count": 2000,
        "weight": 0.30,
    },
    "rail_station_count": {
        "full_score_count": 250,
        "weight": 0.25,
    },
    "metro_tram_count": {
        "full_score_count": 400,
        "weight": 0.25,
    },
    "ferry_aerialway_count": {
        "full_score_count": 40,
        "weight": 0.10,
    },
    "transport_hub_count": {
        "full_score_count": 80,
        "weight": 0.10,
    },
}


def score_transit_count(count: int | float, full_score_count: int | float) -> float:
    count = max(float(count), 0.0)
    full_score_count = max(float(full_score_count), 1.0)

    return min(np.log1p(count) / np.log1p(full_score_count) * 100.0, 100.0)


def calculate_transit_score(row: pd.Series) -> float:
    weighted_score = 0.0
    total_weight = 0.0

    for column, settings in TRANSIT_COMPONENTS.items():
        if column not in row or pd.isna(row[column]):
            continue

        component_score = score_transit_count(
            row[column],
            settings["full_score_count"],
        )
        weight = settings["weight"]

        weighted_score += component_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_score / total_weight, 1)


def add_transit_scores(
    cities_df: pd.DataFrame,
    transit_counts_df: pd.DataFrame,
) -> pd.DataFrame:
    required_city_columns = {"city", "country"}
    required_count_columns = {"city", "country", *TRANSIT_COMPONENTS.keys()}

    missing_city_columns = required_city_columns - set(cities_df.columns)
    missing_count_columns = required_count_columns - set(transit_counts_df.columns)

    if missing_city_columns:
        raise ValueError(
            f"City data is missing columns: {sorted(missing_city_columns)}"
        )

    if missing_count_columns:
        raise ValueError(
            f"Transit count data is missing columns: {sorted(missing_count_columns)}"
        )

    scored_df = cities_df.merge(
        transit_counts_df[list(required_count_columns)],
        on=["city", "country"],
        how="left",
    )

    for column in TRANSIT_COMPONENTS:
        scored_df[column] = pd.to_numeric(scored_df[column], errors="coerce").fillna(0)

    scored_df["transit_score"] = scored_df.apply(
        calculate_transit_score,
        axis=1,
    )

    return scored_df
