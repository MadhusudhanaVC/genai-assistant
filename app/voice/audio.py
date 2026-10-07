import base64
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

STT_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
STT_MODEL = STT_MODEL = "openai/whisper-large-v3-turbo"

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024

SUPPORTED_AUDIO_FORMATS = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".flac": "flac",
    ".m4a": "m4a",
    ".ogg": "ogg",
    ".webm": "webm",
    ".aac": "aac",
}


class AudioValidationError(Exception):
    pass


class STTProviderError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        reason_code: str = "STT_PROVIDER_ERROR",
    ):
        super().__init__(message)
        self.status_code = status_code
        self.reason_code = reason_code


def transcribe_audio(
    audio_path: str,
    language: str | None = None,
) -> dict:
    path = Path(audio_path)

    if not path.exists():
        raise AudioValidationError("Audio file does not exist.")

    if not path.is_file():
        raise AudioValidationError("Audio path is not a file.")

    file_size = path.stat().st_size

    if file_size == 0:
        raise AudioValidationError("Audio file is empty.")

    if file_size > MAX_AUDIO_SIZE_BYTES:
        raise AudioValidationError(
            "Audio file exceeds the 10 MB size limit."
        )

    audio_format = SUPPORTED_AUDIO_FORMATS.get(
        path.suffix.lower()
    )

    if audio_format is None:
        raise AudioValidationError(
            "Unsupported audio format."
        )

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise STTProviderError(
            "OPENROUTER_API_KEY is not configured.",
            reason_code="STT_CONFIGURATION_ERROR",
        )

    audio_bytes = path.read_bytes()

    audio_base64 = base64.b64encode(
        audio_bytes
    ).decode("utf-8")

    payload = {
        "model": STT_MODEL,
        "input_audio": {
            "data": audio_base64,
            "format": audio_format,
        },
    }

    if language:
        payload["language"] = language

    start_time = time.perf_counter()

    try:
        response = requests.post(
            STT_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
    except requests.RequestException as error:
        raise STTProviderError(
            "STT provider request failed.",
            reason_code="STT_NETWORK_ERROR",
        ) from error

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    if not response.ok:
        reason_code = "STT_PROVIDER_ERROR"

        if response.status_code == 402:
            reason_code = "STT_CREDITS_REQUIRED"
        elif response.status_code == 401:
            reason_code = "STT_AUTHENTICATION_ERROR"
        elif response.status_code == 429:
            reason_code = "STT_RATE_LIMITED"

        raise STTProviderError(
            f"STT provider returned HTTP {response.status_code}.",
            status_code=response.status_code,
            reason_code=reason_code,
        )

    try:
        result = response.json()
    except ValueError as error:
        raise STTProviderError(
            "STT provider returned invalid JSON.",
            status_code=response.status_code,
            reason_code="STT_INVALID_RESPONSE",
        ) from error

    transcript = result.get("text")

    if not transcript or not transcript.strip():
        raise STTProviderError(
            "STT provider returned an empty transcript.",
            status_code=response.status_code,
            reason_code="STT_EMPTY_TRANSCRIPT",
        )

    detected_language = result.get("language") or language

    return {
        "text": transcript.strip(),
        "language": detected_language,
        "latency_ms": latency_ms,
        "model": STT_MODEL,
    }