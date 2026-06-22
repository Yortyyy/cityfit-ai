from cityfit.agent.service import build_agent_answer
from cityfit.api.schemas import UserProfile
from cityfit.rag.ingest import ingest_knowledge_base


def test_agent_response_includes_sources_and_metadata():
    ingest_knowledge_base(reset=True)

    profile = UserProfile(top_n=5)

    response = build_agent_answer(
        question="Compare Tampa, Madrid, and Tokyo for a remote worker.",
        profile=profile,
    )

    assert "answer" in response
    assert response["answer"]
    assert "sources" in response
    assert response["sources"]
    assert "metadata" in response
    assert "tools_used" in response["metadata"]
    assert "limitations" in response["metadata"]
    assert "retrieve_context" in response["metadata"]["tools_used"]
    

def test_methodology_question_uses_methodology_response():
    profile = UserProfile(top_n=5)

    response = build_agent_answer(
        question="What is CityFit's methodology?",
        profile=profile,
        response_mode="template",
    )

    assert "retrieve_context" in response["metadata"]["tools_used"]
    assert "rank_city_recommendations" not in response["metadata"]["tools_used"]
    assert "CityFit" in response["answer"]
    assert "methodology" in response["answer"].lower() or "scoring" in response["answer"].lower()


def test_agent_response_compares_requested_cities():
    ingest_knowledge_base(reset=True)

    profile = UserProfile(top_n=5)

    response = build_agent_answer(
        question="Compare Tampa and Madrid.",
        profile=profile,
    )

    assert "Tampa" in response["cities_compared"]
    assert "Madrid" in response["cities_compared"]
    assert len(response["city_results"]) >= 2

def test_agent_respects_region_filter_for_recommendations():
    profile = UserProfile(
        region="Europe",
        top_n=5,
    )

    response = build_agent_answer(
        question="What are the best cities for me?",
        profile=profile,
        response_mode="template",
    )

    assert len(response["city_results"]) > 0
    assert all(city["region"] == "Europe" for city in response["city_results"])
    
def test_agent_explains_city_fit_question_without_ranking_recommendations():
    profile = UserProfile(top_n=10)

    response = build_agent_answer(
        question="What are Tampa's strengths and weaknesses?",
        profile=profile,
        response_mode="template",
    )

    assert "explain_city_fit" in response["metadata"]["tools_used"]
    assert "rank_city_recommendations" not in response["metadata"]["tools_used"]
    assert "compare_cities" not in response["metadata"]["tools_used"]

    assert "Tampa" in response["answer"]
    assert "Quick take" in response["answer"]
    assert "Strengths" in response["answer"]
    assert "Tradeoffs" in response["answer"]
    assert "Explanation" in response["answer"]
    assert "Personalized rank" in response["answer"]
    assert "Neutral baseline rank" in response["answer"]
    
def test_agent_methodology_question_still_uses_methodology_answer():
    profile = UserProfile(top_n=10)

    response = build_agent_answer(
        question="How does CityFit calculate scores?",
        profile=profile,
        response_mode="template",
    )

    assert "retrieve_context" in response["metadata"]["tools_used"]
    assert "explain_city_fit" not in response["metadata"]["tools_used"]
    assert "rank_city_recommendations" not in response["metadata"]["tools_used"]

    assert "How CityFit scoring works" in response["answer"]
    assert "Baseline vs personalized ranking" in response["answer"]