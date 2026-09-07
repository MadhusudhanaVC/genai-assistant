from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = None


def get_reranker() -> CrossEncoder:
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(MODEL_NAME)

    return _reranker


def rerank_documents(
    question: str,
    documents: list[dict],
    top_k: int = 3,
) -> list[dict]:
    if not question or not question.strip():
        raise ValueError("question cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    if not documents:
        return []

    reranker = get_reranker()

    pairs = [
        (question, document.get("text", ""))
        for document in documents
    ]

    scores = reranker.predict(pairs)

    reranked = []

    for original_rank, (document, rerank_score) in enumerate(
        zip(documents, scores),
        start=1,
    ):
        result = document.copy()
        result["original_rank"] = original_rank
        result["original_score"] = document.get("score")
        result["rerank_score"] = round(float(rerank_score), 4)
        reranked.append(result)

    reranked.sort(
        key=lambda result: result["rerank_score"],
        reverse=True,
    )

    reranked = reranked[:top_k]

    for final_rank, result in enumerate(reranked, start=1):
        result["rank"] = final_rank

    return reranked