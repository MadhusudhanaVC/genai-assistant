from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to answer from the indexed documents",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        description="Maximum number of retrieved results",
    )
    min_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Optional minimum retrieval score",
    )


class AskResponse(BaseModel):
    answer: str
    status: str
    citations: list[str]
    sources: list[dict]


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