import app.rag.generate as grounded_generation


def test_answerable_question_returns_cited_answer(monkeypatch):
    retrieved_results = [
        {
            "document_id": "DOC001",
            "chunk_id": "DOC001_CHUNK_001",
            "title": "Python Basics",
            "source_path": "docs/python.md",
            "text": "A Python variable stores a value.",
            "score": 0.82,
        }
    ]

    def fake_retrieve_documents(
        query,
        top_k=3,
        min_score=None,
    ):
        return retrieved_results

    def fake_generate_response(prompt):
        return {
            "model": "test-model",
            "latency_seconds": 0.01,
            "text": (
                '{"answer":"A Python variable stores a value.",'
                '"status":"answered",'
                '"citations":["[DOC001 | DOC001_CHUNK_001]"]}'
            ),
        }

    monkeypatch.setattr(
        grounded_generation,
        "retrieve_documents",
        fake_retrieve_documents,
    )

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        fake_generate_response,
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "answered"

    assert result["answer"] == (
        "A Python variable stores a value."
    )

    assert result["citations"] == [
        "[DOC001 | DOC001_CHUNK_001]"
    ]

    assert result["sources"] == retrieved_results


def test_partially_answerable_question_uses_supported_evidence(
    monkeypatch,
):
    retrieved_results = [
        {
            "document_id": "DOC002",
            "chunk_id": "DOC002_CHUNK_001",
            "title": "Python Functions",
            "source_path": "docs/python_functions.md",
            "text": (
                "Python functions are reusable blocks of code "
                "that perform a specific task."
            ),
            "score": 0.79,
        }
    ]

    def fake_retrieve_documents(
        query,
        top_k=3,
        min_score=None,
    ):
        return retrieved_results

    def fake_generate_response(prompt):
        return {
            "model": "test-model",
            "latency_seconds": 0.01,
            "text": (
                '{"answer":"Python functions are reusable blocks '
                'of code that perform a specific task. The provided '
                'context does not contain additional details.",'
                '"status":"answered",'
                '"citations":["[DOC002 | DOC002_CHUNK_001]"]}'
            ),
        }

    monkeypatch.setattr(
        grounded_generation,
        "retrieve_documents",
        fake_retrieve_documents,
    )

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        fake_generate_response,
    )

    result = grounded_generation.generate_grounded_answer(
        "What are Python functions and who created them?"
    )

    assert result["status"] == "answered"

    assert "reusable blocks of code" in result["answer"]

    assert result["citations"] == [
        "[DOC002 | DOC002_CHUNK_001]"
    ]


def test_unanswerable_question_abstains(monkeypatch):
    def fake_retrieve_documents(
        query,
        top_k=3,
        min_score=None,
    ):
        return []

    def fake_generate_response(prompt):
        raise AssertionError(
            "LLM should not be called when there is no evidence."
        )

    monkeypatch.setattr(
        grounded_generation,
        "retrieve_documents",
        fake_retrieve_documents,
    )

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        fake_generate_response,
    )

    result = grounded_generation.generate_grounded_answer(
        "What is the capital of Mars?"
    )

    assert result["status"] == "insufficient_evidence"

    assert result["citations"] == []

    assert result["sources"] == []

    assert result["answer"] == (
        grounded_generation.ABSTENTION_MESSAGE
    )