import time
import uuid
from datetime import datetime

from fastapi import Request
from fastapi.concurrency import run_in_threadpool

from app.db.crud import create_api_request, update_api_request
from app.db.database import SessionLocal
from app.llm.client import MODEL_VERSION, ProviderError
from app.rag.generate import PROMPT_VERSION


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        await run_in_threadpool(
            create_request_log,
            request_id,
            request.url.path,
        )

        response = await call_next(request)

        total_latency_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        outcome = (
            "SUCCESS"
            if response.status_code < 400
            else "ERROR"
        )

        await run_in_threadpool(
            update_request_log,
            request_id,
            total_latency_ms,
            outcome,
            None,
        )

        response.headers["X-Request-ID"] = request_id

        return response

    except ProviderError:
        total_latency_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        try:
            await run_in_threadpool(
                update_request_log,
                request_id,
                total_latency_ms,
                "ERROR",
                "PROVIDER_ERROR",
            )
        except Exception:
            pass

        raise

    except Exception:
        total_latency_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        try:
            await run_in_threadpool(
                update_request_log,
                request_id,
                total_latency_ms,
                "ERROR",
                "INTERNAL_ERROR",
            )
        except Exception:
            pass

        raise


def create_request_log(
    request_id: str,
    endpoint: str,
):
    db = SessionLocal()

    try:
        create_api_request(
            db=db,
            request_id=request_id,
            endpoint=endpoint,
            started_at=datetime.utcnow(),
            model_version=MODEL_VERSION,
            prompt_version=PROMPT_VERSION,
        )
    finally:
        db.close()


def update_request_log(
    request_id: str,
    total_latency_ms: int,
    outcome: str,
    error_category: str = None,
):
    db = SessionLocal()

    try:
        update_api_request(
            db=db,
            request_id=request_id,
            total_latency_ms=total_latency_ms,
            outcome=outcome,
            error_category=error_category,
        )
    finally:
        db.close()