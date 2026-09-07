import json
import time
from pathlib import Path

from app.rag.query_rewriter import rewrite_query
from app.rag.retrieve import retrieve_documents


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "day6_retrieval_test_cases.json"
)

BASELINE_PATH = (
    PROJECT_ROOT
    / "results"
    / "day9_baseline_metrics.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "results"
    / "day10_query_rewrite_results.json"
)

TOP_K = 3
MIN_SCORE = None
WHERE = None


def load_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def reciprocal_rank(rank: int | None) -> float:
    if rank is None:
        return 0.0

    return round(1.0 / rank, 4)


def find_expected_rank(
    retrieved_documents: list[dict],
    expected_document_id: str,
) -> int | None:
    for result in retrieved_documents:
        if result["document_id"] == expected_document_id:
            return result["rank"]

    return None


def run_evaluation() -> dict:
    test_cases = load_json(DATASET_PATH)

    question_results = []

    total_latency = 0.0

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_document_id = test_case["expected_document_id"]

        retrieval_query = rewrite_query(question)

        start_time = time.perf_counter()

        retrieved = retrieve_documents(
            query=retrieval_query,
            top_k=TOP_K,
            min_score=MIN_SCORE,
            where=WHERE,
        )

        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        total_latency += latency_ms

        retrieved_documents = []

        for rank, result in enumerate(retrieved, start=1):
            retrieved_documents.append(
                {
                    "rank": rank,
                    "document_id": result.get("document_id"),
                    "chunk_id": result.get("chunk_id"),
                    "score": result.get("score"),
                    "title": result.get("title"),
                    "source_path": result.get("source_path"),
                }
            )

        expected_rank = find_expected_rank(
            retrieved_documents,
            expected_document_id,
        )

        hit_at_1 = expected_rank == 1

        hit_at_3 = (
            expected_rank is not None
            and expected_rank <= 3
        )

        rr = reciprocal_rank(expected_rank)

        question_results.append(
            {
                "question_number": index,
                "question": question,
                "retrieval_query": retrieval_query,
                "rewritten": retrieval_query != question,
                "expected_document_id": expected_document_id,
                "expected_rank": expected_rank,
                "hit_at_1": hit_at_1,
                "hit_at_3": hit_at_3,
                "reciprocal_rank": rr,
                "latency_ms": latency_ms,
                "retrieved_documents": retrieved_documents,
            }
        )

        status = "PASS" if hit_at_1 else "CHECK"

        print(
            f"Q{index:02d} | {status} | "
            f"Expected: {expected_document_id} | "
            f"Rank: {expected_rank} | "
            f"Rewritten: {retrieval_query != question} | "
            f"Latency: {latency_ms} ms"
        )

    total_questions = len(question_results)

    hit_at_1_count = sum(
        result["hit_at_1"]
        for result in question_results
    )

    hit_at_3_count = sum(
        result["hit_at_3"]
        for result in question_results
    )

    mrr = (
        sum(
            result["reciprocal_rank"]
            for result in question_results
        )
        / total_questions
        if total_questions
        else 0.0
    )

    average_latency = (
        total_latency / total_questions
        if total_questions
        else 0.0
    )

    report = {
        "evaluation": "Day 10 query rewriting",
        "configuration": {
            "top_k": TOP_K,
            "min_score": MIN_SCORE,
            "metadata_filter": WHERE,
            "rewriter": "app.rag.query_rewriter.rewrite_query",
        },
        "metrics": {
            "total_questions": total_questions,
            "hit_at_1": round(
                hit_at_1_count / total_questions,
                4,
            ) if total_questions else 0.0,
            "hit_at_3": round(
                hit_at_3_count / total_questions,
                4,
            ) if total_questions else 0.0,
            "mrr": round(mrr, 4),
            "average_latency_ms": round(
                average_latency,
                2,
            ),
            "total_latency_ms": round(
                total_latency,
                2,
            ),
        },
        "baseline_reference": str(
            BASELINE_PATH.relative_to(PROJECT_ROOT)
        ),
        "question_results": question_results,
    }

    return report


def save_report(report: dict) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    print("=" * 60)
    print("DAY 10 QUERY REWRITE EVALUATION")
    print("=" * 60)

    print()

    report = run_evaluation()

    save_report(report)

    print()
    print("Metrics:")
    print("-" * 60)

    metrics = report["metrics"]

    print(f"Total Questions : {metrics['total_questions']}")
    print(f"Hit@1           : {metrics['hit_at_1']}")
    print(f"Hit@3           : {metrics['hit_at_3']}")
    print(f"MRR             : {metrics['mrr']}")
    print(
        f"Average Latency : "
        f"{metrics['average_latency_ms']} ms"
    )

    print()
    print(f"Saved report: {OUTPUT_PATH}")
    print()
    print("DAY 10 QUERY REWRITE EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()