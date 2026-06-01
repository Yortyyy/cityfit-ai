from fastapi import FastAPI

from cityfit.api.schemas import RecommendationResponse, UserProfile
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.explanations import explain_city_rank
from cityfit.features.scoring import add_cityfit_rank, calculate_cityfit_score, rank_cities
from cityfit.features.transformations import add_affordability_features


app = FastAPI(
    title="CityFit AI API",
    description="Personalized city recommendations using quality-of-life and cost-of-living metrics.",
    version="0.1.0",
)


def build_weights(profile: UserProfile) -> dict:
    traffic_weight = 0.03 if profile.remote_worker else 0.10

    return {
        "numbeo_quality_of_life": 0.15,
        "purchasing_power": 0.20 * profile.priority_purchasing_power,
        "safety": 0.20 * profile.priority_safety,
        "healthcare": 0.10 * profile.priority_healthcare,
        "climate": 0.10 * profile.priority_climate,
        "cost_penalty": 0.20 * profile.priority_low_cost,
        "housing_penalty": 0.15 * profile.priority_housing,
        "pollution_penalty": 0.07 * profile.priority_low_pollution,
        "traffic_penalty": traffic_weight,
    }


def get_ranked_cities(profile: UserProfile):
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    features_df = add_affordability_features(raw_df)
    scored_df = calculate_cityfit_score(features_df, build_weights(profile))
    ranked_df = add_cityfit_rank(scored_df)

    top_df = rank_cities(ranked_df, top_n=profile.top_n).copy()
    top_df["explanation"] = top_df.apply(explain_city_rank, axis=1)

    return top_df


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend_cities(profile: UserProfile):
    top_df = get_ranked_cities(profile)

    response_columns = [
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
        "pollution_index",
        "climate_index",
        "explanation",
    ]

    recommendations = top_df[response_columns].to_dict(orient="records")

    return {"recommendations": recommendations}