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
from cityfit.lifestyle.lifestyle_scoring import add_lifestyle_scores
from cityfit.lifestyle.merge_lifestyle_metrics import add_lifestyle_metrics
from cityfit.features.fit_blending import calculate_blended_cityfit_score


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
        priority_daily_life=1.0,
        priority_food_scene=1.0,
        priority_culture=1.0,
        priority_outdoors=1.0,
        priority_transit=1.0,
        priority_airport=1.0,
        priority_nightlife=1.0,
        priority_practical_fit=1.0,
        priority_lifestyle_fit=1.0,
        remote_worker=False,
    )

    weights = build_weights(baseline_profile)

    scored_df = calculate_cityfit_score(raw_df, weights).rename(
        columns={"cityfit_score": "practical_score"}
    )
    scored_df = add_lifestyle_metrics(scored_df).rename(
        columns={"lifestyle_score": "baseline_lifestyle_score"}
    )
    scored_df = add_lifestyle_scores(scored_df)
    scored_df = calculate_blended_cityfit_score(
        scored_df,
        practical_fit_weight=baseline_profile.priority_practical_fit,
        lifestyle_fit_weight=baseline_profile.priority_lifestyle_fit,
    )

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
                "practical_score",
                "lifestyle_fit_score",
                "lifestyle_score",
                "cost_of_living_index",
                "purchasing_power_index",
                "safety_index",
                "healthcare_index",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
