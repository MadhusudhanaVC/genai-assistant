from app.db.database import SessionLocal
from app.db.models import ProcessingEvent
from app.rag.generate import prepare_context
from app.rag.ingest import ingest_documents
from app.rag.retrieve import retrieve_documents


def test_ingest_then_retrieve(tmp_path):
    document = tmp_path / "DOC900_test_python.md"

    document.write_text(
        """---
document_id: DOC900
title: Test Python Document
category: python
updated_at: 2026-08-20
---

# Test Python Document

Python variables store values that a program can use later.
""",
        encoding="utf-8",
    )

    chroma_path = tmp_path / "chroma_test"

    result = ingest_documents(
        input_folder=tmp_path,
        chunk_size=500,
        overlap=80,
        batch_size=16,
        chroma_path=chroma_path,
        collection_name="test_collection",
    )

    assert result["completed_documents"] == 1
    assert result["failed_documents"] == 0
    assert result["chunks"] >= 1

    results = retrieve_documents(
        "What stores a value in Python?",
        top_k=3,
        min_score=0.3,
        chroma_path=chroma_path,
        collection_name="test_collection",
    )

    assert results

    document_ids = {
        result["document_id"]
        for result in results
    }

    assert "DOC900" in document_ids

    context = prepare_context(
        results,
        max_chunks=3,
        max_characters=3000,
    )

    assert "[DOC900 |" in context
    assert "Test Python Document" in context


def test_failed_document_does_not_stop_other_documents(tmp_path):
    good_document_1 = tmp_path / "DOC901_good_one.md"
    good_document_2 = tmp_path / "DOC902_good_two.md"
    bad_document = tmp_path / "DOC903_bad_document.md"

    good_document_1.write_text(
        """---
document_id: DOC901
title: Good Document One
category: python
updated_at: 2026-08-20
---

Python is a programming language.
""",
        encoding="utf-8",
    )

    good_document_2.write_text(
        """---
document_id: DOC902
title: Good Document Two
category: python
updated_at: 2026-08-20
---

Python functions organize reusable code.
""",
        encoding="utf-8",
    )

    bad_document.write_text(
        """---
document_id: DOC903
title: Bad Document
category: python
updated_at: 2026-08-20
---

""",
        encoding="utf-8",
    )

    chroma_path = tmp_path / "chroma_failure_test"

    result = ingest_documents(
        input_folder=tmp_path,
        chunk_size=500,
        overlap=80,
        batch_size=16,
        chroma_path=chroma_path,
        collection_name="failure_test_collection",
    )

    assert result["completed_documents"] == 2
    assert result["failed_documents"] == 1

    db = SessionLocal()

    try:
        failed_event = (
            db.query(ProcessingEvent)
            .filter(
                ProcessingEvent.document_id == "DOC903",
                ProcessingEvent.event_type == "FAILED",
                ProcessingEvent.status == "FAILED",
            )
            .first()
        )

        completed_event_1 = (
            db.query(ProcessingEvent)
            .filter(
                ProcessingEvent.document_id == "DOC901",
                ProcessingEvent.event_type == "COMPLETED",
                ProcessingEvent.status == "SUCCESS",
            )
            .first()
        )

        completed_event_2 = (
            db.query(ProcessingEvent)
            .filter(
                ProcessingEvent.document_id == "DOC902",
                ProcessingEvent.event_type == "COMPLETED",
                ProcessingEvent.status == "SUCCESS",
            )
            .first()
        )

        assert failed_event is not None
        assert completed_event_1 is not None
        assert completed_event_2 is not None

    finally:
        db.close()