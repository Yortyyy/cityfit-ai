from __future__ import annotations

import numpy as np
import pandas as pd


TRAFFIC_PRESSURE_MIN = 22.0
TRAFFIC_PRESSURE_MAX = 55.0
SLOW_PACE_MAX = 45.0
FAST_PACE_MIN = 68.0

REGION_CULTURAL_PACE_BASELINES = {
    "Africa": 42.0,
    "Asia": 54.0,
    "Europe": 43.0,
    "Middle East": 46.0,
    "North America": 54.0,
    "Oceania": 44.0,
    "South America": 40.0,
}

COUNTRY_CULTURAL_PACE_BASELINES = {
    "Australia": 43.0,
    "Austria": 40.0,
    "Belgium": 45.0,
    "Brazil": 38.0,
    "Canada": 48.0,
    "China": 60.0,
    "Colombia": 38.0,
    "Costa Rica": 34.0,
    "Croatia": 35.0,
    "Cyprus": 35.0,
    "Denmark": 39.0,
    "Finland": 39.0,
    "France": 40.0,
    "Germany": 48.0,
    "Greece": 35.0,
    "Hong Kong (China)": 72.0,
    "India": 54.0,
    "Ireland": 42.0,
    "Italy": 35.0,
    "Japan": 62.0,
    "Mexico": 38.0,
    "Netherlands": 45.0,
    "New Zealand": 38.0,
    "Norway": 38.0,
    "Portugal": 34.0,
    "Singapore": 78.0,
    "South Korea": 76.0,
    "Spain": 36.0,
    "Sweden": 39.0,
    "Switzerland": 43.0,
    "Thailand": 38.0,
    "United Kingdom": 52.0,
    "United States": 58.0,
    "Uruguay": 36.0,
}

CITY_PACE_ADJUSTMENTS = {
    ("Italy", "Milan"): 14.0,
    ("Japan", "Tokyo"): 10.0,
    ("South Korea", "Seoul"): 8.0,
    ("United Kingdom", "London"): 10.0,
    ("United States", "New York"): 12.0,
}

PACE_COMPONENTS = {
    "cultural_pace_baseline": 0.75,
    "traffic_pressure_score": 0.20,
    "nightlife_score": 0.05,
}


def score_traffic_pressure(
    traffic_commute_index: int | float,
    low_value: float = TRAFFIC_PRESSURE_MIN,
    high_value: float = TRAFFIC_PRESSURE_MAX,
) -> float:
    if pd.isna(traffic_commute_index):
        return np.nan

    traffic_commute_index = float(traffic_commute_index)
    low_value = float(low_value)
    high_value = max(float(high_value), low_value + 1.0)

    return round(
        float(np.clip((traffic_commute_index - low_value) / (high_value - low_value), 0, 1))
        * 100.0,
        1,
    )


def calculate_cultural_pace_baseline(row: pd.Series) -> float:
    country = row.get("country")
    region = row.get("region")
    city = row.get("city")

    baseline = COUNTRY_CULTURAL_PACE_BASELINES.get(country)

    if baseline is None:
        baseline = REGION_CULTURAL_PACE_BASELINES.get(region, 45.0)

    adjustment = CITY_PACE_ADJUSTMENTS.get((country, city), 0.0)

    return round(float(np.clip(baseline + adjustment, 0.0, 100.0)), 1)


def calculate_pace_intensity_score(row: pd.Series) -> float:
    weighted_score = 0.0
    total_weight = 0.0

    for column, weight in PACE_COMPONENTS.items():
        if column not in row or pd.isna(row[column]):
            continue

        weighted_score += float(row[column]) * weight
        total_weight += weight

    if total_weight == 0:
        return np.nan

    return round(weighted_score / total_weight, 1)


def classify_pace_of_life(pace_intensity_score: int | float) -> str:
    if pd.isna(pace_intensity_score):
        return "moderate"

    pace_intensity_score = float(pace_intensity_score)

    if pace_intensity_score < SLOW_PACE_MAX:
        return "slow"

    if pace_intensity_score > FAST_PACE_MIN:
        return "fast"

    return "moderate"


def add_pace_of_life(
    lifestyle_df: pd.DataFrame,
    city_features_df: pd.DataFrame,
) -> pd.DataFrame:
    required_lifestyle_columns = {
        "city",
        "country",
        "region",
        "nightlife_score",
    }
    required_feature_columns = {"city", "country", "traffic_commute_index"}

    missing_lifestyle_columns = required_lifestyle_columns - set(lifestyle_df.columns)
    missing_feature_columns = required_feature_columns - set(city_features_df.columns)

    if missing_lifestyle_columns:
        raise ValueError(
            f"Lifestyle data is missing columns: {sorted(missing_lifestyle_columns)}"
        )

    if missing_feature_columns:
        raise ValueError(
            f"City feature data is missing columns: {sorted(missing_feature_columns)}"
        )

    scored_df = lifestyle_df.merge(
        city_features_df[list(required_feature_columns)],
        on=["city", "country"],
        how="left",
    )

    scored_df["traffic_pressure_score"] = scored_df["traffic_commute_index"].apply(
        score_traffic_pressure
    )
    scored_df["cultural_pace_baseline"] = scored_df.apply(
        calculate_cultural_pace_baseline,
        axis=1,
    )
    scored_df["pace_intensity_score"] = scored_df.apply(
        calculate_pace_intensity_score,
        axis=1,
    )
    scored_df["pace_of_life"] = scored_df["pace_intensity_score"].apply(
        classify_pace_of_life
    )

    return scored_df
