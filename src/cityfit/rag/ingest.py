from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from cityfit.config import DATA_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME, VECTOR_STORE_DIR


KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
COLLECTION_NAME = "cityfit_knowledge_base"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def read_markdown_files(directory: Path = KNOWLEDGE_BASE_DIR) -> list[Path]:
    """Return all markdown files in the knowledge base directory."""
    if not directory.exists():
        raise FileNotFoundError(f"Knowledge base directory does not exist: {directory}")

    markdown_files = sorted(directory.glob("*.md"))

    if not markdown_files:
        raise FileNotFoundError(f"No markdown files found in: {directory}")

    return markdown_files


def chunk_text(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> list[str]:
    """
    Split text into overlapping chunks.

    This simple chunker is enough for the current markdown knowledge base.
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def build_documents(markdown_files: Iterable[Path]) -> tuple[list[str], list[str], list[dict]]:
    """
    Convert markdown files into Chroma document inputs.

    Returns:
        ids: stable chunk IDs
        documents: text chunks
        metadatas: source metadata for each chunk
    """
    ids = []
    documents = []
    metadatas = []

    for file_path in markdown_files:
        text = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"{file_path.stem}_{chunk_idx}"

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(
                {
                    "source": file_path.name,
                    "source_path": str(file_path),
                    "chunk_index": chunk_idx,
                }
            )

    return ids, documents, metadatas


def get_chroma_collection(
    reset: bool = False,
    embedding_function=None,
    collection_name: str = COLLECTION_NAME,
    vector_store_dir: Path = VECTOR_STORE_DIR,
):
    """Create or load the local Chroma collection."""
    vector_store_dir.mkdir(parents=True, exist_ok=True)

    if embedding_function is None:
        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )

    client = chromadb.PersistentClient(path=str(vector_store_dir))

    if reset:
        existing_collections = [
            collection.name for collection in client.list_collections()
        ]

        if collection_name in existing_collections:
            client.delete_collection(name=collection_name)

    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={"description": "CityFit AI knowledge base"},
    )


def ingest_knowledge_base(
    reset: bool = True,
    embedding_function=None,
    collection_name: str = COLLECTION_NAME,
    vector_store_dir: Path = VECTOR_STORE_DIR,
) -> int:
    """
    Ingest markdown knowledge base files into Chroma.

    Returns:
        Number of chunks ingested.
    """
    markdown_files = read_markdown_files()
    ids, documents, metadatas = build_documents(markdown_files)

    collection = get_chroma_collection(
        reset=reset,
        embedding_function=embedding_function,
        collection_name=collection_name,
        vector_store_dir=vector_store_dir,
    )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return len(documents)


def main() -> None:
    chunk_count = ingest_knowledge_base(reset=True)
    print(f"Ingested {chunk_count} chunks into Chroma collection '{COLLECTION_NAME}'.")
    print(f"Vector store path: {VECTOR_STORE_DIR}")


if __name__ == "__main__":
    main()