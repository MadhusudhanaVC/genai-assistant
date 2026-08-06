"""
Database Tests
--------------

These tests verify database CRUD operations.
"""

from app.db.database import SessionLocal
from app.db.crud import log_event
from app.db.models import ProcessingEvent


# ==========================================================
# Test 5 - SQL Event Insertion
# ==========================================================
def test_sql_event_insertion():

    db = SessionLocal()

    # Insert one test event
    log_event(
        db=db,
        document_id="TEST001",
        event_type="TEST",
        status="SUCCESS"
    )

    # Read it back
    event = (
        db.query(ProcessingEvent)
        .filter(ProcessingEvent.document_id == "TEST001")
        .first()
    )

    assert event is not None
    assert event.document_id == "TEST001"
    assert event.event_type == "TEST"

    # Clean up (delete the test record)
    db.delete(event)
    db.commit()

    db.close()