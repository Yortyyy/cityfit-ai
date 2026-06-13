from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    priority_purchasing_power: float = Field(default=1.0, ge=0.0, le=2.0)
    priority_low_cost: float = Field(default=1.0, ge=0.0, le=2.0)
    priority_safety: float = Field(default=1.0, ge=0.0, le=2.0)
    priority_healthcare: float = Field(default=1.0, ge=0.0, le=2.0)
    priority_housing: float = Field(default=1.0, ge=0.0, le=2.0)
    priority_low_traffic: float = Field(default=0.7, ge=0.0, le=2.0)
    priority_climate: float = Field(default=0.8, ge=0.0, le=2.0)
    priority_low_pollution: float = Field(default=0.7, ge=0.0, le=2.0)
    remote_worker: bool = True
    top_n: int = Field(default=10, ge=1, le=500)

    region: str | None = Field(default=None)
    country: str | None = Field(default=None)


class CityRecommendation(BaseModel):
    city: str
    country: str
    region: str

    latitude: float
    longitude: float

    numbeo_qol_rank: float
    cityfit_rank: float
    rank_difference: float
    numbeo_quality_of_life_index: float
    cityfit_score: float
    cost_of_living_index: float
    purchasing_power_index: float
    safety_index: float
    healthcare_index: float
    traffic_commute_index: float
    climate_index: float
    pollution_index: float

    explanation: str


class RecommendationResponse(BaseModel):
    recommendations: list[CityRecommendation]


class AgentQueryRequest(UserProfile):
    question: str
    top_k_context: int = Field(default=4, ge=1, le=10)
    response_mode: str = Field(default="template", pattern="^(template|llm)$")


class RetrievedContextChunk(BaseModel):
    source: str
    chunk_index: int
    text: str
    distance: float


class AgentMetadata(BaseModel):
    prompt_version: str
    data_version: str
    tools_used: list[str]
    model_provider: str
    model_name: str
    limitations: list[str]


class AgentQueryResponse(BaseModel):
    answer: str
    cities_compared: list[str]
    city_results: list[dict]
    sources: list[str]
    retrieved_context: list[RetrievedContextChunk]
    metadata: AgentMetadata