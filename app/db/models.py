# Import SQLAlchemy column types
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
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


class APIRequest(Base):

    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)

    request_id = Column(String, unique=True, nullable=False)

    endpoint = Column(String, nullable=False)

    started_at = Column(DateTime, nullable=False)

    total_latency_ms = Column(Integer, nullable=True)

    model_version = Column(String, nullable=True)

    prompt_version = Column(String, nullable=True)

    outcome = Column(String, nullable=False)

    error_category = Column(String, nullable=True)


class RequestSource(Base):

    __tablename__ = "request_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)

    request_id = Column(String, nullable=False)

    source_id = Column(String, nullable=False)

    score = Column(Float, nullable=True)

class RequestStage(Base):
    __tablename__ = "request_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)