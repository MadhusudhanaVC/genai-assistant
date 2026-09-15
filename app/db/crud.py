from sqlalchemy.orm import Session

from app.db.models import (
    APIRequest,
    Document,
    ProcessingEvent,
    RequestSource,
    RequestStage,
)

def update_api_request(
    db: Session,
    request_id: str,
    total_latency_ms: int,
    outcome: str,
    error_category: str = None,
):
    request_log = (
        db.query(APIRequest)
        .filter(APIRequest.request_id == request_id)
        .first()
    )

    if request_log is None:
        raise ValueError(
            f"API request not found: {request_id}"
        )

    request_log.total_latency_ms = total_latency_ms
    request_log.outcome = outcome
    request_log.error_category = error_category

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

def create_api_request(
    db: Session,
    request_id: str,
    endpoint: str,
    started_at,
    model_version: str = None,
    prompt_version: str = None,
):
    request_log = APIRequest(
        request_id=request_id,
        endpoint=endpoint,
        started_at=started_at,
        model_version=model_version,
        prompt_version=prompt_version,
        outcome="IN_PROGRESS",
    )

    try:
        db.add(request_log)
        db.commit()
    except Exception:
        db.rollback()
        raise

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

def log_request_source(
    db: Session,
    request_id: str,
    source_id: str,
    score: float = None,
):
    source_log = RequestSource(
        request_id=request_id,
        source_id=source_id,
        score=score,
    )

    try:
        db.add(source_log)
        db.commit()
    except Exception:
        db.rollback()
        raise
def log_request_stage(
    db: Session,
    request_id: str,
    stage: str,
    status: str,
):
    stage_log = RequestStage(
        request_id=request_id,
        stage=stage,
        status=status,
    )

    try:
        db.add(stage_log)
        db.commit()
    except Exception:
        db.rollback()
        raise