from pathlib import Path

from app.llm.client import generate_response
from app.llm.validator import validate_response
from app.rag.retrieve import retrieve_documents


DEFAULT_MAX_CONTEXT_CHUNKS = 3
DEFAULT_MAX_CONTEXT_CHARACTERS = 6000

ABSTENTION_MESSAGE = (
    "I don't have enough evidence in the "
    "provided documents to answer this question."
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


def build_grounded_prompt(
    question: str,
    context: str,
) -> str:
    prompt_path = Path("prompts/grounded_answer.txt")

    prompt_template = prompt_path.read_text(
        encoding="utf-8"
    )

    return prompt_template.format(
        question=question,
        context=context,
    )


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


def generate_grounded_answer(
    question: str,
    top_k: int = 3,
    min_score: float | None = None,
    max_chunks: int = DEFAULT_MAX_CONTEXT_CHUNKS,
    max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
) -> dict:
    if not question or not question.strip():
        raise ValueError("question cannot be empty")

    results = retrieve_documents(
        query=question,
        top_k=top_k,
        min_score=min_score,
    )

    context = prepare_context(
        results,
        max_chunks=max_chunks,
        max_characters=max_characters,
    )

    if not context:
        return {
            "answer": ABSTENTION_MESSAGE,
            "status": "insufficient_evidence",
            "citations": [],
            "sources": [],
        }

    prompt = build_grounded_prompt(
        question=question,
        context=context,
    )

    response = generate_response(prompt)

    is_valid, validated, error = validate_response(
        "grounded_answer",
        response["text"],
    )

    if not is_valid:
        raise ValueError(
            f"Invalid grounded answer response: {error}"
        )

    return build_grounded_result(
        answer=validated.answer,
        status=validated.status,
        citations=validated.citations,
        results=results,
    )