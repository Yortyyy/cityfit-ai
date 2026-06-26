from __future__ import annotations

import pandas as pd


def scale_lifestyle_score_to_cityfit_scale(
    lifestyle_scores: pd.Series,
) -> pd.Series:
    scores = pd.to_numeric(lifestyle_scores, errors="coerce").astype(float)
    median_score = scores.median()
    low_score = scores.quantile(0.05)
    high_score = scores.quantile(0.95)

    if pd.isna(median_score) or pd.isna(low_score) or pd.isna(high_score):
        return pd.Series(100.0, index=scores.index)

    upper_range = max(high_score - median_score, 1.0)
    lower_range = max(median_score - low_score, 1.0)

    scaled_scores = scores.copy()
    above_median = scores >= median_score

    scaled_scores.loc[above_median] = (
        100.0 + ((scores.loc[above_median] - median_score) / upper_range * 100.0)
    )
    scaled_scores.loc[~above_median] = (
        100.0 - ((median_score - scores.loc[~above_median]) / lower_range * 100.0)
    )

    return scaled_scores.clip(lower=0.0, upper=260.0).round(1)


def calculate_blended_cityfit_score(
    df: pd.DataFrame,
    practical_fit_weight: float = 1.0,
    lifestyle_fit_weight: float = 1.0,
) -> pd.DataFrame:
    required_columns = {"practical_score", "lifestyle_score"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"CityFit blend data is missing columns: {sorted(missing_columns)}"
        )

    scored_df = df.copy()
    scored_df["lifestyle_fit_score"] = scale_lifestyle_score_to_cityfit_scale(
        scored_df["lifestyle_score"]
    )

    practical_fit_weight = max(float(practical_fit_weight), 0.0)
    lifestyle_fit_weight = max(float(lifestyle_fit_weight), 0.0)
    total_weight = practical_fit_weight + lifestyle_fit_weight

    if total_weight == 0:
        practical_fit_weight = 1.0
        total_weight = 1.0

    scored_df["cityfit_score"] = (
        scored_df["practical_score"] * practical_fit_weight
        + scored_df["lifestyle_fit_score"] * lifestyle_fit_weight
    ) / total_weight
    scored_df["cityfit_score"] = scored_df["cityfit_score"].round(1)

    return scored_df
