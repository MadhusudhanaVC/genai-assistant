from app.rag.retrieve import retrieve_documents
from app.rag.reranker import rerank_documents


QUESTION = "What is machine learning?"

INITIAL_TOP_K = 5
FINAL_TOP_K = 3


def main() -> None:
    print("=" * 60)
    print("DAY 10 RERANKER TEST")
    print("=" * 60)
    print()

    retrieved_documents = retrieve_documents(
        query=QUESTION,
        top_k=INITIAL_TOP_K,
    )

    print("Initial vector retrieval:")
    print("-" * 60)

    for rank, document in enumerate(retrieved_documents, start=1):
        print(
            f"Rank {rank} | "
            f"{document.get('document_id')} | "
            f"Score: {document.get('score')}"
        )

    print()
    print("Applying reranker...")
    print()

    reranked_documents = rerank_documents(
        question=QUESTION,
        documents=retrieved_documents,
        top_k=FINAL_TOP_K,
    )

    print("Final reranked results:")
    print("-" * 60)

    for document in reranked_documents:
        print(
            f"Final Rank {document.get('rank')} | "
            f"{document.get('document_id')} | "
            f"Original Rank: {document.get('original_rank')} | "
            f"Original Score: {document.get('original_score')} | "
            f"Rerank Score: {document.get('rerank_score')}"
        )

    print()
    print("RERANKER TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()