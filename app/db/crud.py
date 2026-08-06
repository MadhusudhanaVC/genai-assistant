"""
CRUD Operations
---------------

Purpose:
--------
This module contains all database operations for the project.

Current Operations:
1. Save a validated document.
2. Log processing events.

This separation keeps database logic independent from the CLI.
"""

# ==========================================================
# Third-Party Imports
# ==========================================================
from sqlalchemy.orm import Session

# ==========================================================
# Local Imports
# ==========================================================
from app.db.models import Document, ProcessingEvent


# ==========================================================
# Save Document
# ==========================================================
def save_document(db: Session, document):
    """
    Save a validated document into the documents table.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.

    document : Document (Pydantic Model)
        Validated document received from the CLI.

    Raises
    ------
    Exception
        Re-raises any database exception after performing rollback.
    """

    # Create SQLAlchemy model object
    db_document = Document(
        document_id=document.document_id,
        title=document.title,
        content=document.content,
        source_path=document.source_path,
        updated_at=document.updated_at
    )

    try:
        # Add document to session
        db.add(db_document)

        # Save changes to database
        db.commit()

    except Exception:
        # IMPORTANT:
        # If commit fails, SQLAlchemy keeps the session
        # in a failed state until rollback() is called.
        db.rollback()

        # Raise exception so the caller (CLI)
        # can log FAILED events.
        raise


# ==========================================================
# Log Processing Event
# ==========================================================
def log_event(
    db: Session,
    document_id: str,
    event_type: str,
    status: str,
    error_message: str = None
):
    """
    Store processing events in the database.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.

    document_id : str
        Unique document identifier.

    event_type : str
        Example:
        STARTED
        COMPLETED
        FAILED

    status : str
        SUCCESS or FAILED

    error_message : str, optional
        Stores exception details if processing fails.
    """

    event = ProcessingEvent(
        document_id=document_id,
        event_type=event_type,
        status=status,
        error_message=error_message
    )

    try:
        db.add(event)
        db.commit()

    except Exception:
        # Roll back failed transaction
        db.rollback()

        # Re-raise exception
        raise