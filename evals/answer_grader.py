from __future__ import annotations

import re


def grade_answerability(
    expected_answerability: str,
    actual_status: str | None,
    error: dict | None = None,
) -> dict:
    """Grade whether the system returned the expected answerability status."""

    if error is not None:
        return {
            "passed": False,
            "expected": expected_answerability,
            "actual": actual_status,
            "failure_category": "evaluation_error",
        }

    if actual_status is None:
        return {
            "passed": False,
            "expected": expected_answerability,
            "actual": None,
            "failure_category": "missing_answer_status",
        }

    if expected_answerability == "answerable":
        passed = actual_status == "answered"

    elif expected_answerability == "unanswerable":
        passed = actual_status == "insufficient_evidence"

    elif expected_answerability == "ambiguous":
        passed = actual_status in {
            "answered",
            "insufficient_evidence",
        }

    else:
        passed = False

    return {
        "passed": passed,
        "expected": expected_answerability,
        "actual": actual_status,
        "failure_category": (
            None
            if passed
            else "answerability_mismatch"
        ),
    }


def grade_citation_presence(
    expected_answerability: str,
    actual_status: str | None,
    actual_citations: list[str],
) -> dict:
    """Check whether citations are present when an answer is provided."""

    if actual_status == "insufficient_evidence":
        passed = len(actual_citations) == 0

        return {
            "passed": passed,
            "required": False,
            "actual_count": len(actual_citations),
            "failure_category": (
                None
                if passed
                else "unexpected_citations_on_abstention"
            ),
        }

    if actual_status == "answered":
        passed = len(actual_citations) > 0

        return {
            "passed": passed,
            "required": True,
            "actual_count": len(actual_citations),
            "failure_category": (
                None
                if passed
                else "missing_citations"
            ),
        }

    return {
        "passed": True,
        "required": False,
        "actual_count": len(actual_citations),
        "failure_category": None,
    }


def extract_citation_pairs(
    actual_citations: list[str],
) -> list[tuple[str, str]]:
    """Extract document and chunk IDs from citation strings."""

    citations = []

    for citation in actual_citations:
        if not isinstance(citation, str):
            continue

        cleaned = citation.strip()

        if not (
            cleaned.startswith("[")
            and cleaned.endswith("]")
        ):
            continue

        content = cleaned[1:-1]

        parts = [
            part.strip()
            for part in content.split("|")
        ]

        if len(parts) != 2:
            continue

        document_id, chunk_id = parts

        if document_id and chunk_id:
            citations.append(
                (document_id, chunk_id)
            )

    return citations


def grade_citation_validity(
    actual_citations: list[str],
    retrieval_results: list[dict],
) -> dict:
    """Check whether generated citations refer to retrieved sources."""

    if not actual_citations:
        return {
            "passed": True,
            "checked": 0,
            "valid": 0,
            "invalid": 0,
            "failure_category": None,
        }

    retrieved_pairs = {
        (
            result.get("document_id"),
            result.get("chunk_id"),
        )
        for result in retrieval_results
        if result.get("document_id")
        and result.get("chunk_id")
    }

    parsed_citations = extract_citation_pairs(
        actual_citations
    )

    if len(parsed_citations) != len(actual_citations):
        invalid_count = (
            len(actual_citations)
            - len(parsed_citations)
        )

        valid_count = sum(
            citation in retrieved_pairs
            for citation in parsed_citations
        )

        return {
            "passed": False,
            "checked": len(actual_citations),
            "valid": valid_count,
            "invalid": invalid_count
            + (len(parsed_citations) - valid_count),
            "failure_category": "invalid_citation_format",
        }

    valid_count = sum(
        citation in retrieved_pairs
        for citation in parsed_citations
    )

    invalid_count = (
        len(parsed_citations) - valid_count
    )

    passed = invalid_count == 0

    return {
        "passed": passed,
        "checked": len(parsed_citations),
        "valid": valid_count,
        "invalid": invalid_count,
        "failure_category": (
            None
            if passed
            else "invalid_citation"
        ),
    }


def normalize_text(text: str) -> set[str]:
    """Normalize text into meaningful lowercase words."""

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "use",
        "used",
        "what",
        "when",
        "where",
        "which",
        "with",
    }

    return {
        word
        for word in words
        if word not in stop_words
    }


def grade_required_facts(expected_facts: list[str], actual_answer: str | None) -> dict:
    if not expected_facts:
        return {
            "passed": True,
            "required": False,
            "total_facts": 0,
            "matched_facts": 0,
            "missing_facts": [],
            "failure_category": None,
        }

    if not actual_answer:
        return {
            "passed": False,
            "required": True,
            "total_facts": len(expected_facts),
            "matched_facts": 0,
            "missing_facts": expected_facts,
            "failure_category": "missing_required_facts",
        }

    normalized_answer = " ".join(actual_answer.lower().split())

    matched_facts = 0
    missing_facts = []

    for fact in expected_facts:
        normalized_fact = " ".join(fact.lower().split())

        if normalized_fact in normalized_answer:
            matched_facts += 1
        else:
            missing_facts.append(fact)

    passed = matched_facts == len(expected_facts)

    return {
        "passed": passed,
        "required": True,
        "total_facts": len(expected_facts),
        "matched_facts": matched_facts,
        "missing_facts": missing_facts,
        "failure_category": None if passed else "missing_required_facts",
    }

    answer_words = normalize_text(actual_answer)

    matched_facts = 0
    missing_facts = []

    for fact in expected_facts:
        fact_words = normalize_text(fact)

        if not fact_words:
            continue

        overlap = (
            len(answer_words & fact_words)
            / len(fact_words)
        )

        if overlap >= 0.60:
            matched_facts += 1
        else:
            missing_facts.append(fact)

    passed = matched_facts == len(expected_facts)

    return {
        "passed": passed,
        "required": True,
        "total_facts": len(expected_facts),
        "matched_facts": matched_facts,
        "missing_facts": missing_facts,
        "failure_category": (
            None
            if passed
            else "missing_required_facts"
        ),
    }


def grade_answer(
    expected_answerability: str,
    actual_status: str | None,
    actual_citations: list[str],
    retrieval_results: list[dict],
    actual_answer: str | None = None,
    expected_facts: list[str] | None = None,
    error: dict | None = None,
) -> dict:
    """Run deterministic answer-quality checks for one case."""

    if expected_facts is None:
        expected_facts = []

    answerability = grade_answerability(
        expected_answerability=expected_answerability,
        actual_status=actual_status,
        error=error,
    )

    citation_presence = grade_citation_presence(
        expected_answerability=expected_answerability,
        actual_status=actual_status,
        actual_citations=actual_citations,
    )

    citation_validity = grade_citation_validity(
        actual_citations=actual_citations,
        retrieval_results=retrieval_results,
    )

    required_facts = grade_required_facts(
        expected_facts=expected_facts,
        actual_answer=actual_answer,
    )

    passed = (
        answerability["passed"]
        and citation_presence["passed"]
        and citation_validity["passed"]
        and required_facts["passed"]
    )

    return {
        "passed": passed,
        "answerability": answerability,
        "citation_presence": citation_presence,
        "citation_validity": citation_validity,
        "required_facts": required_facts,
    }