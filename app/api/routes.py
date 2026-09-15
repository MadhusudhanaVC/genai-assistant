from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.crud import (
    get_document,
    log_request_source,
    log_request_stage,
)
from app.db.database import get_db
from app.models.api import (
    AskRequest,
    AskResponse,
    DocumentResponse,
    IngestResponse,
)
from app.rag.generate import generate_grounded_answer
from app.rag.ingest import ingest_documents


def register_routes(app: FastAPI):
    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.post("/ask", response_model=AskResponse)
    def ask(
        request: Request,
        body: AskRequest,
        db: Session = Depends(get_db),
    ):
        request_id = request.state.request_id

        def stage_logger(stage: str, status: str):
            log_request_stage(
                db=db,
                request_id=request_id,
                stage=stage,
                status=status,
            )

        result = generate_grounded_answer(
            question=body.question,
            top_k=body.top_k,
            min_score=body.min_score,
            stage_logger=stage_logger,
        )

        for source in result.get("sources", []):
            source_id = source.get("chunk_id")
            score = source.get("score")

            if source_id:
                log_request_source(
                    db=db,
                    request_id=request_id,
                    source_id=source_id,
                    score=score,
                )

        return result

    @app.post("/ingest", response_model=IngestResponse)
    def ingest():
        result = ingest_documents()

        return {
            **result,
            "status": "completed",
        }

    @app.get(
        "/documents/{document_id}",
        response_model=DocumentResponse,
    )
    def get_document_by_id(
        document_id: str,
        db: Session = Depends(get_db),
    ):
        document = get_document(
            db=db,
            document_id=document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        return {
            "document_id": document.document_id,
            "title": document.title,
            "content": document.content,
            "source_path": document.source_path,
            "updated_at": document.updated_at,
            "status": "completed",
        }