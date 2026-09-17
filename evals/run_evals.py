import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from app.llm.client import MODEL_VERSION
from app.rag.generate import PROMPT_VERSION, generate_grounded_answer


GOLDEN_SET_PATH = BASE_DIR / "datasets" / "golden_set.jsonl"

RESULTS_DIR = BASE_DIR / "results" / "eval_runs"

TOP_K = 3
MIN_SCORE = None


def load_golden_set() -> list[dict]:
    cases = []

    with GOLDEN_SET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            cases.append(json.loads(line))

    return cases


def evaluate_case(case: dict) -> dict:
    started_at = time.perf_counter()

    result = {
        "case_id": case["case_id"],
        "question": case["question"],
        "category": case["category"],
        "expected_source_ids": case["expected_source_ids"],
        "expected_answerability": case["answerability"],
        "actual_answer": None,
        "actual_status": None,
        "actual_citations": [],
        "retrieval_results": [],
        "latency_seconds": None,
        "model_version": MODEL_VERSION,
        "prompt_version": PROMPT_VERSION,
        "top_k": TOP_K,
        "min_score": MIN_SCORE,
        "error": None,
    }

    try:
        result_data = generate_grounded_answer(
            question=case["question"],
            top_k=TOP_K,
            min_score=MIN_SCORE,
        )

        result["actual_answer"] = result_data.get("answer")
        result["actual_status"] = result_data.get("status")
        result["actual_citations"] = result_data.get(
            "citations",
            [],
        )
        result["retrieval_results"] = result_data.get(
            "sources",
            [],
        )

    except Exception as error:
        result["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }

    result["latency_seconds"] = round(
        time.perf_counter() - started_at,
        3,
    )

    return result


def create_run_id() -> str:
    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def main():
    if not GOLDEN_SET_PATH.exists():
        raise FileNotFoundError(
            f"Golden set not found: {GOLDEN_SET_PATH}"
        )

    cases = load_golden_set()

    if not cases:
        raise ValueError(
            "Golden set contains no cases"
        )

    run_id = create_run_id()

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_path = (
        RESULTS_DIR
        / f"eval_{run_id}.json"
    )

    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    run_results = []

    for case in cases:
        print(
            f"Running {case['case_id']}: "
            f"{case['question']}"
        )

        run_results.append(
            evaluate_case(case)
        )

    finished_at = datetime.now(
        timezone.utc
    ).isoformat()

    output = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "golden_set": str(
            GOLDEN_SET_PATH.relative_to(BASE_DIR)
        ),
        "golden_set_cases": len(cases),
        "configuration": {
            "top_k": TOP_K,
            "min_score": MIN_SCORE,
            "model_version": MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
        },
        "results": run_results,
    }

    with result_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("Evaluation run completed.")
    print(f"Cases: {len(cases)}")
    print(f"Result: {result_path}")


if __name__ == "__main__":
    main()