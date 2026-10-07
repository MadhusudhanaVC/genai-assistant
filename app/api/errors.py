from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.llm.client import ProviderError
from app.safety.guardrails import GuardrailBlockedError
from app.voice.audio import STTProviderError


def error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": error_code,
            "message": message,
            "request_id": request.state.request_id,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return error_response(
        request=request,
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="The request data is invalid.",
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    if exc.status_code == 404:
        error_code = "DOCUMENT_NOT_FOUND"
        message = "The requested document was not found."
    else:
        error_code = "HTTP_ERROR"
        message = "The request could not be completed."

    return error_response(
        request=request,
        status_code=exc.status_code,
        error_code=error_code,
        message=message,
    )


async def provider_exception_handler(
    request: Request,
    exc: ProviderError,
):
    return error_response(
        request=request,
        status_code=502,
        error_code="PROVIDER_ERROR",
        message="The language model provider could not complete the request.",
    )


async def stt_provider_exception_handler(
    request: Request,
    exc: STTProviderError,
):
    if exc.reason_code == "STT_CREDITS_REQUIRED":
        status_code = 402
        message = "Speech-to-text service credits are required."
    elif exc.reason_code == "STT_AUTHENTICATION_ERROR":
        status_code = 502
        message = "Speech-to-text authentication failed."
    elif exc.reason_code == "STT_RATE_LIMITED":
        status_code = 429
        message = "Speech-to-text service rate limit was reached."
    elif exc.reason_code == "STT_NETWORK_ERROR":
        status_code = 502
        message = "Speech-to-text service could not be reached."
    else:
        status_code = 502
        message = "Speech-to-text service could not complete the request."

    return error_response(
        request=request,
        status_code=status_code,
        error_code=exc.reason_code,
        message=message,
    )


async def guardrail_exception_handler(
    request: Request,
    exc: GuardrailBlockedError,
):
    return error_response(
        request=request,
        status_code=400,
        error_code="GUARDRAIL_BLOCKED",
        message="The request was blocked by a safety control.",
    )


async def internal_exception_handler(
    request: Request,
    exc: Exception,
):
    return error_response(
        request=request,
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="An internal server error occurred.",
    )