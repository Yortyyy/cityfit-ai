from cityfit.config import (
    CITY_FEATURES_PATH,
    CITYFIT_SCORES_PATH,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
)
from cityfit.api.schemas import UserProfile
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.scoring import (
    calculate_cityfit_score,
    rank_cities,
)
from cityfit.features.weights import build_weights


def main() -> None:
    print("Running CityFit ranking pipeline...")

    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    baseline_profile = UserProfile(
        priority_purchasing_power=1.0,
        priority_safety=1.0,
        priority_healthcare=1.0,
        priority_climate=1.0,
        priority_low_cost=1.0,
        priority_housing=1.0,
        priority_low_pollution=1.0,
        priority_low_traffic=1.0,
        remote_worker=False,
    )

    weights = build_weights(baseline_profile)

    scored_df = calculate_cityfit_score(raw_df, weights)

    features_df = scored_df.drop(columns=["cityfit_score"], errors="ignore")
    features_df.to_csv(CITY_FEATURES_PATH, index=False)

    ranked_df = rank_cities(scored_df)
    ranked_df.to_csv(CITYFIT_SCORES_PATH, index=False)

    top_cities = ranked_df.head(25)

    print("\nTop CityFit recommendations:\n")
    print(
        top_cities[
            [
                "city",
                "country",
                "cityfit_rank",
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