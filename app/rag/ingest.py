import hashlib
from pathlib import Path

from app.db.crud import log_event
from app.db.database import Base, SessionLocal, engine
from app.db.models import Document
from app.rag.embeddings import embed_texts
from app.rag.vector_store import get_collection
from scripts.preprocess_documents import process_documents


DEFAULT_INPUT_FOLDER = Path("sample_data/day5_documents")
DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 80
DEFAULT_BATCH_SIZE = 16
DEFAULT_CHROMA_PATH = Path("results/chroma_db")
DEFAULT_COLLECTION_NAME = "day6_chunks"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def ensure_database_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_content_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def get_document_id_from_path(file_path: str) -> str:
    return Path(file_path).stem.split("_", 1)[0]


def ingest_documents(
    input_folder: Path = DEFAULT_INPUT_FOLDER,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
    batch_size: int = DEFAULT_BATCH_SIZE,
    chroma_path: Path = DEFAULT_CHROMA_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> dict:
    ensure_database_tables()

    chunks, processed_documents, failed_documents = process_documents(
        input_folder=input_folder,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    collection = get_collection(
        path=chroma_path,
        name=collection_name,
    )

    db = SessionLocal()

    completed_documents = set()
    failed_document_ids = {}

    for item in failed_documents:
        document_id = get_document_id_from_path(
            item["file"]
        )
        failed_document_ids[document_id] = item["error"]

    try:
        document_ids = sorted(
            {
                chunk["document_id"]
                for chunk in chunks
            }
        )

        for document_id in document_ids:
            log_event(
                db=db,
                document_id=document_id,
                event_type="STARTED",
                status="SUCCESS",
            )

        for document_id in document_ids:
            document_chunks = [
                chunk
                for chunk in chunks
                if chunk["document_id"] == document_id
            ]

            try:
                first_chunk = document_chunks[0]

                existing = collection.get(
                    ids=[
                        chunk["chunk_id"]
                        for chunk in document_chunks
                    ],
                    include=["metadatas"],
                )

                existing_metadata = {
                    chunk_id: metadata
                    for chunk_id, metadata in zip(
                        existing["ids"],
                        existing["metadatas"],
                    )
                    if metadata
                }

                chunks_to_process = []

                for chunk in document_chunks:
                    chunk_id = chunk["chunk_id"]
                    content_hash = get_content_hash(
                        chunk["text"]
                    )
                    old_metadata = existing_metadata.get(
                        chunk_id
                    )

                    if (
                        old_metadata
                        and old_metadata.get("content_hash")
                        == content_hash
                        and old_metadata.get("embedding_model")
                        == EMBEDDING_MODEL
                    ):
                        continue

                    chunks_to_process.append(chunk)

                if chunks_to_process:
                    texts = [
                        chunk["text"]
                        for chunk in chunks_to_process
                    ]

                    embeddings = embed_texts(
                        texts,
                        batch_size=batch_size,
                    )

                    metadatas = [
                        {
                            "document_id": chunk["document_id"],
                            "title": chunk["title"],
                            "source_path": chunk["source_path"],
                            "updated_at": chunk["updated_at"],
                            "chunk_index": chunk["chunk_index"],
                            "category": chunk["category"],
                            "embedding_model": EMBEDDING_MODEL,
                            "content_hash": get_content_hash(
                                chunk["text"]
                            ),
                        }
                        for chunk in chunks_to_process
                    ]

                    collection.upsert(
                        ids=[
                            chunk["chunk_id"]
                            for chunk in chunks_to_process
                        ],
                        documents=texts,
                        embeddings=embeddings,
                        metadatas=metadatas,
                    )

                document = Document(
                    document_id=first_chunk["document_id"],
                    title=first_chunk["title"],
                    content="\n\n".join(
                        chunk["text"]
                        for chunk in document_chunks
                    ),
                    source_path=first_chunk["source_path"],
                    updated_at=first_chunk["updated_at"],
                )

                existing_document = db.get(
                    Document,
                    document.document_id,
                )

                if existing_document:
                    existing_document.title = document.title
                    existing_document.content = document.content
                    existing_document.source_path = (
                        document.source_path
                    )
                    existing_document.updated_at = (
                        document.updated_at
                    )
                else:
                    db.add(document)

                db.commit()

                log_event(
                    db=db,
                    document_id=document_id,
                    event_type="COMPLETED",
                    status="SUCCESS",
                )

                completed_documents.add(document_id)

            except Exception as error:
                db.rollback()

                failed_document_ids[document_id] = str(error)

                log_event(
                    db=db,
                    document_id=document_id,
                    event_type="FAILED",
                    status="FAILED",
                    error_message=str(error),
                )

        for document_id, error_message in failed_document_ids.items():
            if document_id not in completed_documents:
                log_event(
                    db=db,
                    document_id=document_id,
                    event_type="FAILED",
                    status="FAILED",
                    error_message=error_message,
                )

        return {
            "processed_documents": processed_documents,
            "completed_documents": len(
                completed_documents
            ),
            "failed_documents": len(
                failed_document_ids
            ),
            "chunks": len(chunks),
            "indexed_chunks": collection.count(),
        }

    finally:
        db.close()