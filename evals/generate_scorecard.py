import json
import sys
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


RESULTS_DIR = BASE_DIR / "results" / "eval_runs"
SCORECARDS_DIR = BASE_DIR / "results" / "scorecards"


def load_latest_evaluation() -> dict:
    result_files = sorted(
        RESULTS_DIR.glob("eval_*.json")
    )

    if not result_files:
        raise FileNotFoundError(
            f"No evaluation results found in {RESULTS_DIR}"
        )

    latest_file = result_files[-1]

    with latest_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    data["_source_file"] = latest_file

    return data


def calculate_average(
    values: list[float],
) -> float:
    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        4,
    )


def calculate_scorecard(data: dict) -> dict:
    results = data["results"]

    total_cases = len(results)

    answer_graded = [
        result
        for result in results
        if result.get("answer_grade") is not None
    ]

    answer_passed = sum(
        result["answer_grade"]["passed"]
        for result in answer_graded
    )

    retrieval_graded = [
        result
        for result in results
        if result.get("retrieval_grade") is not None
    ]

    retrieval_passed = sum(
        result["retrieval_grade"]["passed"]
        for result in retrieval_graded
    )

    hit_rates = [
        result["retrieval_grade"]["hit_rate"]
        for result in retrieval_graded
    ]

    recall_at_k = [
        result["retrieval_grade"]["recall_at_k"]
        for result in retrieval_graded
    ]

    mrr_values = [
        result["retrieval_grade"]["mrr"]
        for result in retrieval_graded
    ]

    citation_checks = [
        result["answer_grade"]["citation_validity"]
        for result in answer_graded
    ]

    citation_checked = sum(
        check["checked"]
        for check in citation_checks
    )

    citation_valid = sum(
        check["valid"]
        for check in citation_checks
    )

    citation_correctness = (
        citation_valid / citation_checked
        if citation_checked
        else 0.0
    )

    answerability_checks = [
        result["answer_grade"]["answerability"]
        for result in answer_graded
    ]

    answerability_passed = sum(
        check["passed"]
        for check in answerability_checks
    )

    answerability_accuracy = (
        answerability_passed / len(answerability_checks)
        if answerability_checks
        else 0.0
    )

    abstention_cases = [
        result
        for result in results
        if result.get("expected_answerability") == "unanswerable"
        and result.get("error") is None
    ]

    correct_abstentions = sum(
        result.get("actual_status") == "insufficient_evidence"
        and len(result.get("actual_citations", [])) == 0
        for result in abstention_cases
    )

    abstention_accuracy = (
        correct_abstentions / len(abstention_cases)
        if abstention_cases
        else 0.0
    )

    latencies = [
        result["latency_seconds"]
        for result in results
        if result.get("latency_seconds") is not None
    ]

    average_latency = calculate_average(
        latencies
    )

    max_latency = (
        round(
            max(latencies),
            4,
        )
        if latencies
        else 0.0
    )

    failure_categories = Counter()

    for result in results:
        answer_grade = result.get(
            "answer_grade"
        )

        if result.get("error") is not None:
            failure_categories[
                "evaluation_error"
            ] += 1
            continue

        if (
            answer_grade
            and not answer_grade["passed"]
        ):
            answerability = answer_grade.get(
                "answerability"
            )

            if (
                answerability
                and not answerability["passed"]
            ):
                failure_category = (
                    answerability.get(
                        "failure_category"
                    )
                    or "answerability_failure"
                )

                failure_categories[
                    failure_category
                ] += 1

                continue

            citation_presence = answer_grade.get(
                "citation_presence"
            )

            if (
                citation_presence
                and not citation_presence["passed"]
            ):
                failure_category = (
                    citation_presence.get(
                        "failure_category"
                    )
                    or "citation_presence_failure"
                )

                failure_categories[
                    failure_category
                ] += 1

                continue

            citation_validity = answer_grade.get(
                "citation_validity"
            )

            if (
                citation_validity
                and not citation_validity["passed"]
            ):
                failure_category = (
                    citation_validity.get(
                        "failure_category"
                    )
                    or "citation_validity_failure"
                )

                failure_categories[
                    failure_category
                ] += 1

                continue

            required_facts = answer_grade.get(
                "required_facts"
            )

            if (
                required_facts
                and not required_facts["passed"]
            ):
                failure_category = (
                    required_facts.get(
                        "failure_category"
                    )
                    or "missing_required_facts"
                )

                failure_categories[
                    failure_category
                ] += 1

                continue

        retrieval_grade = result.get(
            "retrieval_grade"
        )

        if (
            retrieval_grade
            and not retrieval_grade["passed"]
        ):
            failure_categories[
                "retrieval_failure"
            ] += 1

    top_failure_categories = [
        {
            "category": category,
            "count": count,
        }
        for category, count
        in failure_categories.most_common(3)
    ]

    component_metrics = {
        "answer_quality": (
            answer_passed / len(answer_graded)
            if answer_graded
            else 0.0
        ),
        "retrieval_quality": calculate_average(
            hit_rates
        ),
        "citation_quality": citation_correctness,
        "abstention_quality": abstention_accuracy,
    }

    weakest_component = min(
        component_metrics,
        key=component_metrics.get,
    )

    return {
        "run_id": data["run_id"],
        "source_file": str(
            data["_source_file"].relative_to(
                BASE_DIR
            )
        ),
        "total_cases": total_cases,
        "answer_grading": {
            "graded_cases": len(answer_graded),
            "passed_cases": answer_passed,
            "pass_rate": round(
                answer_passed / len(answer_graded),
                4,
            )
            if answer_graded
            else 0.0,
        },
        "retrieval_grading": {
            "graded_cases": len(retrieval_graded),
            "passed_cases": retrieval_passed,
            "pass_rate": round(
                retrieval_passed
                / len(retrieval_graded),
                4,
            )
            if retrieval_graded
            else 0.0,
            "hit_rate": calculate_average(
                hit_rates
            ),
            "recall_at_k": calculate_average(
                recall_at_k
            ),
            "mrr": calculate_average(
                mrr_values
            ),
        },
        "citation_quality": {
            "checked_citations": citation_checked,
            "valid_citations": citation_valid,
            "citation_correctness": round(
                citation_correctness,
                4,
            ),
        },
        "answerability": {
            "graded_cases": len(answerability_checks),
            "passed_cases": answerability_passed,
            "accuracy": round(
                answerability_accuracy,
                4,
            ),
        },
        "abstention": {
            "checked_cases": len(abstention_cases),
            "correct_abstentions": correct_abstentions,
            "accuracy": round(
                abstention_accuracy,
                4,
            ),
        },
        "latency": {
            "average_seconds": average_latency,
            "max_seconds": max_latency,
        },
        "failure_categories": dict(
            failure_categories
        ),
        "top_failure_categories": (
            top_failure_categories
        ),
        "component_metrics": {
            component: round(
                value,
                4,
            )
            for component, value
            in component_metrics.items()
        },
        "weakest_component": {
            "component": weakest_component,
            "metric_value": round(
                component_metrics[
                    weakest_component
                ],
                4,
            ),
        },
        "cost_proxy": {
            "llm_calls": total_cases,
        },
    }


def write_scorecard(
    scorecard: dict,
) -> Path:
    SCORECARDS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    scorecard_path = (
        SCORECARDS_DIR
        / f"scorecard_{scorecard['run_id']}.json"
    )

    with scorecard_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            scorecard,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return scorecard_path


def main():
    data = load_latest_evaluation()

    scorecard = calculate_scorecard(
        data
    )

    scorecard_path = write_scorecard(
        scorecard
    )

    print("Scorecard generated.")
    print(
        f"Cases: "
        f"{scorecard['total_cases']}"
    )
    print(
        f"Answer pass rate: "
        f"{scorecard['answer_grading']['pass_rate']}"
    )
    print(
        f"Retrieval hit rate: "
        f"{scorecard['retrieval_grading']['hit_rate']}"
    )
    print(
        f"Recall@K: "
        f"{scorecard['retrieval_grading']['recall_at_k']}"
    )
    print(
        f"MRR: "
        f"{scorecard['retrieval_grading']['mrr']}"
    )
    print(
        f"Citation correctness: "
        f"{scorecard['citation_quality']['citation_correctness']}"
    )
    print(
        f"Answerability accuracy: "
        f"{scorecard['answerability']['accuracy']}"
    )
    print(
        f"Abstention accuracy: "
        f"{scorecard['abstention']['accuracy']}"
    )
    print(
        f"Average latency: "
        f"{scorecard['latency']['average_seconds']} seconds"
    )
    print(
        f"Top failure categories: "
        f"{scorecard['top_failure_categories']}"
    )
    print(
        f"Weakest component: "
        f"{scorecard['weakest_component']['component']} "
        f"({scorecard['weakest_component']['metric_value']})"
    )
    print(
        f"Scorecard: "
        f"{scorecard_path}"
    )


if __name__ == "__main__":
    main()