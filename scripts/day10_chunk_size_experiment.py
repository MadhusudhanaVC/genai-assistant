import json
from pathlib import Path

from app.rag.ingest import ingest_documents
from app.rag.retrieve import retrieve_documents


TEST_FILE = Path("datasets/day6_retrieval_test_cases.json")
CHROMA_PATH = Path("results/chroma_db_day10_chunk400")
COLLECTION_NAME = "day10_chunk400"
OUTPUT_FILE = Path(
    "results/day10_experiments/chunk400_results.json"
)

CHUNK_SIZE = 400
OVERLAP = 80
TOP_K = 3


def load_test_cases() -> list[dict]:
    with TEST_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_metrics(results: list[dict]) -> dict:
    total = len(results)

    hit_at_1 = sum(
        result["expected_rank"] == 1
        for result in results
    )

    hit_at_3 = sum(
        result["expected_rank"] is not None
        and result["expected_rank"] <= 3
        for result in results
    )

    reciprocal_ranks = [
        1 / result["expected_rank"]
        if result["expected_rank"] is not None
        else 0
        for result in results
    ]

    mrr = (
        sum(reciprocal_ranks) / total
        if total
        else 0
    )

    return {
        "total_questions": total,
        "hit_at_1": round(hit_at_1 / total, 4) if total else 0,
        "hit_at_3": round(hit_at_3 / total, 4) if total else 0,
        "mrr": round(mrr, 4),
    }


def run_experiment() -> list[dict]:
    test_cases = load_test_cases()
    results = []

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_document_id = test_case["expected_document_id"]

        retrieved = retrieve_documents(
            query=question,
            top_k=TOP_K,
            chroma_path=CHROMA_PATH,
            collection_name=COLLECTION_NAME,
        )

        expected_rank = None

        for rank, result in enumerate(retrieved, start=1):
            if result["document_id"] == expected_document_id:
                expected_rank = rank
                break

        result = {
            "question_number": index,
            "question": question,
            "expected_document_id": expected_document_id,
            "expected_rank": expected_rank,
            "hit_at_1": expected_rank == 1,
            "hit_at_3": (
                expected_rank is not None
                and expected_rank <= 3
            ),
            "reciprocal_rank": (
                round(1 / expected_rank, 4)
                if expected_rank is not None
                else 0
            ),
            "retrieved_documents": [
                {
                    "rank": rank,
                    "document_id": item["document_id"],
                    "chunk_id": item["chunk_id"],
                    "score": item["score"],
                    "title": item["title"],
                }
                for rank, item in enumerate(
                    retrieved,
                    start=1,
                )
            ],
        }

        results.append(result)

        status = "PASS" if result["hit_at_3"] else "FAIL"

        print(
            f"{index}. {status} - "
            f"{question} -> "
            f"expected {expected_document_id}, "
            f"rank {expected_rank}"
        )

    return results


def main() -> None:
    print("Building chunk-size experiment index...")
    print(f"Chunk size : {CHUNK_SIZE}")
    print(f"Overlap    : {OVERLAP}")
    print(f"Collection : {COLLECTION_NAME}")
    print()

    ingestion_result = ingest_documents(
        input_folder=Path("sample_data/day5_documents"),
        chunk_size=CHUNK_SIZE,
        overlap=OVERLAP,
        batch_size=16,
        chroma_path=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
    )

    print()
    print("Ingestion complete.")
    print(
        f"Documents processed : "
        f"{ingestion_result['processed_documents']}"
    )
    print(
        f"Documents completed : "
        f"{ingestion_result['completed_documents']}"
    )
    print(
        f"Chunks processed    : "
        f"{ingestion_result['chunks']}"
    )
    print(
        f"Indexed chunks      : "
        f"{ingestion_result['indexed_chunks']}"
    )
    print()

    results = run_experiment()
    metrics = calculate_metrics(results)

    report = {
        "day": 10,
        "experiment": "chunk_size",
        "configuration": {
            "chunk_size": CHUNK_SIZE,
            "overlap": OVERLAP,
            "top_k": TOP_K,
            "embedding_model": "all-MiniLM-L6-v2",
            "min_score": None,
            "metadata_filter": None,
            "chroma_path": str(CHROMA_PATH),
            "collection_name": COLLECTION_NAME,
        },
        "metrics": metrics,
        "question_results": results,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    print()
    print("========== CHUNK SIZE EXPERIMENT ==========")
    print(f"Hit@1 : {metrics['hit_at_1']}")
    print(f"Hit@3 : {metrics['hit_at_3']}")
    print(f"MRR   : {metrics['mrr']}")
    print(f"Report saved to: {OUTPUT_FILE}")
    print("============================================")


if __name__ == "__main__":
    main()