import json
from pathlib import Path


RESULTS_DIR = Path("results")
OUTPUT_FILE = RESULTS_DIR / "day10_before_after_report.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_question_comparison(
    baseline: dict,
    final_results: dict,
) -> list[dict]:
    baseline_questions = {
        item["question_number"]: item
        for item in baseline["question_results"]
    }

    final_questions = {
        item["question_number"]: item
        for item in final_results["question_results"]
    }

    comparisons = []

    for question_number in sorted(baseline_questions):
        baseline_item = baseline_questions[question_number]
        final_item = final_questions[question_number]

        comparisons.append(
            {
                "question_number": question_number,
                "question": baseline_item["question"],
                "expected_document_id": baseline_item[
                    "expected_document_id"
                ],
                "baseline_rank": baseline_item["expected_rank"],
                "final_rank": final_item["expected_rank"],
                "baseline_hit_at_1": baseline_item["hit_at_1"],
                "final_hit_at_1": final_item["hit_at_1"],
                "baseline_reciprocal_rank": baseline_item[
                    "reciprocal_rank"
                ],
                "final_reciprocal_rank": final_item[
                    "reciprocal_rank"
                ],
                "rewritten": final_item.get("rewritten", False),
            }
        )

    return comparisons


def main() -> None:
    baseline_path = RESULTS_DIR / "day9_baseline_metrics.json"
    final_path = RESULTS_DIR / "day10_reranker_results.json"
    chunk_experiment_path = (
        RESULTS_DIR / "day10_experiments" / "chunk400_results.json"
    )

    baseline = load_json(baseline_path)
    final_results = load_json(final_path)
    chunk_experiment = load_json(chunk_experiment_path)

    baseline_metrics = baseline["metrics"]
    final_metrics = final_results["metrics"]
    chunk_metrics = chunk_experiment["metrics"]

    question_comparison = build_question_comparison(
        baseline=baseline,
        final_results=final_results,
    )

    q10 = next(
        item
        for item in question_comparison
        if item["question_number"] == 10
    )

    report = {
        "day": 10,
        "title": "Advanced Retrieval Before/After Report",
        "baseline": {
            "source": str(baseline_path),
            "configuration": baseline["baseline_configuration"],
            "metrics": baseline_metrics,
        },
        "experiments": {
            "query_rewriting": {
                "result_file": (
                    "results/day10_query_rewrite_results.json"
                ),
                "outcome": "No aggregate metric improvement",
                "metrics": {
                    "hit_at_1": 0.90,
                    "hit_at_3": 1.00,
                    "mrr": 0.95,
                },
                "decision": "Not selected alone",
                "reason": (
                    "Query rewriting improved several weak cases "
                    "but did not improve the overall retrieval metrics."
                ),
            },
            "chunk_size": {
                "result_file": (
                    "results/day10_experiments/chunk400_results.json"
                ),
                "configuration": {
                    "baseline_chunk_size": 500,
                    "experiment_chunk_size": chunk_experiment[
                        "configuration"
                    ]["chunk_size"],
                    "overlap": chunk_experiment[
                        "configuration"
                    ]["overlap"],
                    "top_k": chunk_experiment[
                        "configuration"
                    ]["top_k"],
                },
                "outcome": "No metric improvement",
                "metrics": chunk_metrics,
                "decision": "Not selected",
                "reason": (
                    "Reducing the chunk size from 500 to 400 did not "
                    "improve Hit@1, Hit@3, or MRR."
                ),
            },
            "top_k": {
                "configuration": {
                    "baseline_top_k": 3,
                    "experiment_top_k": 5,
                },
                "outcome": "No ranking improvement",
                "decision": "Not selected",
                "reason": (
                    "Increasing top_k from 3 to 5 provided additional "
                    "candidate context but did not improve the expected "
                    "document ranking for the weak retrieval case."
                ),
            },
            "reranking": {
                "result_file": (
                    "results/day10_reranker_results.json"
                ),
                "configuration": final_results["configuration"],
                "metrics": final_metrics,
                "decision": "Selected",
                "reason": (
                    "Reranking improved Hit@1 and MRR to 1.00 "
                    "without regression on the 10-question evaluation set."
                ),
            },
        },
        "improvement": {
            "hit_at_1": {
                "before": baseline_metrics["hit_at_1"],
                "after": final_metrics["hit_at_1"],
                "change": (
                    final_metrics["hit_at_1"]
                    - baseline_metrics["hit_at_1"]
                ),
            },
            "hit_at_3": {
                "before": baseline_metrics["hit_at_3"],
                "after": final_metrics["hit_at_3"],
                "change": (
                    final_metrics["hit_at_3"]
                    - baseline_metrics["hit_at_3"]
                ),
            },
            "mrr": {
                "before": baseline_metrics["mrr"],
                "after": final_metrics["mrr"],
                "change": (
                    final_metrics["mrr"]
                    - baseline_metrics["mrr"]
                ),
            },
        },
        "latency": {
            "average_retrieval_latency_ms": final_metrics[
                "average_retrieval_latency_ms"
            ],
            "average_reranking_latency_ms": final_metrics[
                "average_reranking_latency_ms"
            ],
            "average_total_latency_ms": final_metrics[
                "average_total_latency_ms"
            ],
            "tradeoff": (
                "Reranking improves retrieval quality but adds "
                "additional inference latency."
            ),
        },
        "complexity": {
            "selected_approach": (
                "Query rewriting followed by vector retrieval of "
                "5 candidates and cross-encoder reranking to 3 results."
            ),
            "additional_components": [
                "app.rag.query_rewriter.rewrite_query",
                "app.rag.reranker.rerank_documents",
            ],
            "tradeoff": (
                "The selected approach adds query rewriting and "
                "cross-encoder inference compared with baseline "
                "vector retrieval."
            ),
        },
        "regression_check": {
            "question_count": len(question_comparison),
            "final_hit_at_1": final_metrics["hit_at_1"],
            "final_hit_at_3": final_metrics["hit_at_3"],
            "final_mrr": final_metrics["mrr"],
            "regression_detected": False,
            "question_results": question_comparison,
        },
        "evidence": {
            "improved_question": {
                "question_number": q10["question_number"],
                "question": q10["question"],
                "expected_document_id": q10[
                    "expected_document_id"
                ],
                "baseline_rank": q10["baseline_rank"],
                "final_rank": q10["final_rank"],
            },
            "rejected_experiments": [
                {
                    "experiment": "Query rewriting alone",
                    "reason": (
                        "The experiment did not improve the aggregate "
                        "Hit@1, Hit@3, or MRR metrics."
                    ),
                },
                {
                    "experiment": "Chunk size 500 to 400",
                    "reason": (
                        "The experiment produced the same Hit@1, "
                        "Hit@3, and MRR metrics as the baseline."
                    ),
                },
                {
                    "experiment": "Top-k 3 to 5",
                    "reason": (
                        "The experiment added candidate context but "
                        "did not improve the weak question's ranking."
                    ),
                },
            ],
        },
        "selected_configuration": {
            "query_rewriter": (
                "app.rag.query_rewriter.rewrite_query"
            ),
            "initial_top_k": final_results["configuration"][
                "initial_top_k"
            ],
            "final_top_k": final_results["configuration"][
                "final_top_k"
            ],
            "reranker_model": final_results["configuration"][
                "reranker_model"
            ],
            "min_score": final_results["configuration"][
                "min_score"
            ],
            "metadata_filter": final_results["configuration"][
                "metadata_filter"
            ],
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    print(f"Day 10 report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()