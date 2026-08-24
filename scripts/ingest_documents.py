import argparse
from pathlib import Path

from app.rag.ingest import ingest_documents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest approved documents into the RAG pipeline."
    )

    parser.add_argument(
        "input_folder",
        nargs="?",
        type=Path,
        default=Path("sample_data/day5_documents"),
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
        "--batch-size",
        type=int,
        default=16,
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
        raise ValueError(
            "chunk-size must be greater than zero"
        )

    if args.overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if args.overlap >= args.chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk-size"
        )

    if args.batch_size <= 0:
        raise ValueError(
            "batch-size must be greater than zero"
        )

    result = ingest_documents(
        input_folder=args.input_folder,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        batch_size=args.batch_size,
    )

    print()
    print("========== RAG INGESTION SUMMARY ==========")
    print(
        f"Documents processed : "
        f"{result['processed_documents']}"
    )
    print(
        f"Documents completed : "
        f"{result['completed_documents']}"
    )
    print(
        f"Documents failed    : "
        f"{result['failed_documents']}"
    )
    print(f"Chunks processed    : {result['chunks']}")
    print(
        f"Indexed chunks      : "
        f"{result['indexed_chunks']}"
    )
    print("============================================")


if __name__ == "__main__":
    main()