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