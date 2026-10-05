
import pytest

import app.rag.generate as grounded_generation


def _valid_retrieved_result():
    """Return a reusable, valid evidence chunk for tests."""
    return {
        "document_id": "DOC001",
        "chunk_id": "DOC001_CHUNK_001",
        "title": "Python Basics",
        "source_path": "docs/python.md",
        "text": "A Python variable stores a value.",
        "score": 0.82,
    }


def _mock_retrieval(monkeypatch, retrieved_results):
    """Replace document retrieval with predictable test evidence."""
    monkeypatch.setattr(
        grounded_generation,
        "retrieve_documents",
        lambda query, top_k=3, min_score=None: retrieved_results,
    )


def _mock_generation(monkeypatch, response_text):
    """Replace the LLM with a predictable response."""
    def fake_generate_response(prompt, system_prompt=None):
        assert system_prompt is not None
        assert isinstance(prompt, str)

        return {
            "model": "test-model",
            "latency_seconds": 0.01,
            "text": response_text,
        }

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        fake_generate_response,
    )


def test_answerable_question_returns_cited_answer(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]

    _mock_retrieval(monkeypatch, retrieved_results)
    _mock_generation(
        monkeypatch,
        (
            '{"answer":"A Python variable stores a value.",'
            '"status":"answered",'
            '"citations":["[DOC001 | DOC001_CHUNK_001]"]}'
        ),
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "answered"
    assert result["answer"] == "A Python variable stores a value."
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

    _mock_retrieval(monkeypatch, retrieved_results)
    _mock_generation(
        monkeypatch,
        (
            '{"answer":"Python functions are reusable blocks '
            'of code that perform a specific task. The provided '
            'context does not contain additional details.",'
            '"status":"answered",'
            '"citations":["[DOC002 | DOC002_CHUNK_001]"]}'
        ),
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
    _mock_retrieval(monkeypatch, [])

    def unexpected_generation(prompt, system_prompt=None):
        raise AssertionError(
            "LLM should not be called when there is no evidence."
        )

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        unexpected_generation,
    )

    result = grounded_generation.generate_grounded_answer(
        "What is the capital of Mars?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["citations"] == []
    assert result["sources"] == []
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE


def test_missing_document_id_abstains(monkeypatch):
    retrieved_results = [
        {
            "chunk_id": "CHUNK001",
            "text": "A Python variable stores a value.",
            "score": 0.82,
        }
    ]

    _mock_retrieval(monkeypatch, retrieved_results)

    def unexpected_generation(prompt, system_prompt=None):
        raise AssertionError(
            "LLM should not be called when evidence has no document ID."
        )

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        unexpected_generation,
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []
    assert result["sources"] == []


def test_empty_evidence_text_abstains(monkeypatch):
    retrieved_results = [
        {
            "document_id": "DOC001",
            "chunk_id": "CHUNK001",
            "text": "   ",
            "score": 0.82,
        }
    ]

    _mock_retrieval(monkeypatch, retrieved_results)

    def unexpected_generation(prompt, system_prompt=None):
        raise AssertionError(
            "LLM should not be called when evidence text is empty."
        )

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        unexpected_generation,
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []
    assert result["sources"] == []



def test_malformed_llm_output_returns_safe_fallback(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]

    _mock_retrieval(monkeypatch, retrieved_results)
    _mock_generation(
        monkeypatch,
        "This is not valid JSON",
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []
    assert result["sources"] == retrieved_results

def test_invalid_citation_is_converted_to_abstention(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]

    _mock_retrieval(monkeypatch, retrieved_results)
    _mock_generation(
        monkeypatch,
        (
            '{"answer":"A Python variable stores a value.",'
            '"status":"answered",'
            '"citations":["[UNKNOWN | UNKNOWN_CHUNK]"]}'
        ),
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []


def test_answered_response_without_citations_abstains(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]

    _mock_retrieval(monkeypatch, retrieved_results)
    _mock_generation(
        monkeypatch,
        (
            '{"answer":"A Python variable stores a value.",'
            '"status":"answered",'
            '"citations":[]}'
        ),
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []

def test_missing_response_text_returns_safe_fallback(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]
    _mock_retrieval(monkeypatch, retrieved_results)

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        lambda prompt, system_prompt=None: {
            "model": "test-model",
            "latency_seconds": 0.01,
        },
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []


def test_non_dictionary_response_returns_safe_fallback(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]
    _mock_retrieval(monkeypatch, retrieved_results)

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        lambda prompt, system_prompt=None: "unexpected response",
    )

    result = grounded_generation.generate_grounded_answer(
        "What is a Python variable?"
    )

    assert result["status"] == "insufficient_evidence"
    assert result["answer"] == grounded_generation.ABSTENTION_MESSAGE
    assert result["citations"] == []


def test_api_exception_is_reraised(monkeypatch):
    retrieved_results = [_valid_retrieved_result()]
    _mock_retrieval(monkeypatch, retrieved_results)

    def raise_api_error(prompt, system_prompt=None):
        raise RuntimeError("Simulated API failure")

    monkeypatch.setattr(
        grounded_generation,
        "generate_response",
        raise_api_error,
    )

    with pytest.raises(RuntimeError, match="Simulated API failure"):
        grounded_generation.generate_grounded_answer(
            "What is a Python variable?"
        )