from pathlib import Path

import pandas as pd


CITY_COORDINATES_PATH = Path("data/reference/city_coordinates.csv")
CITYFIT_SCORES_PATH = Path("data/processed/cityfit_scores.csv")
OUTPUT_PATH = Path("data/reference/lifestyle_metrics.csv")


LIFESTYLE_COLUMNS = [
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


def main() -> None:
    city_df = pd.read_csv(CITY_COORDINATES_PATH)

    required_columns = ["city", "state", "country", "latitude", "longitude"]
    missing_columns = [
        column for column in required_columns if column not in city_df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    city_df = city_df[required_columns].drop_duplicates(
        subset=["city", "country"]
    )

    if CITYFIT_SCORES_PATH.exists():
        scores_df = pd.read_csv(CITYFIT_SCORES_PATH)

        if "region" in scores_df.columns:
            region_df = (
                scores_df[["city", "country", "region"]]
                .drop_duplicates(subset=["city", "country"])
            )

            city_df = city_df.merge(
                region_df,
                on=["city", "country"],
                how="left",
            )
        else:
            city_df["region"] = None
    else:
        city_df["region"] = None

    ordered_columns = [
        "city",
        "state",
        "country",
        "region",
        "latitude",
        "longitude",
    ]

    lifestyle_df = (
        city_df[ordered_columns]
        .sort_values(["country", "city"])
        .reset_index(drop=True)
    )

    for column in LIFESTYLE_COLUMNS:
        lifestyle_df[column] = None

    lifestyle_df["data_quality"] = "not_started"
    lifestyle_df["method_version"] = "free_proxy_v1"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lifestyle_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Created {OUTPUT_PATH} with {len(lifestyle_df)} cities.")


if __name__ == "__main__":
    main()
