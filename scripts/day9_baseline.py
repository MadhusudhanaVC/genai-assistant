import json
import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT / IMPORT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.rag.retrieve import retrieve_documents


# ============================================================
# DAY 9 — FROZEN BASELINE CONFIGURATION
# ============================================================

TOP_K = 3
MIN_SCORE = None
WHERE = None

DATASET_PATH = PROJECT_ROOT / "datasets" / "day6_retrieval_test_cases.json"
OUTPUT_PATH = PROJECT_ROOT / "results" / "day9_baseline_metrics.json"


# ============================================================
# LOAD FIXED EVALUATION DATASET
# ============================================================

def load_test_cases() -> list[dict]:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# CALCULATE RECIPROCAL RANK
# ============================================================

def reciprocal_rank(rank: int | None) -> float:
    if rank is None:
        return 0.0

    return round(1.0 / rank, 4)


# ============================================================
# RUN BASELINE RETRIEVAL
# ============================================================

def run_baseline() -> dict:
    test_cases = load_test_cases()

    question_results = []

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_document_id = test_case["expected_document_id"]

        results = retrieve_documents(
            query=question,
            top_k=TOP_K,
            min_score=MIN_SCORE,
            where=WHERE,
        )

        retrieved_documents = [
            {
                "rank": rank,
                "document_id": result.get("document_id"),
                "chunk_id": result.get("chunk_id"),
                "score": result.get("score"),
                "title": result.get("title"),
                "source_path": result.get("source_path"),
            }
            for rank, result in enumerate(results, start=1)
        ]

        expected_rank = None

        for result in retrieved_documents:
            if result["document_id"] == expected_document_id:
                expected_rank = result["rank"]
                break

        hit_at_1 = expected_rank == 1
        hit_at_3 = (
            expected_rank is not None
            and expected_rank <= TOP_K
        )

        result_record = {
            "question_number": index,
            "question": question,
            "expected_document_id": expected_document_id,
            "expected_rank": expected_rank,
            "hit_at_1": hit_at_1,
            "hit_at_3": hit_at_3,
            "reciprocal_rank": reciprocal_rank(expected_rank),
            "retrieved_documents": retrieved_documents,
        }

        question_results.append(result_record)

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

    report = {
        "baseline_configuration": {
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_normalization": True,
            "embedding_dimension": 384,
            "chunk_size": 500,
            "chunk_overlap": 80,
            "top_k": TOP_K,
            "min_score": MIN_SCORE,
            "metadata_filter": WHERE,
            "collection_name": "day6_chunks",
            "chroma_path": "results/chroma_db",
            "evaluation_dataset": str(
                DATASET_PATH.relative_to(PROJECT_ROOT)
            ),
            "prompt_file": "prompts/grounded_answer.txt",
            "prompt_version": "current Day 8 grounded-answer template",
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
        },
        "question_results": question_results,
    }

    return report


# ============================================================
# SAVE BASELINE REPORT
# ============================================================

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
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("=" * 60)
    print("DAY 9 BASELINE RETRIEVAL MEASUREMENT")
    print("=" * 60)

    print()
    print("Frozen configuration:")
    print(f"Embedding model : all-MiniLM-L6-v2")
    print(f"Chunk size      : 500")
    print(f"Chunk overlap   : 80")
    print(f"Top-K           : {TOP_K}")
    print(f"Minimum score   : {MIN_SCORE}")
    print(f"Metadata filter : {WHERE}")

    report = run_baseline()
    save_report(report)

    print()
    print("Per-question baseline results:")
    print("-" * 60)

    for result in report["question_results"]:
        rank = result["expected_rank"]

        rank_display = (
            rank
            if rank is not None
            else "NOT FOUND"
        )

        print(
            f"Q{result['question_number']:02d} | "
            f"Expected: {result['expected_document_id']} | "
            f"Rank: {rank_display} | "
            f"Hit@1: {result['hit_at_1']} | "
            f"Hit@3: {result['hit_at_3']} | "
            f"RR: {result['reciprocal_rank']}"
        )

    print()
    print("Baseline metrics:")
    print("-" * 60)

    metrics = report["metrics"]

    print(
        f"Total Questions : "
        f"{metrics['total_questions']}"
    )

    print(
        f"Hit@1           : "
        f"{metrics['hit_at_1']}"
    )

    print(
        f"Hit@3           : "
        f"{metrics['hit_at_3']}"
    )

    print(
        f"MRR             : "
        f"{metrics['mrr']}"
    )

    print()
    print(f"Saved report: {OUTPUT_PATH}")
    print()
    print("DAY 9 BASELINE MEASUREMENT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()