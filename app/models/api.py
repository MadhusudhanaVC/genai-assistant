from datetime import datetime

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        description="Number of retrieved chunks",
    )
    min_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Minimum retrieval score",
    )


class AskResponse(BaseModel):
    answer: str
    status: str
    citations: list[str]
    sources: list[dict]


class VoiceAskResponse(BaseModel):
    answer: str
    status: str
    citations: list[str]
    sources: list[dict]
    transcript: str


class IngestResponse(BaseModel):
    processed_documents: int
    completed_documents: int
    failed_documents: int
    chunks: int
    indexed_chunks: int
    status: str


class DocumentResponse(BaseModel):
    document_id: str
    title: str
    content: str
    source_path: str
    updated_at: str
    status: str


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    request_id: str