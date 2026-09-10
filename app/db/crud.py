from sqlalchemy.orm import Session

from app.db.models import Document, ProcessingEvent


def save_document(db: Session, document):
    db_document = Document(
        document_id=document.document_id,
        title=document.title,
        content=document.content,
        source_path=document.source_path,
        updated_at=document.updated_at,
    )

    try:
        db.add(db_document)
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_document(db: Session, document_id: str):
    return (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )


def log_event(
    db: Session,
    document_id: str,
    event_type: str,
    status: str,
    error_message: str = None,
):
    event = ProcessingEvent(
        document_id=document_id,
        event_type=event_type,
        status=status,
        error_message=error_message,
    )

    try:
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()
        raise