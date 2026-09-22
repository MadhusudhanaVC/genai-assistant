import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


RESULTS_DIR = BASE_DIR / "results" / "eval_runs"
REPORTS_DIR = BASE_DIR / "results" / "eval_reports"


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


def get_failure_category(result: dict) -> str:
    if result.get("error") is not None:
        return "evaluation_error"

    answer_grade = result.get("answer_grade")

    if not answer_grade:
        return "missing_answer_grade"

    if not answer_grade.get("passed"):
        answerability = answer_grade.get(
            "answerability",
            {},
        )

        if not answerability.get("passed"):
            return answerability.get(
                "failure_category",
                "answer_failure",
            )

        citation_presence = answer_grade.get(
            "citation_presence",
            {},
        )

        if not citation_presence.get("passed"):
            return citation_presence.get(
                "failure_category",
                "citation_presence_failure",
            )

        citation_validity = answer_grade.get(
            "citation_validity",
            {},
        )

        if not citation_validity.get("passed"):
            return citation_validity.get(
                "failure_category",
                "citation_validity_failure",
            )

        return "answer_failure"

    retrieval_grade = result.get("retrieval_grade")

    if retrieval_grade and not retrieval_grade.get("passed"):
        return "retrieval_failure"

    return "none"


def format_retrieval_result(result: dict) -> str:
    retrieval_grade = result.get("retrieval_grade")

    if retrieval_grade is None:
        return "not graded"

    if retrieval_grade.get("passed"):
        return "PASS"

    return "FAIL"


def format_answer_result(result: dict) -> str:
    answer_grade = result.get("answer_grade")

    if answer_grade is None:
        return "not graded"

    if answer_grade.get("passed"):
        return "PASS"

    return "FAIL"


def create_report(data: dict) -> str:
    lines = []

    lines.append("# Evaluation Review Report")
    lines.append("")
    lines.append(
        f"**Run ID:** {data['run_id']}"
    )
    lines.append(
        f"**Cases:** {data['golden_set_cases']}"
    )
    lines.append(
        f"**Source:** `{data['_source_file'].relative_to(BASE_DIR)}`"
    )
    lines.append("")
    lines.append(
        "| Case | Retrieval | Answer | Latency (s) | Failure Category |"
    )
    lines.append(
        "|---|---|---|---:|---|"
    )

    for result in data["results"]:
        failure_category = get_failure_category(
            result
        )

        lines.append(
            "| "
            f"{result['case_id']} | "
            f"{format_retrieval_result(result)} | "
            f"{format_answer_result(result)} | "
            f"{result['latency_seconds']} | "
            f"{failure_category} |"
        )

    lines.append("")
    lines.append("## Case Details")
    lines.append("")

    for result in data["results"]:
        lines.append(
            f"### {result['case_id']} — "
            f"{result['question']}"
        )
        lines.append("")

        lines.append(
            f"- **Expected answerability:** "
            f"{result['expected_answerability']}"
        )

        lines.append(
            f"- **Actual status:** "
            f"{result['actual_status']}"
        )

        lines.append(
            f"- **Retrieval:** "
            f"{format_retrieval_result(result)}"
        )

        lines.append(
            f"- **Answer:** "
            f"{format_answer_result(result)}"
        )

        lines.append(
            f"- **Latency:** "
            f"{result['latency_seconds']} seconds"
        )

        lines.append(
            f"- **Failure category:** "
            f"{get_failure_category(result)}"
        )

        lines.append("")

    return "\n".join(lines)


def main():
    data = load_latest_evaluation()

    report = create_report(data)

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        REPORTS_DIR
        / f"report_{data['run_id']}.md"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    print("Evaluation report generated.")
    print(f"Cases: {data['golden_set_cases']}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()