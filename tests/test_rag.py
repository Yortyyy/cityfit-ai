from cityfit.rag.ingest import ingest_knowledge_base
from cityfit.rag.retriever import retrieve_context


TEST_COLLECTION_NAME = "test_cityfit_knowledge_base"


class FakeEmbeddingFunction:
    def name(self) -> str:
        return "default"

    def __call__(self, input):
        return self.embed_documents(input=input)

    def embed_documents(self, input):
        return [[0.1, 0.2, 0.3] for _ in input]

    def embed_query(self, input):
        return [[0.1, 0.2, 0.3] for _ in input]


def test_retrieve_context_returns_chunks(tmp_path):
    embedding_function = FakeEmbeddingFunction()
    test_vector_store_dir = tmp_path / "vector_store"

    ingest_knowledge_base(
        reset=True,
        embedding_function=embedding_function,
        collection_name=TEST_COLLECTION_NAME,
        vector_store_dir=test_vector_store_dir,
    )

    chunks = retrieve_context(
        "What are CityFit data limitations?",
        top_k=2,
        embedding_function=embedding_function,
        collection_name=TEST_COLLECTION_NAME,
        vector_store_dir=test_vector_store_dir,
    )

    assert len(chunks) > 0