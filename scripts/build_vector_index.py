import hashlib
import json
from pathlib import Path

from app.rag.embeddings import embed_texts
from app.rag.vector_store import get_collection


CHUNKS_FILE = Path("results/chunks.jsonl")

SELECTED_DOCUMENTS = {
    "DOC001",
    "DOC002",
    "DOC003",
    "DOC004",
    "DOC005",
    "DOC007",
    "DOC008",
    "DOC009",
    "DOC010",
    "DOC013",
    "DOC014",
    "DOC015",
    "DOC016",
    "DOC017",
    "DOC019",
}

BATCH_SIZE = 16
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_selected_chunks() -> list[dict]:
    chunks = []

    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            row = json.loads(line)

            if row["document_id"] in SELECTED_DOCUMENTS:
                chunks.append(row)

    return chunks


def get_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_index() -> None:
    chunks = load_selected_chunks()

    if not chunks:
        raise ValueError("No selected chunks were found.")

    collection = get_collection()

    ids = [chunk["chunk_id"] for chunk in chunks]

    existing = collection.get(
        ids=ids,
        include=["metadatas"],
    )

    existing_metadata = {}

    for chunk_id, metadata in zip(
        existing["ids"],
        existing["metadatas"],
    ):
        if metadata:
            existing_metadata[chunk_id] = metadata

    chunks_to_process = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        content_hash = get_content_hash(chunk["text"])

        old_metadata = existing_metadata.get(chunk_id)

        if (
            old_metadata
            and old_metadata.get("content_hash") == content_hash
            and old_metadata.get("embedding_model") == EMBEDDING_MODEL
        ):
            continue

        chunks_to_process.append(chunk)

    if not chunks_to_process:
        print("No changed chunks found.")
        print(f"Indexed chunks: {collection.count()}")
        return

    texts = [chunk["text"] for chunk in chunks_to_process]

    embeddings = embed_texts(
        texts,
        batch_size=BATCH_SIZE,
    )

    metadatas = []

    for chunk in chunks_to_process:
        metadatas.append(
            {
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "source_path": chunk["source_path"],
                "updated_at": chunk["updated_at"],
                "chunk_index": chunk["chunk_index"],
                "category": chunk["category"],
                "embedding_model": EMBEDDING_MODEL,
                "content_hash": get_content_hash(chunk["text"]),
            }
        )

    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in chunks_to_process],
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Selected chunks: {len(chunks)}")
    print(f"Chunks embedded: {len(chunks_to_process)}")
    print(f"Chunks skipped: {len(chunks) - len(chunks_to_process)}")
    print(f"Total indexed chunks: {collection.count()}")


if __name__ == "__main__":
    build_index()