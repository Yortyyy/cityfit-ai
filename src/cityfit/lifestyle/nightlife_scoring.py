from __future__ import annotations

import numpy as np
import pandas as pd


NIGHTLIFE_COMPONENTS = {
    "bar_pub_count": {
        "full_score_count": 900,
        "weight": 0.42,
    },
    "club_count": {
        "full_score_count": 120,
        "weight": 0.30,
    },
    "music_venue_count": {
        "full_score_count": 160,
        "weight": 0.18,
    },
    "late_entertainment_count": {
        "full_score_count": 80,
        "weight": 0.10,
    },
}


def score_nightlife_count(count: int | float, full_score_count: int | float) -> float:
    count = max(float(count), 0.0)
    full_score_count = max(float(full_score_count), 1.0)

    return min(np.log1p(count) / np.log1p(full_score_count) * 100.0, 100.0)


def calculate_nightlife_score(row: pd.Series) -> float:
    weighted_score = 0.0
    total_weight = 0.0

    for column, settings in NIGHTLIFE_COMPONENTS.items():
        if column not in row or pd.isna(row[column]):
            continue

        component_score = score_nightlife_count(
            row[column],
            settings["full_score_count"],
        )
        weight = settings["weight"]

        weighted_score += component_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_score / total_weight, 1)


def add_nightlife_scores(
    cities_df: pd.DataFrame,
    nightlife_counts_df: pd.DataFrame,
) -> pd.DataFrame:
    required_city_columns = {"city", "country"}
    required_count_columns = {"city", "country", *NIGHTLIFE_COMPONENTS.keys()}

    missing_city_columns = required_city_columns - set(cities_df.columns)
    missing_count_columns = required_count_columns - set(nightlife_counts_df.columns)

    if missing_city_columns:
        raise ValueError(
            f"City data is missing columns: {sorted(missing_city_columns)}"
        )

    if missing_count_columns:
        raise ValueError(
            f"Nightlife count data is missing columns: {sorted(missing_count_columns)}"
        )

    scored_df = cities_df.merge(
        nightlife_counts_df[list(required_count_columns)],
        on=["city", "country"],
        how="left",
    )

    for column in NIGHTLIFE_COMPONENTS:
        scored_df[column] = pd.to_numeric(scored_df[column], errors="coerce").fillna(0)

    scored_df["nightlife_score"] = scored_df.apply(
        calculate_nightlife_score,
        axis=1,
    )

    return scored_df
