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
    title="CityFit AI API",
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

@app.post("/agent/query", response_model=AgentQueryResponse)
def query_agent(request: AgentQueryRequest):
    profile = UserProfile(
        priority_safety=request.priority_safety,
        priority_healthcare=request.priority_healthcare,
        priority_climate=request.priority_climate,
        priority_purchasing_power=request.priority_purchasing_power,
        priority_low_cost=request.priority_low_cost,
        priority_housing=request.priority_housing,
        priority_low_pollution=request.priority_low_pollution,
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