from pathlib import Path

import pandas as pd


LIFESTYLE_METRICS_PATH = Path("data/reference/lifestyle_metrics.csv")


REQUIRED_COLUMNS = [
    "city",
    "country",
    "latitude",
    "longitude",
    "daily_life_score",
    "food_scene_score",
    "culture_score",
    "outdoors_score",
    "transit_score",
    "airport_score",
    "nightlife_score",
    "friendliness_score",
    "pace_of_life",
    "lifestyle_score",
    "data_quality",
    "method_version",
]


def load_lifestyle_metrics() -> pd.DataFrame:
    if not LIFESTYLE_METRICS_PATH.exists():
        raise FileNotFoundError(
            f"Could not find lifestyle metrics file: {LIFESTYLE_METRICS_PATH}"
        )

    lifestyle_df = pd.read_csv(LIFESTYLE_METRICS_PATH)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in lifestyle_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required lifestyle metric columns: {missing_columns}"
        )

    duplicated_rows = lifestyle_df.duplicated(subset=["city", "country"])

    if duplicated_rows.any():
        duplicates = lifestyle_df.loc[
            duplicated_rows,
            ["city", "country"],
        ].to_dict(orient="records")

        raise ValueError(
            f"Duplicate lifestyle metric rows found: {duplicates}"
        )

    return lifestyle_df
