from __future__ import annotations


def calculate_hit_rate(expected_source_ids: list[str], retrieved_results: list[dict]) -> float:
    """Return 1.0 if at least one expected source was retrieved, otherwise 0.0."""
    expected_sources = set(expected_source_ids)
    retrieved_sources = {
        result.get("document_id")
        for result in retrieved_results
        if result.get("document_id")
    }

    return 1.0 if expected_sources & retrieved_sources else 0.0


def calculate_recall_at_k(
    expected_source_ids: list[str],
    retrieved_results: list[dict],
) -> float:
    """Return the fraction of expected sources retrieved in the top-k results."""
    expected_sources = set(expected_source_ids)

    if not expected_sources:
        return 0.0

    retrieved_sources = {
        result.get("document_id")
        for result in retrieved_results
        if result.get("document_id")
    }

    retrieved_expected = expected_sources & retrieved_sources

    return len(retrieved_expected) / len(expected_sources)


def calculate_mrr(
    expected_source_ids: list[str],
    retrieved_results: list[dict],
) -> float:
    """Return reciprocal rank of the first expected source."""
    expected_sources = set(expected_source_ids)

    if not expected_sources:
        return 0.0

    for rank, result in enumerate(retrieved_results, start=1):
        document_id = result.get("document_id")

        if document_id in expected_sources:
            return 1.0 / rank

    return 0.0


def grade_retrieval(
    expected_source_ids: list[str],
    retrieved_results: list[dict],
) -> dict:
    """Calculate retrieval metrics for one evaluation case."""
    hit_rate = calculate_hit_rate(
        expected_source_ids,
        retrieved_results,
    )

    recall_at_k = calculate_recall_at_k(
        expected_source_ids,
        retrieved_results,
    )

    mrr = calculate_mrr(
        expected_source_ids,
        retrieved_results,
    )

    return {
        "hit_rate": hit_rate,
        "recall_at_k": recall_at_k,
        "mrr": mrr,
        "passed": hit_rate == 1.0,
    }