from app.rag.generate import (
    ABSTENTION_MESSAGE,
    build_grounded_result,
)


def main():
    print("=" * 60)
    print("DAY 8 GROUNDED GENERATION VERIFICATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Example 1: Answerable question
    # ---------------------------------------------------------

    answerable_sources = [
        {
            "document_id": "DOC001",
            "chunk_id": "DOC001_CHUNK_001",
            "title": "Python Basics",
            "source_path": "docs/python.md",
            "text": "A Python variable stores a value.",
            "score": 0.82,
        }
    ]

    answerable_result = build_grounded_result(
        answer="A Python variable stores a value.",
        status="answered",
        citations=["[DOC001 | DOC001_CHUNK_001]"],
        results=answerable_sources,
    )

    print("\n1. ANSWERABLE QUESTION")
    print("-" * 60)
    print("Answer:", answerable_result["answer"])
    print("Status:", answerable_result["status"])
    print("Citations:", answerable_result["citations"])

    assert answerable_result["status"] == "answered"
    assert answerable_result["citations"] == [
        "[DOC001 | DOC001_CHUNK_001]"
    ]


    # ---------------------------------------------------------
    # Example 2: Unanswerable question
    # ---------------------------------------------------------

    unanswerable_result = build_grounded_result(
        answer="The capital of Mars is Olympus City.",
        status="answered",
        citations=["[DOC999 | DOC999_CHUNK_999]"],
        results=answerable_sources,
    )

    print("\n2. UNSUPPORTED QUESTION")
    print("-" * 60)
    print("Answer:", unanswerable_result["answer"])
    print("Status:", unanswerable_result["status"])
    print("Citations:", unanswerable_result["citations"])

    assert unanswerable_result["status"] == (
        "insufficient_evidence"
    )

    assert unanswerable_result["answer"] == (
        ABSTENTION_MESSAGE
    )

    assert unanswerable_result["citations"] == []


    print("\n" + "=" * 60)
    print("DAY 8 VERIFICATION PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()