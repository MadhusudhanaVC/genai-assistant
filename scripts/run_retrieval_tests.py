import json
from pathlib import Path

from app.rag.retrieve import retrieve_documents


TEST_FILE = Path("datasets/day6_retrieval_test_cases.json")
REPORT_FILE = Path("results/day6_retrieval_report.json")

TOP_K = 3


def load_test_cases() -> list[dict]:
    with TEST_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_tests() -> list[dict]:
    test_cases = load_test_cases()
    results = []

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_document_id = test_case["expected_document_id"]

        retrieved = retrieve_documents(
            question,
            top_k=TOP_K,
        )

        top_3_results = []

        for result in retrieved:
            top_3_results.append(
                {
                    "chunk_id": result["chunk_id"],
                    "document_id": result["document_id"],
                    "title": result["title"],
                    "score": result["score"],
                    "source_path": result["source_path"],
                    "updated_at": result["updated_at"],
                    "chunk_index": result["chunk_index"],
                    "category": result["category"],
                }
            )

        retrieved_document_ids = [
            result["document_id"]
            for result in retrieved
        ]

        passed = expected_document_id in retrieved_document_ids

        results.append(
            {
                "test_case": index,
                "question": question,
                "expected_document_id": expected_document_id,
                "top_3_results": top_3_results,
                "passed": passed,
            }
        )

        status = "PASS" if passed else "FAIL"

        print(
            f"{index}. {status} - "
            f"{question} -> "
            f"expected {expected_document_id}"
        )

    return results


def save_report(results: list[dict]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    passed = sum(result["passed"] for result in results)
    total = len(results)

    report = {
        "embedding_model": "all-MiniLM-L6-v2",
        "top_k": TOP_K,
        "total_questions": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total, 4) if total else 0,
        "results": results,
    }

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    results = run_tests()

    passed = sum(result["passed"] for result in results)
    total = len(results)

    save_report(results)

    print()
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()python -m scripts.run_retrieval_tests