from pathlib import Path

import pandas as pd

from cityfit.lifestyle.lifestyle_scoring import add_lifestyle_scores


LIFESTYLE_METRICS_PATH = Path("data/reference/lifestyle_metrics.csv")


def update_lifestyle_scores(
    lifestyle_path: Path = LIFESTYLE_METRICS_PATH,
) -> pd.DataFrame:
    lifestyle_df = pd.read_csv(lifestyle_path)
    scored_df = add_lifestyle_scores(lifestyle_df)
    scored_df["method_version"] = scored_df["method_version"].fillna("free_proxy_v1")
    scored_df.to_csv(lifestyle_path, index=False)

    return scored_df


def main() -> None:
    scored_df = update_lifestyle_scores()

    print(
        "Updated lifestyle scores for "
        f"{scored_df['lifestyle_score'].notna().sum()} cities in "
        f"{LIFESTYLE_METRICS_PATH}."
    )
    print(
        scored_df[["city", "country", "lifestyle_score"]]
        .sort_values("lifestyle_score", ascending=False)
        .head(12)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
