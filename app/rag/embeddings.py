from functools import lru_cache

from sentence_transformers import SentenceTransformer

# We use the same model for both documents and user queries.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Number of texts processed at a time.
DEFAULT_BATCH_SIZE = 16


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(
    texts: list[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[list[float]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    if not query or not query.strip():
        raise ValueError("query cannot be empty")

    return embed_texts(
        [query.strip()],
        batch_size=1,
    )[0]


def get_embedding_dimension() -> int:
    model = get_embedding_model()
    return model.get_embedding_dimension()