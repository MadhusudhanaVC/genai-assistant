import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from app.rag.chunking import chunk_text


SUPPORTED_EXTENSIONS = {".md", ".txt", ".html"}


def get_document_id(file_path: Path) -> str:
    match = re.match(r"^(DOC\d+)_", file_path.stem)

    if not match:
        raise ValueError(f"Document ID not found in filename: {file_path.name}")

    return match.group(1)


def read_document(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def remove_front_matter(text: str) -> str:
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return text.strip()

    end_index = None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise ValueError("Document front matter is not closed")

    content = "\n".join(lines[end_index + 1:])

    return content.strip()


def get_title(text: str, file_path: Path) -> str:
    for line in text.splitlines():
        line = line.strip()

        if line.startswith("# "):
            return line[2:].strip()

    return file_path.stem.replace("_", " ").title()


def get_category(file_path: Path) -> str:
    name = file_path.stem.lower()

    if "python" in name:
        return "python"

    if "git" in name:
        return "git"

    if "sql" in name or "database" in name:
        return "database"

    if "api" in name or "http" in name or "fastapi" in name:
        return "api"

    if "artificial" in name or "machine" in name:
        return "ai"

    return "general"


def get_updated_at(file_path: Path) -> str:
    timestamp = file_path.stat().st_mtime

    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def build_chunks(
    file_path: Path,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    raw_text = read_document(file_path)
    document_text = remove_front_matter(raw_text)

    if not document_text:
        raise ValueError("Document is empty after cleaning")

    document_id = get_document_id(file_path)
    title = get_title(document_text, file_path)
    category = get_category(file_path)
    updated_at = get_updated_at(file_path)

    chunks = chunk_text(
        document_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not chunks:
        raise ValueError("Document produced no chunks")

    results = []

    for index, text in enumerate(chunks):
        cleaned_text = text.strip()

        if not cleaned_text:
            continue

        results.append(
            {
                "chunk_id": f"{document_id}_CHUNK_{index + 1:03d}",
                "document_id": document_id,
                "title": title,
                "source_path": str(file_path),
                "updated_at": updated_at,
                "chunk_index": index,
                "category": category,
                "text": cleaned_text,
            }
        )

    if not results:
        raise ValueError("Document produced only empty chunks")

    return results


def process_documents(
    input_folder: Path,
    chunk_size: int,
    overlap: int,
) -> tuple[list[dict], int, list[dict]]:
    files = sorted(
        file_path
        for file_path in input_folder.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        raise ValueError(f"No supported documents found in {input_folder}")

    all_chunks = []
    processed_documents = 0
    failed_documents = []

    for file_path in files:
        try:
            chunks = build_chunks(
                file_path,
                chunk_size,
                overlap,
            )

            all_chunks.extend(chunks)
            processed_documents += 1

            print(
                f"Processed {file_path.name}: "
                f"{len(chunks)} chunks"
            )

        except Exception as error:
            failed_documents.append(
                {
                    "file": str(file_path),
                    "error": str(error),
                }
            )

            print(
                f"Failed {file_path.name}: {error}"
            )

    return all_chunks, processed_documents, failed_documents


def save_jsonl(chunks: list[dict], output_file: Path) -> None:
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        for chunk in chunks:
            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare documents and create traceable chunks."
    )

    parser.add_argument(
        "input_folder",
        type=Path,
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=80,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/chunks.jsonl"),
    )

    args = parser.parse_args()

    if not args.input_folder.exists():
        raise FileNotFoundError(
            f"Input folder not found: {args.input_folder}"
        )

    if not args.input_folder.is_dir():
        raise ValueError(
            f"Input path is not a folder: {args.input_folder}"
        )

    if args.chunk_size <= 0:
        raise ValueError("chunk-size must be greater than zero")

    if args.overlap < 0:
        raise ValueError("overlap cannot be negative")

    if args.overlap >= args.chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk-size"
        )

    chunks, processed, failed = process_documents(
        args.input_folder,
        args.chunk_size,
        args.overlap,
    )

    save_jsonl(
        chunks,
        args.output,
    )

    print()
    print("========== PREPROCESSING SUMMARY ==========")
    print(f"Documents processed : {processed}")
    print(f"Documents failed    : {len(failed)}")
    print(f"Total chunks        : {len(chunks)}")
    print(f"Output              : {args.output}")
    print("============================================")

    if failed:
        print()
        print("Failed documents:")

        for item in failed:
            print(
                f"- {item['file']}: {item['error']}"
            )

        raise SystemExit(1)


if __name__ == "__main__":
    main()