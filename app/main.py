from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.errors import (
    guardrail_exception_handler,
    http_exception_handler,
    internal_exception_handler,
    provider_exception_handler,
    stt_provider_exception_handler,
    validation_exception_handler,
)
from app.api.routes import register_routes
from app.core.config import settings
from app.llm.client import ProviderError
from app.middleware.request_logging import request_logging_middleware
from app.safety.guardrails import GuardrailBlockedError
from app.voice.audio import STTProviderError


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG == "True",
)

app.middleware("http")(request_logging_middleware)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    ProviderError,
    provider_exception_handler,
)

app.add_exception_handler(
    STTProviderError,
    stt_provider_exception_handler,
)

app.add_exception_handler(
    GuardrailBlockedError,
    guardrail_exception_handler,
)

app.add_exception_handler(
    Exception,
    internal_exception_handler,
)

register_routes(app)