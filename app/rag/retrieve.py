from pathlib import Path

from app.rag.embeddings import embed_query
from app.rag.vector_store import get_collection


DEFAULT_TOP_K = 3


def retrieve_documents(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    min_score: float | None = None,
    where: dict | None = None,
    chroma_path: Path | None = None,
    collection_name: str = "day6_chunks",
) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    query_embedding = embed_query(query)

    if chroma_path is None:
        collection = get_collection(
            name=collection_name,
        )
    else:
        collection = get_collection(
            path=chroma_path,
            name=collection_name,
        )

    if collection.count() == 0:
        return []

    search_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        where=where,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    results = []

    ids = search_results["ids"][0]
    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        score = 1.0 - distance

        if min_score is not None and score < min_score:
            continue

        results.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "score": round(score, 4),
                "document_id": metadata.get("document_id"),
                "title": metadata.get("title"),
                "source_path": metadata.get("source_path"),
                "updated_at": metadata.get("updated_at"),
                "chunk_index": metadata.get("chunk_index"),
                "category": metadata.get("category"),
            }
        )

    return results