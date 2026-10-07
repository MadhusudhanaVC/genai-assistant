from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source_path = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)


class ProcessingEvent(Base):
    __tablename__ = "processing_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String)
    event_type = Column(String)
    status = Column(String)
    error_message = Column(Text, nullable=True)
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
    latency_ms = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class GuardrailDecision(Base):
    __tablename__ = "guardrail_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, nullable=False)
    control = Column(String, nullable=False)
    outcome = Column(String, nullable=False)
    reason_code = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)