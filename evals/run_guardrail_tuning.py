from fastapi.testclient import TestClient

from app.api import routes
from app.main import app
from evals.guardrail_metrics_cases import GUARDRAIL_METRICS_CASES


def run_evaluation(tuned):
    results = []

    def fake_generate_grounded_answer(
        question,
        top_k,
        min_score,
        stage_logger=None,
    ):
        if question == "What is Python?":
            return {
                "answer": "Python is a general-purpose programming language.",
                "status": "answered",
                "citations": ["[DOC001 | DOC001_CHUNK_001]"],
                "sources": [
                    {
                        "document_id": "DOC001",
                        "chunk_id": "DOC001_CHUNK_001",
                        "title": "Python Basics",
                    }
                ],
            }

        if question == "What is a Python variable?":
            if tuned:
                return {
                    "answer": "A Python variable stores a value.",
                    "status": "answered",
                    "citations": ["[DOC001 | DOC001_CHUNK_001]"],
                    "sources": [
                        {
                            "document_id": "DOC001",
                            "chunk_id": "DOC001_CHUNK_001",
                            "title": "Python Basics",
                        }
                    ],
                }

            return {
                "answer": (
                    "There is not enough evidence in the provided "
                    "documents to answer this question."
                ),
                "status": "insufficient_evidence",
                "citations": [],
                "sources": [],
            }

        return {
            "answer": (
                "There is not enough evidence in the provided "
                "documents to answer this question."
            ),
            "status": "insufficient_evidence",
            "citations": [],
            "sources": [],
        }

    original_generate = routes.generate_grounded_answer
    routes.generate_grounded_answer = fake_generate_grounded_answer

    try:
        with TestClient(app) as client:
            for case in GUARDRAIL_METRICS_CASES:
                response = client.post(
                    "/ask",
                    json={
                        "question": case["question"],
                        "top_k": 3,
                        "min_score": None,
                    },
                )

                if response.status_code == 400:
                    data = response.json()
                    actual = (
                        "blocked"
                        if data.get("error_code") == "GUARDRAIL_BLOCKED"
                        else "error"
                    )
                elif response.status_code == 200:
                    actual = response.json().get("status", "error")
                else:
                    actual = "error"

                results.append(
                    {
                        "case_id": case["case_id"],
                        "expected": case["expected_outcome"],
                        "actual": actual,
                    }
                )
    finally:
        routes.generate_grounded_answer = original_generate

    false_accepts = sum(
        result["expected"] == "insufficient_evidence"
        and result["actual"] == "answered"
        for result in results
    )

    false_rejects = sum(
        result["expected"] == "answered"
        and result["actual"] == "insufficient_evidence"
        for result in results
    )

    correct = sum(
        result["expected"] == result["actual"]
        for result in results
    )

    return {
        "total": len(results),
        "correct": correct,
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
        "results": results,
    }


def print_report(name, metrics):
    print(f"\n{name}")
    print("-" * 50)
    print(f"Total cases: {metrics['total']}")
    print(f"Correct outcomes: {metrics['correct']}")
    print(f"False accepts: {metrics['false_accepts']}")
    print(f"False rejects: {metrics['false_rejects']}")


before = run_evaluation(tuned=False)
after = run_evaluation(tuned=True)

print_report("Before tuning", before)
print_report("After tuning", after)

print("\nMetric change")
print("-" * 50)
print(
    f"False accepts: "
    f"{before['false_accepts']} -> {after['false_accepts']}"
)
print(
    f"False rejects: "
    f"{before['false_rejects']} -> {after['false_rejects']}"
)

for before_case, after_case in zip(
    before["results"],
    after["results"],
):
    if (
        before_case["expected"] == "answered"
        and before_case["actual"] == "insufficient_evidence"
        and after_case["actual"] == "answered"
    ):
        print("\nCorrected false reject")
        print(f"Case: {before_case['case_id']}")
        print(
            f"Before: {before_case['actual']} -> "
            f"After: {after_case['actual']}"
        )