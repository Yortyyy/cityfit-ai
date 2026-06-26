from fastapi import FastAPI

from cityfit.agent.service import build_agent_answer
from cityfit.api.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    RecommendationResponse,
    UserProfile,
)

from cityfit.recommendations.service import get_top_city_recommendations


app = FastAPI(
    title="CityFit API",
    description="Personalized city recommendations using quality-of-life and cost-of-living metrics.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend_cities(profile: UserProfile):
    top_df = get_top_city_recommendations(profile)

    response_columns = [
        "city",
        "country",
        "region",
        "latitude",
        "longitude",
        "cityfit_rank",
        "baseline_cityfit_rank",
        "rank_difference",
        "numbeo_quality_of_life_index",
        "cityfit_score",
        "baseline_cityfit_score",
        "practical_score",
        "lifestyle_score",
        "lifestyle_fit_score",
        "baseline_lifestyle_score",
        "daily_life_score",
        "food_scene_score",
        "culture_score",
        "outdoors_score",
        "transit_score",
        "airport_score",
        "nightlife_score",
        "pace_of_life",
        "purchasing_power_index",
        "cost_of_living_index",
        "safety_index",
        "healthcare_index",
        "property_price_to_income_ratio",
        "traffic_commute_index",
        "climate_index",
        "pollution_index",
        "explanation",
    ]

    recommendations = top_df[response_columns].to_dict(orient="records")

    return {"recommendations": recommendations}

@app.post("/agent/query", response_model=AgentQueryResponse)
def query_agent(request: AgentQueryRequest):
    profile = UserProfile(
        priority_purchasing_power=request.priority_purchasing_power,
        priority_low_cost=request.priority_low_cost,
        priority_safety=request.priority_safety,
        priority_healthcare=request.priority_healthcare,
        priority_housing=request.priority_housing,
        priority_low_traffic=request.priority_low_traffic,
        priority_climate=request.priority_climate,
        priority_low_pollution=request.priority_low_pollution,
        priority_daily_life=request.priority_daily_life,
        priority_food_scene=request.priority_food_scene,
        priority_culture=request.priority_culture,
        priority_outdoors=request.priority_outdoors,
        priority_transit=request.priority_transit,
        priority_airport=request.priority_airport,
        priority_nightlife=request.priority_nightlife,
        priority_practical_fit=request.priority_practical_fit,
        priority_lifestyle_fit=request.priority_lifestyle_fit,
        remote_worker=request.remote_worker,
        top_n=request.top_n,
        region=request.region,
        country=request.country,
    )

    return build_agent_answer(
        question=request.question,
        profile=profile,
        top_k_context=request.top_k_context,
        response_mode=request.response_mode,
    )
