from cityfit.rag.ingest import ingest_knowledge_base
from cityfit.rag.retriever import retrieve_context


def test_retrieve_context_returns_chunks():
    ingest_knowledge_base(reset=True)

    chunks = retrieve_context("What are CityFit data limitations?", top_k=2)

    assert len(chunks) > 0
    assert chunks[0].text
    assert chunks[0].source.endswith(".md")