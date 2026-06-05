from cityfit.agent.service import build_agent_answer
from cityfit.api.schemas import UserProfile
from cityfit.rag.ingest import ingest_knowledge_base


def test_agent_template_mode_uses_template_provider():
    ingest_knowledge_base(reset=True)

    profile = UserProfile(top_n=5)

    response = build_agent_answer(
        question="Compare Tampa and Madrid.",
        profile=profile,
        response_mode="template",
    )

    assert response["metadata"]["model_provider"] == "deterministic_template"
    assert response["metadata"]["model_name"] == "no_llm_v1"
    assert "retrieve_context" in response["metadata"]["tools_used"]
    assert "compare_cities" in response["metadata"]["tools_used"]


def test_agent_template_mode_returns_requested_cities():
    ingest_knowledge_base(reset=True)

    profile = UserProfile(top_n=5)

    response = build_agent_answer(
        question="Compare Tokyo and Osaka.",
        profile=profile,
        response_mode="template",
    )

    assert response["cities_compared"] == ["Tokyo", "Osaka"]
    assert len(response["city_results"]) == 2