from cityfit.config import (
    CITY_FEATURES_PATH,
    CITYFIT_SCORES_PATH,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
)
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.scoring import (
    add_cityfit_rank,
    calculate_cityfit_score,
    rank_cities,
)
from cityfit.features.transformations import add_affordability_features
from cityfit.features.user_profiles import REMOTE_WORKER_WEIGHTS


def main() -> None:
    print("Running CityFit ranking pipeline...")
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    features_df = add_affordability_features(raw_df)
    features_df.to_csv(CITY_FEATURES_PATH, index=False)

    scored_df = calculate_cityfit_score(features_df, REMOTE_WORKER_WEIGHTS)
    ranked_df = add_cityfit_rank(scored_df)
    ranked_df.to_csv(CITYFIT_SCORES_PATH, index=False)

    top_cities = rank_cities(ranked_df, top_n=25)

    print("\nTop CityFit recommendations for a remote worker:\n")
    print(
        top_cities[
            [
                "city",
                "country",
                "numbeo_qol_rank",
                "cityfit_rank",
                "rank_difference",
                "numbeo_quality_of_life_index",
                "cityfit_score",
                "cost_of_living_index",
                "purchasing_power_index",
                "safety_index",
                "healthcare_index",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()