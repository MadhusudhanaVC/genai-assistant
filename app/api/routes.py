from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db.crud import get_document
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
    def ask(request: AskRequest):
        result = generate_grounded_answer(
            question=request.question,
            top_k=request.top_k,
            min_score=request.min_score,
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

        