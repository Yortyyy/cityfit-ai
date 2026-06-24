from pathlib import Path

import pandas as pd

from cityfit.lifestyle.food_scene_scoring import (
    FOOD_SCENE_COMPONENTS,
    add_food_scene_scores,
)


LIFESTYLE_METRICS_PATH = Path("data/reference/lifestyle_metrics.csv")
OSM_DAILY_LIFE_COUNTS_PATH = Path("data/reference/osm_daily_life_counts.csv")

DIAGNOSTIC_COLUMNS = list(FOOD_SCENE_COMPONENTS.keys())


def update_lifestyle_food_scene_scores(
    lifestyle_path: Path = LIFESTYLE_METRICS_PATH,
    counts_path: Path = OSM_DAILY_LIFE_COUNTS_PATH,
) -> pd.DataFrame:
    lifestyle_df = pd.read_csv(lifestyle_path)
    counts_df = pd.read_csv(counts_path)

    scored_df = add_food_scene_scores(lifestyle_df, counts_df)

    completed_count = counts_df.drop_duplicates(subset=["city", "country"]).shape[0]
    total_count = lifestyle_df.drop_duplicates(subset=["city", "country"]).shape[0]

    if completed_count < total_count:
        raise ValueError(
            "OSM count cache is incomplete: "
            f"{completed_count}/{total_count} cities have counts."
        )

    scored_df["data_quality"] = scored_df["data_quality"].replace(
        {
            "not_started": "partial_food",
            "partial_airport": "partial_food_airport",
            "partial_daily_life": "partial_daily_life_food",
            "partial_daily_life_airport": "partial_daily_life_food_airport",
        }
    )
    scored_df["method_version"] = scored_df["method_version"].fillna("free_proxy_v1")

    output_columns = [
        column for column in scored_df.columns if column not in DIAGNOSTIC_COLUMNS
    ]

    scored_df[output_columns].to_csv(lifestyle_path, index=False)

    return scored_df


def main() -> None:
    scored_df = update_lifestyle_food_scene_scores()

    print(
        "Updated food scene scores for "
        f"{scored_df['food_scene_score'].notna().sum()} cities in "
        f"{LIFESTYLE_METRICS_PATH}."
    )
    print(
        scored_df[["city", "country", "food_scene_score"]]
        .sort_values("food_scene_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
