from pathlib import Path

import chromadb


CHROMA_PATH = Path("results/chroma_db")
COLLECTION_NAME = "day6_chunks"


def get_chroma_client(path: Path = CHROMA_PATH):
    path.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(path)
    )


def get_collection(
    path: Path = CHROMA_PATH,
    name: str = COLLECTION_NAME,
):
    client = get_chroma_client(path)

    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    ids: list[str],
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    if not ids:
        raise ValueError("ids cannot be empty")

    if not (
        len(ids)
        == len(texts)
        == len(embeddings)
        == len(metadatas)
    ):
        raise ValueError(
            "ids, texts, embeddings, and metadatas must have the same length"
        )

    collection = get_collection()

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def get_collection_count() -> int:
    collection = get_collection()
    return collection.count()