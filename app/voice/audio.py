import time
from pathlib import Path

from faster_whisper import WhisperModel


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

STT_MODEL = "small"
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"


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


_model = None


def get_stt_model() -> WhisperModel:
    global _model

    if _model is None:
        _model = WhisperModel(
            STT_MODEL,
            device=STT_DEVICE,
            compute_type=STT_COMPUTE_TYPE,
        )

    return _model


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

    start_time = time.perf_counter()

    try:
        model = get_stt_model()

        segments, info = model.transcribe(
            str(path),
            language=language,
        )

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )

    except Exception as error:
        latency_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        raise STTProviderError(
            "Local STT transcription failed.",
            reason_code="STT_LOCAL_ERROR",
        ) from error

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    if not transcript:
        raise STTProviderError(
            "Local STT returned an empty transcript.",
            reason_code="STT_EMPTY_TRANSCRIPT",
        )

    detected_language = getattr(
        info,
        "language",
        None,
    ) or language

    return {
        "text": transcript,
        "language": detected_language,
        "latency_ms": latency_ms,
        "model": STT_MODEL,
    }