from fastapi import FastAPI

from cityfit.agent.service import build_agent_answer
from cityfit.api.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    RecommendationResponse,
    UserProfile,
)
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.explanations import explain_city_rank
from cityfit.features.filters import filter_by_country, filter_by_region
from cityfit.features.scoring import add_cityfit_rank, calculate_cityfit_score, rank_cities
from cityfit.features.weights import build_weights


app = FastAPI(
    title="CityFit AI API",
    description="Personalized city recommendations using quality-of-life and cost-of-living metrics.",
    version="0.1.0",
)

def get_ranked_cities(profile: UserProfile):
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    scored_df = calculate_cityfit_score(raw_df, build_weights(profile))
    ranked_df = add_cityfit_rank(scored_df)

    ranked_df = filter_by_region(ranked_df, profile.region)
    ranked_df = filter_by_country(ranked_df, profile.country)

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
        "region",
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