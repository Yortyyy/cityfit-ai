from __future__ import annotations

import pandas as pd


LIFESTYLE_SCORE_WEIGHTS = {
    "daily_life_score": 0.20,
    "food_scene_score": 0.15,
    "culture_score": 0.15,
    "outdoors_score": 0.15,
    "transit_score": 0.15,
    "airport_score": 0.10,
    "nightlife_score": 0.10,
}

LIFESTYLE_PRIORITY_FIELDS = {
    "daily_life_score": "priority_daily_life",
    "food_scene_score": "priority_food_scene",
    "culture_score": "priority_culture",
    "outdoors_score": "priority_outdoors",
    "transit_score": "priority_transit",
    "airport_score": "priority_airport",
    "nightlife_score": "priority_nightlife",
}


def calculate_lifestyle_score(
    row: pd.Series,
    priority_multipliers: dict[str, float] | None = None,
) -> float:
    priority_multipliers = priority_multipliers or {}
    weighted_score = 0.0
    total_weight = 0.0

    for column, base_weight in LIFESTYLE_SCORE_WEIGHTS.items():
        if column not in row or pd.isna(row[column]):
            continue

        priority_field = LIFESTYLE_PRIORITY_FIELDS[column]
        priority_multiplier = priority_multipliers.get(priority_field, 1.0)
        weight = base_weight * max(float(priority_multiplier), 0.0)

        if weight == 0:
            continue

        weighted_score += float(row[column]) * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_score / total_weight, 1)


def add_lifestyle_scores(
    lifestyle_df: pd.DataFrame,
    priority_multipliers: dict[str, float] | None = None,
) -> pd.DataFrame:
    missing_columns = set(LIFESTYLE_SCORE_WEIGHTS) - set(lifestyle_df.columns)

    if missing_columns:
        raise ValueError(
            f"Lifestyle data is missing score columns: {sorted(missing_columns)}"
        )

    scored_df = lifestyle_df.copy()
    scored_df["lifestyle_score"] = scored_df.apply(
        calculate_lifestyle_score,
        axis=1,
        priority_multipliers=priority_multipliers,
    )

    return scored_df
