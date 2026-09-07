import json
import time
from pathlib import Path

from app.rag.query_rewriter import rewrite_query
from app.rag.retrieve import retrieve_documents
from app.rag.reranker import rerank_documents


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "datasets" / "day6_retrieval_test_cases.json"
OUTPUT_PATH = PROJECT_ROOT / "results" / "day10_reranker_results.json"

INITIAL_TOP_K = 5
FINAL_TOP_K = 3
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

    total_retrieval_latency = 0.0
    total_reranking_latency = 0.0

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_document_id = test_case["expected_document_id"]

        retrieval_query = rewrite_query(question)

        retrieval_start = time.perf_counter()

        retrieved_documents = retrieve_documents(
            query=retrieval_query,
            top_k=INITIAL_TOP_K,
            min_score=MIN_SCORE,
            where=WHERE,
        )

        retrieval_latency_ms = round(
            (time.perf_counter() - retrieval_start) * 1000,
            2,
        )

        reranking_start = time.perf_counter()

        reranked_documents = rerank_documents(
            question=question,
            documents=retrieved_documents,
            top_k=FINAL_TOP_K,
        )

        reranking_latency_ms = round(
            (time.perf_counter() - reranking_start) * 1000,
            2,
        )

        total_latency_ms = round(
            retrieval_latency_ms + reranking_latency_ms,
            2,
        )

        total_retrieval_latency += retrieval_latency_ms
        total_reranking_latency += reranking_latency_ms

        expected_rank = find_expected_rank(
            reranked_documents,
            expected_document_id,
        )

        hit_at_1 = expected_rank == 1
        hit_at_3 = expected_rank is not None and expected_rank <= 3
        rr = reciprocal_rank(expected_rank)

        retrieved_results = []

        for result in reranked_documents:
            retrieved_results.append(
                {
                    "rank": result.get("rank"),
                    "original_rank": result.get("original_rank"),
                    "document_id": result.get("document_id"),
                    "chunk_id": result.get("chunk_id"),
                    "original_score": result.get("original_score"),
                    "rerank_score": result.get("rerank_score"),
                    "title": result.get("title"),
                    "source_path": result.get("source_path"),
                }
            )

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
                "retrieval_latency_ms": retrieval_latency_ms,
                "reranking_latency_ms": reranking_latency_ms,
                "total_latency_ms": total_latency_ms,
                "retrieved_documents": retrieved_results,
            }
        )

        status = "PASS" if hit_at_1 else "CHECK"

        print(
            f"Q{index:02d} | {status} | "
            f"Expected: {expected_document_id} | "
            f"Final Rank: {expected_rank} | "
            f"Rewritten: {retrieval_query != question} | "
            f"Retrieval: {retrieval_latency_ms} ms | "
            f"Rerank: {reranking_latency_ms} ms"
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
        ) / total_questions
        if total_questions
        else 0.0
    )

    average_retrieval_latency = (
        total_retrieval_latency / total_questions
        if total_questions
        else 0.0
    )

    average_reranking_latency = (
        total_reranking_latency / total_questions
        if total_questions
        else 0.0
    )

    average_total_latency = (
        (
            total_retrieval_latency
            + total_reranking_latency
        ) / total_questions
        if total_questions
        else 0.0
    )

    report = {
        "evaluation": "Day 10 reranker",
        "configuration": {
            "rewriter": "app.rag.query_rewriter.rewrite_query",
            "initial_top_k": INITIAL_TOP_K,
            "final_top_k": FINAL_TOP_K,
            "min_score": MIN_SCORE,
            "metadata_filter": WHERE,
            "reranker_model": (
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            ),
        },
        "metrics": {
            "total_questions": total_questions,
            "hit_at_1": (
                round(
                    hit_at_1_count / total_questions,
                    4,
                )
                if total_questions
                else 0.0
            ),
            "hit_at_3": (
                round(
                    hit_at_3_count / total_questions,
                    4,
                )
                if total_questions
                else 0.0
            ),
            "mrr": round(mrr, 4),
            "average_retrieval_latency_ms": round(
                average_retrieval_latency,
                2,
            ),
            "average_reranking_latency_ms": round(
                average_reranking_latency,
                2,
            ),
            "average_total_latency_ms": round(
                average_total_latency,
                2,
            ),
        },
        "question_results": question_results,
    }

    return report


def save_report(report: dict) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    print("=" * 60)
    print("DAY 10 RERANKER EVALUATION")
    print("=" * 60)
    print()

    report = run_evaluation()

    save_report(report)

    print()
    print("Metrics:")
    print("-" * 60)

    metrics = report["metrics"]

    print(f"Total Questions       : {metrics['total_questions']}")
    print(f"Hit@1                 : {metrics['hit_at_1']}")
    print(f"Hit@3                 : {metrics['hit_at_3']}")
    print(f"MRR                   : {metrics['mrr']}")
    print(
        "Average Retrieval     : "
        f"{metrics['average_retrieval_latency_ms']} ms"
    )
    print(
        "Average Reranking     : "
        f"{metrics['average_reranking_latency_ms']} ms"
    )
    print(
        "Average Total         : "
        f"{metrics['average_total_latency_ms']} ms"
    )

    print()
    print(f"Saved report: {OUTPUT_PATH}")
    print()
    print("DAY 10 RERANKER EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()