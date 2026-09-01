import json
import sys
from pathlib import Path

from app.rag.retrieve import retrieve_documents


# DAY 9 — CONTROLLED RETRIEVAL EXPERIMENT

DATASET_PATH = Path("datasets/day6_retrieval_test_cases.json")
BASELINE_PATH = Path("results/day9_baseline_metrics.json")
OUTPUT_DIR = Path("results/day9_experiments")



# FROZEN BASELINE RETRIEVAL SETTINGS

BASELINE_TOP_K = 3
BASELINE_MIN_SCORE = None
BASELINE_WHERE = None


# EXPERIMENT DEFINITIONS

EXPERIMENTS = {
    "E01": {
        "question_number": 10,
        "variable_changed": "query_wording",
        "original_query": "What is machine learning?",
        "experiment_query": "What is machine learning and how is it defined?",
        "expected_document_id": "DOC019",
        "hypothesis": (
            "A more explicit query may improve the ranking of DOC019 "
            "against the closely competing DOC020."
        ),
    },
    "E02": {
        "question_number": 7,
        "variable_changed": "query_wording",
        "original_query": "What is a Git branch?",
        "experiment_query": (
            "What is a Git branch and how is it used for "
            "separate lines of development?"
        ),
        "expected_document_id": "DOC008",
        "hypothesis": (
            "A more explicit branch-focused query may increase "
            "the separation between DOC008 and DOC007."
        ),
    },
    "E03": {
        "question_number": 4,
        "variable_changed": "query_wording",
        "original_query": "What is a Python module?",
        "experiment_query": (
            "What is a Python module and how is it used to organize "
            "Python code?"
        ),
        "expected_document_id": "DOC004",
        "hypothesis": (
            "A more explicit module-focused query may increase "
            "the separation between DOC004 and related Python documents."
        ),
    },
    "E04": {
        "question_number": 8,
        "variable_changed": "top_k",
        "original_query": "What causes a Git merge conflict?",
        "experiment_query": "What causes a Git merge conflict?",
        "experiment_top_k": 5,
        "expected_document_id": "DOC009",
        "hypothesis": (
            "Increasing Top-K may reveal useful additional evidence "
            "beyond the baseline three retrieved chunks."
        ),
    },
    "E05": {
        "question_number": 1,
        "variable_changed": "query_wording",
        "original_query": "What is a Python variable?",
        "experiment_query": (
            "What is a Python variable and what does it store?"
        ),
        "expected_document_id": "DOC001",
        "hypothesis": (
            "A more explicit variable-focused query may improve "
            "separation from related Python documents."
        ),
    },
}


# LOAD DATASET
def load_test_cases() -> list[dict]:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

# LOAD BASELINE QUESTION RESULT
def load_baseline_results() -> dict:
    with BASELINE_PATH.open("r", encoding="utf-8") as file:
        report = json.load(file)

    return {
        result["question_number"]: result
        for result in report["question_results"]
    }


# ============================================================
# RECIPROCAL RANK
# ============================================================

def reciprocal_rank(rank: int | None) -> float:
    if rank is None:
        return 0.0

    return round(1.0 / rank, 4)


# FIND EXPECTED DOCUMENT RANK

def find_expected_rank(
    retrieved_documents: list[dict],
    expected_document_id: str,
) -> int | None:

    for result in retrieved_documents:
        if result["document_id"] == expected_document_id:
            return result["rank"]

    return None

# CALCULATE SCORE MARGIN

def calculate_score_margin(
    retrieved_documents: list[dict],
    expected_document_id: str,
) -> dict:

    expected_result = None
    competing_result = None

    for result in retrieved_documents:
        if result["document_id"] == expected_document_id:
            expected_result = result
            break

    for result in retrieved_documents:
        if result["document_id"] != expected_document_id:
            competing_result = result
            break

    if expected_result is None or competing_result is None:
        return {
            "expected_score": (
                expected_result["score"]
                if expected_result
                else None
            ),
            "competitor_document_id": (
                competing_result["document_id"]
                if competing_result
                else None
            ),
            "competitor_score": (
                competing_result["score"]
                if competing_result
                else None
            ),
            "score_margin": None,
        }

    margin = round(
        expected_result["score"] - competing_result["score"],
        4,
    )

    return {
        "expected_score": expected_result["score"],
        "competitor_document_id": competing_result["document_id"],
        "competitor_score": competing_result["score"],
        "score_margin": margin,
    }



# RETRIEVE EXPERIMENT RESULTS


def retrieve_for_experiment(
    query: str,
    top_k: int,
) -> list[dict]:

    results = retrieve_documents(
        query=query,
        top_k=top_k,
        min_score=BASELINE_MIN_SCORE,
        where=BASELINE_WHERE,
    )

    return [
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


# RUN ONE EXPERIMENT
def run_experiment(experiment_id: str) -> dict:

    if experiment_id not in EXPERIMENTS:
        raise ValueError(
            f"Unknown experiment: {experiment_id}. "
            f"Available experiments: {', '.join(EXPERIMENTS)}"
        )

    experiment = EXPERIMENTS[experiment_id]

    test_cases = load_test_cases()
    baseline_results = load_baseline_results()

    question_number = experiment["question_number"]

    test_case = next(
        case
        for index, case in enumerate(test_cases, start=1)
        if index == question_number
    )

    expected_document_id = test_case["expected_document_id"]

    if expected_document_id != experiment["expected_document_id"]:
        raise ValueError(
            "Experiment expected document does not match "
            "the fixed evaluation dataset."
        )

    baseline_question = baseline_results[question_number]

    if experiment["variable_changed"] == "query_wording":
        experiment_top_k = BASELINE_TOP_K
        experiment_query = experiment["experiment_query"]

    elif experiment["variable_changed"] == "top_k":
        experiment_top_k = experiment["experiment_top_k"]
        experiment_query = experiment["original_query"]

    else:
        raise ValueError(
            f"Unsupported experiment variable: "
            f"{experiment['variable_changed']}"
        )

    retrieved_documents = retrieve_for_experiment(
        query=experiment_query,
        top_k=experiment_top_k,
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

    reciprocal = reciprocal_rank(expected_rank)

    score_information = calculate_score_margin(
        retrieved_documents,
        expected_document_id,
    )

    unique_documents = list(
        dict.fromkeys(
            result["document_id"]
            for result in retrieved_documents
        )
    )

    chunks_per_document = {}

    for result in retrieved_documents:
        document_id = result["document_id"]

        chunks_per_document[document_id] = (
            chunks_per_document.get(document_id, 0) + 1
        )

    return {
        "experiment": experiment_id,
        "question_number": question_number,
        "variable_changed": experiment["variable_changed"],
        "hypothesis": experiment["hypothesis"],
        "baseline": {
            "query": baseline_question["question"],
            "top_k": BASELINE_TOP_K,
            "expected_document_id": expected_document_id,
            "expected_rank": baseline_question["expected_rank"],
            "hit_at_1": baseline_question["hit_at_1"],
            "hit_at_3": baseline_question["hit_at_3"],
            "reciprocal_rank": baseline_question["reciprocal_rank"],
        },
        "experiment_configuration": {
            "query": experiment_query,
            "top_k": experiment_top_k,
            "min_score": BASELINE_MIN_SCORE,
            "metadata_filter": BASELINE_WHERE,
        },
        "experiment_result": {
            "expected_document_id": expected_document_id,
            "expected_rank": expected_rank,
            "hit_at_1": hit_at_1,
            "hit_at_3": hit_at_3,
            "reciprocal_rank": reciprocal,
            "unique_document_count": len(unique_documents),
            "unique_documents": unique_documents,
            "chunks_per_document": chunks_per_document,
            **score_information,
            "retrieved_documents": retrieved_documents,
        },
    }


# SAVE EXPERIMENT RESULT

def save_result(experiment_id: str, result: dict) -> Path:

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = (
        OUTPUT_DIR / f"{experiment_id.lower()}_result.json"
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_path


# PRINT RESULT

def print_result(result: dict) -> None:

    baseline = result["baseline"]
    experiment = result["experiment_result"]

    print()
    print("=" * 60)
    print(
        f"DAY 9 CONTROLLED EXPERIMENT "
        f"{result['experiment']}"
    )
    print("=" * 60)

    print()
    print("Variable changed:")
    print(result["variable_changed"])

    print()
    print("Baseline:")
    print(f"Query       : {baseline['query']}")
    print(f"Top-K       : {baseline['top_k']}")
    print(f"Expected    : {baseline['expected_document_id']}")
    print(f"Rank        : {baseline['expected_rank']}")
    print(f"Hit@1       : {baseline['hit_at_1']}")
    print(f"Hit@3       : {baseline['hit_at_3']}")
    print(f"MRR         : {baseline['reciprocal_rank']}")

    print()
    print("Experiment:")
    print(
        f"Query       : "
        f"{result['experiment_configuration']['query']}"
    )
    print(
        f"Top-K       : "
        f"{result['experiment_configuration']['top_k']}"
    )
    print(f"Expected    : {experiment['expected_document_id']}")
    print(f"Rank        : {experiment['expected_rank']}")
    print(f"Hit@1       : {experiment['hit_at_1']}")
    print(f"Hit@3       : {experiment['hit_at_3']}")
    print(f"MRR         : {experiment['reciprocal_rank']}")

    print()
    print("Score comparison:")
    print(
        f"Expected score   : "
        f"{experiment['expected_score']}"
    )
    print(
        f"Competitor       : "
        f"{experiment['competitor_document_id']}"
    )
    print(
        f"Competitor score : "
        f"{experiment['competitor_score']}"
    )
    print(
        f"Score margin     : "
        f"{experiment['score_margin']}"
    )

    print()
    print("Retrieved documents:")
    print("-" * 60)

    for retrieved in experiment["retrieved_documents"]:
        print(
            f"Rank {retrieved['rank']} | "
            f"{retrieved['document_id']} | "
            f"{retrieved['chunk_id']} | "
            f"Score: {retrieved['score']}"
        )

    print()
    print(
        f"Unique documents: "
        f"{experiment['unique_document_count']}"
    )

    print()
    print("Hypothesis:")
    print(result["hypothesis"])

    print()
    print("=" * 60)



# MAIN

def main() -> None:

    if len(sys.argv) != 2:
        print(
            "Usage: python.exe scripts/day9_experiment.py E01"
        )
        print()
        print(
            "Available experiments: "
            + ", ".join(EXPERIMENTS)
        )
        raise SystemExit(1)

    experiment_id = sys.argv[1].upper()

    result = run_experiment(experiment_id)

    output_path = save_result(
        experiment_id,
        result,
    )

    print_result(result)

    print()
    print(f"Saved result: {output_path}")
    print()
    print(
        f"DAY 9 {experiment_id} EXPERIMENT COMPLETE"
    )


if __name__ == "__main__":
    main()