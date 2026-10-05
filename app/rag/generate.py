
from pathlib import Path

from app.llm.client import generate_response
from app.llm.validator import validate_response
from app.rag.retrieve import retrieve_documents
from app.rag.query_rewriter import rewrite_query
from app.rag.reranker import rerank_documents


DEFAULT_MAX_CONTEXT_CHUNKS = 3
DEFAULT_MAX_CONTEXT_CHARACTERS = 6000
DEFAULT_INITIAL_RETRIEVAL_K = 5
PROMPT_VERSION = "v2"

ABSTENTION_MESSAGE = (
    "There is not enough evidence in the provided documents to answer this question."
)


def prepare_context(
    results: list[dict],
    max_chunks: int = DEFAULT_MAX_CONTEXT_CHUNKS,
    max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
) -> str:
    if max_chunks <= 0:
        raise ValueError("max_chunks must be greater than zero")

    if max_characters <= 0:
        raise ValueError("max_characters must be greater than zero")

    context_parts = []
    seen_chunks = set()
    total_characters = 0

    for result in results:
        chunk_id = result.get("chunk_id")

        if not chunk_id or chunk_id in seen_chunks:
            continue

        text = result.get("text", "").strip()

        if not text:
            continue

        if len(context_parts) >= max_chunks:
            break

        source_path = result.get("source_path") or "unknown"
        document_id = result.get("document_id") or "unknown"
        title = result.get("title") or "Untitled"

        source_label = f"[{document_id} | {chunk_id}]"

        block = (
            f"{source_label}\n"
            f"Title: {title}\n"
            f"Source: {source_path}\n\n"
            f"{text}"
        )

        remaining = max_characters - total_characters

        if remaining <= 0:
            break

        if len(block) > remaining:
            block = block[:remaining].rstrip()

        context_parts.append(block)
        seen_chunks.add(chunk_id)
        total_characters += len(block)

        if total_characters >= max_characters:
            break

    return "\n\n---\n\n".join(context_parts)


def filter_usable_evidence(results: list[dict]) -> list[dict]:
    """Keep only evidence chunks with valid IDs and non-empty text."""
    usable_results = []
    seen_chunks = set()

    for result in results:
        document_id = result.get("document_id")
        chunk_id = result.get("chunk_id")
        text = result.get("text")

        if not isinstance(document_id, str) or not document_id.strip():
            continue

        if not isinstance(chunk_id, str) or not chunk_id.strip():
            continue

        if not isinstance(text, str) or not text.strip():
            continue

        if chunk_id in seen_chunks:
            continue

        usable_results.append(result)
        seen_chunks.add(chunk_id)

    return usable_results


def build_system_prompt() -> str:
    prompt_path = Path("prompts/grounded_answer.txt")

    prompt_template = prompt_path.read_text(encoding="utf-8")

    rules_start = prompt_template.index(
        "You are a grounded question-answering assistant."
    )

    user_question_marker = "\nUser question\n=============="

    rules = prompt_template[
        rules_start:prompt_template.index(user_question_marker)
    ]

    return rules.strip()


def build_grounded_prompt(
    question: str,
    context: str,
) -> str:
    prompt_path = Path("prompts/grounded_answer.txt")

    prompt_template = prompt_path.read_text(encoding="utf-8")

    user_question_marker = "\nUser question\n=============="

    user_template = prompt_template[
        prompt_template.index(user_question_marker)
        + len(user_question_marker):
    ]

    user_template = user_template.replace("{question}", question)
    user_template = user_template.replace("{context}", context)

    return user_template.strip()


def validate_citations(
    citations: list[str],
    results: list[dict],
) -> list[str]:
    valid_citations = {
        f"[{result.get('document_id')} | {result.get('chunk_id')}]"
        for result in results
        if result.get("document_id") and result.get("chunk_id")
    }

    return [
        citation
        for citation in citations
        if citation in valid_citations
    ]


def build_grounded_result(
    answer: str,
    status: str,
    citations: list[str],
    results: list[dict],
) -> dict:
    validated_citations = validate_citations(
        citations=citations,
        results=results,
    )

    if status == "answered" and not validated_citations:
        status = "insufficient_evidence"
        answer = ABSTENTION_MESSAGE

    if status == "insufficient_evidence":
        validated_citations = []

    return {
        "answer": answer,
        "status": status,
        "citations": validated_citations,
        "sources": results,
    }


def build_abstention_result(results: list[dict]) -> dict:
    """Return a consistent safe response when output validation fails."""
    return {
        "answer": ABSTENTION_MESSAGE,
        "status": "insufficient_evidence",
        "citations": [],
        "sources": results,
    }


def generate_grounded_answer(
    question: str,
    top_k: int = 3,
    min_score: float | None = None,
    max_chunks: int = DEFAULT_MAX_CONTEXT_CHUNKS,
    max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
    stage_logger=None,
) -> dict:
    if not question or not question.strip():
        raise ValueError("question cannot be empty")

    retrieval_query = rewrite_query(question)

    if stage_logger:
        stage_logger("RETRIEVAL", "STARTED")

    try:
        retrieved_documents = retrieve_documents(
            query=retrieval_query,
            top_k=max(top_k, DEFAULT_INITIAL_RETRIEVAL_K),
            min_score=min_score,
        )
    except Exception:
        if stage_logger:
            stage_logger("RETRIEVAL", "FAILED")
        raise

    if stage_logger:
        stage_logger("RETRIEVAL", "SUCCESS")

    if len(retrieved_documents) > 1:
        results = rerank_documents(
            question=question,
            documents=retrieved_documents,
            top_k=top_k,
        )
    else:
        results = retrieved_documents

    clean_results = []

    for result in results:
        clean_result = result.copy()

        clean_result.pop("original_rank", None)
        clean_result.pop("original_score", None)
        clean_result.pop("rerank_score", None)
        clean_result.pop("rank", None)

        clean_results.append(clean_result)

    # Reject malformed evidence before building the LLM context.
    clean_results = filter_usable_evidence(clean_results)

    # Abstain without calling the LLM if no usable evidence remains.
    if not clean_results:
        return build_abstention_result([])

    context = prepare_context(
        clean_results,
        max_chunks=max_chunks,
        max_characters=max_characters,
    )

    if not context:
        return build_abstention_result([])

    prompt = build_grounded_prompt(
        question=question,
        context=context,
    )

    system_prompt = build_system_prompt()

    if stage_logger:
        stage_logger("GENERATION", "STARTED")

    # Keep actual model/API failures distinguishable from invalid output.
    try:
        response = generate_response(
            prompt,
            system_prompt=system_prompt,
        )
    except Exception:
        if stage_logger:
            stage_logger("GENERATION", "FAILED")
        raise

    # Validate the returned response structure before reading its text.
    if not isinstance(response, dict):
        if stage_logger:
            stage_logger("GENERATION", "FAILED")
        return build_abstention_result(clean_results)

    response_text = response.get("text")

    if not isinstance(response_text, str) or not response_text.strip():
        if stage_logger:
            stage_logger("GENERATION", "FAILED")
        return build_abstention_result(clean_results)

    # Treat schema-invalid output as a controlled abstention.
    try:
        is_valid, validated, error = validate_response(
            "grounded_answer",
            response_text,
        )
    except Exception:
        if stage_logger:
            stage_logger("GENERATION", "FAILED")
        return build_abstention_result(clean_results)

    if not is_valid:
        if stage_logger:
            stage_logger("GENERATION", "FAILED")
        return build_abstention_result(clean_results)

    if stage_logger:
        stage_logger("GENERATION", "SUCCESS")

    # Validate citations before returning the answer.
    return build_grounded_result(
        answer=validated.answer,
        status=validated.status,
        citations=validated.citations,
        results=clean_results,
    )