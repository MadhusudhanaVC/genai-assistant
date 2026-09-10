from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ask_validation_empty_question():
    response = client.post(
        "/ask",
        json={
            "question": "",
            "top_k": 3,
            "min_score": None,
        },
    )

    assert response.status_code == 422


def test_ask_validation_invalid_top_k():
    response = client.post(
        "/ask",
        json={
            "question": "What is Python?",
            "top_k": 0,
            "min_score": None,
        },
    )

    assert response.status_code == 422


def test_ask_validation_invalid_min_score():
    response = client.post(
        "/ask",
        json={
            "question": "What is Python?",
            "top_k": 3,
            "min_score": 2,
        },
    )

    assert response.status_code == 422


def test_document_not_found():
    response = client.get("/documents/UNKNOWN_DOCUMENT")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_ask_success(monkeypatch):
    def fake_generate_grounded_answer(question, top_k, min_score):
        return {
            "answer": "Python is a general-purpose programming language.",
            "status": "answered",
            "citations": ["[DOC001 | DOC001_CHUNK_001]"],
            "sources": [
                {
                    "chunk_id": "DOC001_CHUNK_001",
                    "document_id": "DOC001",
                    "title": "Python Basics",
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.routes.generate_grounded_answer",
        fake_generate_grounded_answer,
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is Python?",
            "top_k": 3,
            "min_score": None,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "answered"
    assert data["answer"] == "Python is a general-purpose programming language."
    assert data["citations"] == ["[DOC001 | DOC001_CHUNK_001]"]
    assert len(data["sources"]) == 1


def test_ingest_success(monkeypatch):
    def fake_ingest_documents():
        return {
            "processed_documents": 30,
            "completed_documents": 30,
            "failed_documents": 0,
            "chunks": 47,
            "indexed_chunks": 47,
        }

    monkeypatch.setattr(
        "app.api.routes.ingest_documents",
        fake_ingest_documents,
    )

    response = client.post("/ingest")

    assert response.status_code == 200

    data = response.json()

    assert data["processed_documents"] == 30
    assert data["completed_documents"] == 30
    assert data["failed_documents"] == 0
    assert data["chunks"] == 47
    assert data["indexed_chunks"] == 47
    assert data["status"] == "completed"


def test_document_success(monkeypatch):
    class FakeDocument:
        document_id = "DOC001"
        title = "Python Basics"
        content = "Python is a general-purpose programming language."
        source_path = "sample_data/DOC001_python_basics.md"
        updated_at = "2026-08-10"

    def fake_get_document(db, document_id):
        return FakeDocument()

    monkeypatch.setattr(
        "app.api.routes.get_document",
        fake_get_document,
    )

    response = client.get("/documents/DOC001")

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == "DOC001"
    assert data["title"] == "Python Basics"
    assert data["status"] == "completed"