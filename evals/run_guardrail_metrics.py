
from fastapi.testclient import TestClient

from app.main import app
from evals.guardrail_metrics_cases import GUARDRAIL_METRICS_CASES


def run_evaluation():
    results = []
    original_generate = None

    from app.api import routes

    original_generate = routes.generate_grounded_answer

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

                expected = case["expected_outcome"]

                results.append(
                    {
                        "case_id": case["case_id"],
                        "expected": expected,
                        "actual": actual,
                        "correct": expected == actual,
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

    print("\nGuardrail Evaluation")
    print("-" * 60)

    for result in results:
        outcome = "PASS" if result["correct"] else "FAIL"
        print(
            f"{outcome} | {result['case_id']} | "
            f"expected={result['expected']} | "
            f"actual={result['actual']}"
        )

    print("-" * 60)
    print(f"Total cases: {len(results)}")
    print(f"Correct outcomes: {sum(r['correct'] for r in results)}")
    print(f"Incorrect outcomes: {sum(not r['correct'] for r in results)}")
    print(f"False accepts: {false_accepts}")
    print(f"False rejects: {false_rejects}")


if __name__ == "__main__":
    run_evaluation()