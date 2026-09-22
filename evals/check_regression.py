import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


SCORECARDS_DIR = BASE_DIR / "results" / "scorecards"
THRESHOLDS_PATH = (
    BASE_DIR
    / "evals"
    / "regression_thresholds.json"
)


def is_valid_scorecard(scorecard: dict) -> bool:
    total_cases = scorecard.get("total_cases", 0)

    if total_cases <= 0:
        return False

    failure_categories = scorecard.get(
        "failure_categories",
        {},
    )

    evaluation_errors = failure_categories.get(
        "evaluation_error",
        0,
    )

    if evaluation_errors >= total_cases:
        return False

    answer_grading = scorecard.get(
        "answer_grading",
        {},
    )

    retrieval_grading = scorecard.get(
        "retrieval_grading",
        {},
    )

    citation_quality = scorecard.get(
        "citation_quality",
        {},
    )

    answerability = scorecard.get(
        "answerability",
        {},
    )

    abstention = scorecard.get(
        "abstention",
        {},
    )

    required_sections = [
        answer_grading,
        retrieval_grading,
        citation_quality,
        answerability,
        abstention,
    ]

    if any(not section for section in required_sections):
        return False

    return True


def load_latest_scorecard() -> dict:
    scorecard_files = sorted(
        SCORECARDS_DIR.glob("scorecard_*.json")
    )

    if not scorecard_files:
        raise FileNotFoundError(
            f"No scorecards found in {SCORECARDS_DIR}"
        )

    for scorecard_file in reversed(scorecard_files):
        with scorecard_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            scorecard = json.load(file)

        if is_valid_scorecard(scorecard):
            print(
                f"Using scorecard: "
                f"{scorecard_file.name}"
            )
            return scorecard

    raise RuntimeError(
        "No valid scorecard found. "
        "All available scorecards contain "
        "provider/evaluation errors."
    )


def load_thresholds() -> dict:
    with THRESHOLDS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def check_threshold(
    name: str,
    actual: float,
    minimum: float,
) -> bool:
    passed = actual >= minimum

    status = "PASS" if passed else "FAIL"

    print(
        f"{name}: "
        f"{actual} "
        f"(minimum {minimum}) "
        f"-> {status}"
    )

    return passed


def check_max_threshold(
    name: str,
    actual: float,
    maximum: float,
) -> bool:
    passed = actual <= maximum

    status = "PASS" if passed else "FAIL"

    print(
        f"{name}: "
        f"{actual} "
        f"(maximum {maximum}) "
        f"-> {status}"
    )

    return passed


def main() -> int:
    scorecard = load_latest_scorecard()
    thresholds = load_thresholds()

    checks = []

    checks.append(
        check_threshold(
            "Answer pass rate",
            scorecard["answer_grading"]["pass_rate"],
            thresholds["answer_pass_rate"],
        )
    )

    checks.append(
        check_threshold(
            "Retrieval hit rate",
            scorecard["retrieval_grading"]["hit_rate"],
            thresholds["retrieval_hit_rate"],
        )
    )

    checks.append(
        check_threshold(
            "Recall@K",
            scorecard["retrieval_grading"]["recall_at_k"],
            thresholds["recall_at_k"],
        )
    )

    checks.append(
        check_threshold(
            "MRR",
            scorecard["retrieval_grading"]["mrr"],
            thresholds["mrr"],
        )
    )

    checks.append(
        check_threshold(
            "Citation correctness",
            scorecard["citation_quality"][
                "citation_correctness"
            ],
            thresholds["citation_correctness"],
        )
    )

    checks.append(
        check_threshold(
            "Answerability accuracy",
            scorecard["answerability"]["accuracy"],
            thresholds["answerability_accuracy"],
        )
    )

    checks.append(
        check_threshold(
            "Abstention accuracy",
            scorecard["abstention"]["accuracy"],
            thresholds["abstention_accuracy"],
        )
    )

    checks.append(
        check_max_threshold(
            "Average latency",
            scorecard["latency"]["average_seconds"],
            thresholds["max_average_latency_seconds"],
        )
    )

    if all(checks):
        print("REGRESSION CHECK PASSED")
        return 0

    print("REGRESSION CHECK FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())