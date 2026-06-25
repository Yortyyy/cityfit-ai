from pathlib import Path

import pandas as pd

from cityfit.lifestyle.pace_scoring import add_pace_of_life


LIFESTYLE_METRICS_PATH = Path("data/reference/lifestyle_metrics.csv")
CITY_FEATURES_PATH = Path("data/processed/city_features.csv")

DIAGNOSTIC_COLUMNS = [
    "traffic_commute_index",
    "traffic_pressure_score",
    "cultural_pace_baseline",
    "pace_intensity_score",
]


def _mark_pace_data_quality(value: object) -> str:
    if pd.isna(value) or value == "not_started":
        return "partial_pace"

    value = str(value)

    if "pace" in value:
        return value

    return f"{value}_pace"


def update_lifestyle_pace_of_life(
    lifestyle_path: Path = LIFESTYLE_METRICS_PATH,
    city_features_path: Path = CITY_FEATURES_PATH,
) -> pd.DataFrame:
    lifestyle_df = pd.read_csv(lifestyle_path)
    city_features_df = pd.read_csv(city_features_path)

    scored_df = add_pace_of_life(lifestyle_df, city_features_df)

    missing_traffic_count = scored_df["traffic_commute_index"].isna().sum()

    if missing_traffic_count:
        raise ValueError(
            "City feature data is missing traffic rows for "
            f"{missing_traffic_count} lifestyle cities."
        )

    scored_df["data_quality"] = scored_df["data_quality"].apply(
        _mark_pace_data_quality
    )
    scored_df["method_version"] = scored_df["method_version"].fillna("free_proxy_v1")

    output_columns = [
        column for column in scored_df.columns if column not in DIAGNOSTIC_COLUMNS
    ]

    scored_df[output_columns].to_csv(lifestyle_path, index=False)

    return scored_df


def main() -> None:
    scored_df = update_lifestyle_pace_of_life()

    print(
        "Updated pace of life for "
        f"{scored_df['pace_of_life'].notna().sum()} cities in "
        f"{LIFESTYLE_METRICS_PATH}."
    )
    print(scored_df["pace_of_life"].value_counts().to_string())
    print(
        scored_df[["city", "country", "pace_of_life", "pace_intensity_score"]]
        .sort_values("pace_intensity_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
