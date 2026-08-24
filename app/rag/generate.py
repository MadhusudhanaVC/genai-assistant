DEFAULT_MAX_CONTEXT_CHUNKS = 3
DEFAULT_MAX_CONTEXT_CHARACTERS = 6000


def prepare_context(
    results: list[dict],
    max_chunks: int = DEFAULT_MAX_CONTEXT_CHUNKS,
    max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
) -> str:
    if max_chunks <= 0:
        raise ValueError("max_chunks must be greater than zero")

    if max_characters <= 0:
        raise ValueError("max_characters must be greater than zero")

    context_parts = []
    seen_chunks = set()
    total_characters = 0

    for result in results:
        chunk_id = result.get("chunk_id")

        if not chunk_id or chunk_id in seen_chunks:
            continue

        text = result.get("text", "").strip()

        if not text:
            continue

        if len(context_parts) >= max_chunks:
            break

        source_path = result.get("source_path") or "unknown"
        document_id = result.get("document_id") or "unknown"
        title = result.get("title") or "Untitled"

        source_label = f"[{document_id} | {chunk_id}]"

        block = (
            f"{source_label}\n"
            f"Title: {title}\n"
            f"Source: {source_path}\n\n"
            f"{text}"
        )

        remaining = max_characters - total_characters

        if remaining <= 0:
            break

        if len(block) > remaining:
            block = block[:remaining].rstrip()

        context_parts.append(block)
        seen_chunks.add(chunk_id)
        total_characters += len(block)

        if total_characters >= max_characters:
            break

    return "\n\n---\n\n".join(context_parts)