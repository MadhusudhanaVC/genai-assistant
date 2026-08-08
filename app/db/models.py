# Import SQLAlchemy column types
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

# Import the Base class from database.py
from app.db.database import Base


class Document(Base):


    # Table name inside SQLite
    __tablename__ = "documents"

    # Primary Key
    document_id = Column(String, primary_key=True)

    # Document title
    title = Column(String, nullable=False)

    # Document content
    content = Column(Text, nullable=False)

    # Original file path
    source_path = Column(String, nullable=False)

    # Last updated date
    updated_at = Column(String, nullable=False)


class ProcessingEvent(Base):

    # Table name
    __tablename__ = "processing_events"

    # Auto Increment ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Document ID
    document_id = Column(String)

    # STARTED / COMPLETED / FAILED
    event_type = Column(String)

    # SUCCESS / FAILED
    status = Column(String)

    # Error message if failed
    error_message = Column(Text, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)