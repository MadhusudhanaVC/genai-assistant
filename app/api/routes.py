import json
import os
import tempfile
import time
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.db.crud import (
    get_document,
    log_guardrail_decision,
    log_request_source,
    log_request_stage,
)
from app.db.database import get_db
from app.models.api import (
    AskRequest,
    AskResponse,
    DocumentResponse,
    IngestResponse,
    VoiceAskResponse,
)
from app.rag.generate import generate_grounded_answer
from app.rag.ingest import ingest_documents
from app.safety.guardrails import (
    GuardrailBlockedError,
    evaluate_question,
)
from app.voice.audio import (
    AudioValidationError,
    STTProviderError,
    transcribe_audio,
)


MAX_VOICE_UPLOAD_SIZE = 10 * 1024 * 1024

SUPPORTED_VOICE_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/flac",
    "audio/mp4",
    "audio/x-m4a",
    "audio/ogg",
    "audio/webm",
    "audio/aac",
}


def process_question(
    db: Session,
    request_id: str,
    question: str,
    top_k: int = 3,
    min_score: float | None = None,
) -> dict:
    decision = evaluate_question(question)

    log_guardrail_decision(
        db=db,
        request_id=request_id,
        control=decision.control,
        outcome="ALLOWED" if decision.allowed else "BLOCKED",
        reason_code=decision.reason_code,
    )

    if not decision.allowed:
        raise GuardrailBlockedError(decision)

    def stage_logger(stage: str, status: str):
        log_request_stage(
            db=db,
            request_id=request_id,
            stage=stage,
            status=status,
        )

    rag_start_time = time.perf_counter()

    log_request_stage(
        db=db,
        request_id=request_id,
        stage="RAG",
        status="STARTED",
    )

    try:
        result = generate_grounded_answer(
            question=question,
            top_k=top_k,
            min_score=min_score,
            stage_logger=stage_logger,
        )
    except Exception as error:
        rag_latency_ms = round(
            (time.perf_counter() - rag_start_time) * 1000
        )

        log_request_stage(
            db=db,
            request_id=request_id,
            stage="RAG",
            status="FAILED",
            latency_ms=rag_latency_ms,
            details=json.dumps(
                {
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            ),
        )

        raise

    rag_latency_ms = round(
        (time.perf_counter() - rag_start_time) * 1000
    )

    log_request_stage(
        db=db,
        request_id=request_id,
        stage="RAG",
        status="SUCCESS",
        latency_ms=rag_latency_ms,
        details=json.dumps(
            {
                "question": question,
                "status": result.get("status"),
                "source_count": len(result.get("sources", [])),
            }
        ),
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

        return process_question(
            db=db,
            request_id=request_id,
            question=body.question,
            top_k=body.top_k,
            min_score=body.min_score,
        )

    @app.post(
        "/voice/ask",
        response_model=VoiceAskResponse,
    )
    def voice_ask(
        request: Request,
        audio: UploadFile = File(...),
        db: Session = Depends(get_db),
    ):
        request_id = request.state.request_id

        if not audio.filename:
            raise HTTPException(
                status_code=400,
                detail="Audio filename is required.",
            )

        if audio.content_type not in SUPPORTED_VOICE_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported audio format.",
            )

        audio.file.seek(0)

        audio_bytes = audio.file.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=400,
                detail="Audio file is empty.",
            )

        if len(audio_bytes) > MAX_VOICE_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Audio file exceeds the 10 MB size limit.",
            )

        suffix = Path(audio.filename).suffix.lower()

        if not suffix:
            raise HTTPException(
                status_code=400,
                detail="Audio file extension is required.",
            )

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temporary_file:
                temporary_file.write(audio_bytes)
                temporary_path = temporary_file.name

            log_request_stage(
                db=db,
                request_id=request_id,
                stage="STT",
                status="STARTED",
            )

            stt_start_time = time.perf_counter()

            try:
                transcription = transcribe_audio(
                    temporary_path,
                )
            except AudioValidationError as error:
                stt_latency_ms = round(
                    (time.perf_counter() - stt_start_time) * 1000
                )

                log_request_stage(
                    db=db,
                    request_id=request_id,
                    stage="STT",
                    status="FAILED",
                    latency_ms=stt_latency_ms,
                    details=json.dumps(
                        {
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    ),
                )

                raise
            except STTProviderError as error:
                stt_latency_ms = round(
                    (time.perf_counter() - stt_start_time) * 1000
                )

                log_request_stage(
                    db=db,
                    request_id=request_id,
                    stage="STT",
                    status="FAILED",
                    latency_ms=stt_latency_ms,
                    details=json.dumps(
                        {
                            "error_type": type(error).__name__,
                            "error": str(error),
                            "reason_code": error.reason_code,
                            "status_code": error.status_code,
                        }
                    ),
                )

                raise

            transcript = transcription["text"]

            voice_details = {
                "filename": audio.filename,
                "content_type": audio.content_type,
                "size_bytes": len(audio_bytes),
                "language": transcription.get("language"),
                "model": transcription.get("model"),
                "transcript": transcript,
            }

            log_request_stage(
                db=db,
                request_id=request_id,
                stage="STT",
                status="SUCCESS",
                latency_ms=transcription.get("latency_ms"),
                details=json.dumps(voice_details),
            )

            result = process_question(
                db=db,
                request_id=request_id,
                question=transcript,
            )

            return {
                **result,
                "transcript": transcript,
            }

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)

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