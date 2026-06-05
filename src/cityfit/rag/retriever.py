from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from cityfit.config import COLLECTION_NAME, EMBEDDING_MODEL_NAME, VECTOR_STORE_DIR


@dataclass
class RetrievedChunk:
    """A retrieved knowledge-base chunk."""

    text: str
    source: str
    source_path: str
    chunk_index: int
    distance: float


def get_collection(
    embedding_function=None,
    collection_name: str = COLLECTION_NAME,
    vector_store_dir: Path = VECTOR_STORE_DIR,
):
    """Load the existing Chroma knowledge-base collection."""
    if embedding_function is None:
        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )

    client = chromadb.PersistentClient(path=str(vector_store_dir))

    return client.get_collection(
        name=collection_name,
        embedding_function=embedding_function,
    )


def retrieve_context(
    query: str,
    top_k: int = 4,
    embedding_function=None,
    collection_name: str = COLLECTION_NAME,
    vector_store_dir: Path = VECTOR_STORE_DIR,
) -> list[RetrievedChunk]:
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    collection = get_collection(
        embedding_function=embedding_function,
        collection_name=collection_name,
        vector_store_dir=vector_store_dir,
    )

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[RetrievedChunk] = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        chunks.append(
            RetrievedChunk(
                text=document,
                source=metadata["source"],
                source_path=metadata["source_path"],
                chunk_index=int(metadata["chunk_index"]),
                distance=float(distance),
            )
        )

    return chunks


def format_retrieved_context(chunks: list[RetrievedChunk]) -> str:
    """
    Format retrieved chunks for use in a prompt or API response.
    """
    formatted_chunks = []

    for idx, chunk in enumerate(chunks, start=1):
        formatted_chunks.append(
            f"[Source {idx}: {chunk.source}, chunk {chunk.chunk_index}]\n"
            f"{chunk.text}"
        )

    return "\n\n---\n\n".join(formatted_chunks)


def main() -> None:
    query = "How does CityFit handle data limitations and responsible AI?"
    chunks = retrieve_context(query, top_k=3)

    print(f"Query: {query}\n")

    for chunk in chunks:
        print(f"Source: {chunk.source}")
        print(f"Distance: {chunk.distance:.4f}")
        print(chunk.text[:500])
        print("-" * 80)


if __name__ == "__main__":
    main()