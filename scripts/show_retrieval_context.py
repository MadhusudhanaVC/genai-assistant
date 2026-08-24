import argparse

from app.rag.generate import prepare_context
from app.rag.retrieve import retrieve_documents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrieve and display generation-ready context."
    )

    parser.add_argument(
        "question",
        help="Question to search for.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--min-score",
        type=float,
        default=None,
    )

    parser.add_argument(
        "--max-chunks",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--max-characters",
        type=int,
        default=6000,
    )

    args = parser.parse_args()

    results = retrieve_documents(
        query=args.question,
        top_k=args.top_k,
        min_score=args.min_score,
    )

    context = prepare_context(
        results,
        max_chunks=args.max_chunks,
        max_characters=args.max_characters,
    )

    print()
    print("========== RETRIEVAL RESULTS ==========")
    print(f"Question: {args.question}")
    print(f"Results: {len(results)}")

    for result in results:
        print(
            f"{result['chunk_id']} | "
            f"{result['document_id']} | "
            f"{result['title']} | "
            f"score={result['score']}"
        )

    print()
    print("========== GENERATION CONTEXT ==========")

    if context:
        print(context)
    else:
        print("No evidence met the retrieval criteria.")

    print("========================================")


if __name__ == "__main__":
    main()