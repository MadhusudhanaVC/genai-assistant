from pathlib import Path

import pytest

from app.voice.audio import (
    AudioValidationError,
    STTProviderError,
    transcribe_audio,
)


def test_missing_audio_file():
    with pytest.raises(
        AudioValidationError,
        match="Audio file does not exist.",
    ):
        transcribe_audio("does_not_exist.wav")


def test_empty_audio_file(tmp_path: Path):
    audio_file = tmp_path / "empty.wav"
    audio_file.write_bytes(b"")

    with pytest.raises(
        AudioValidationError,
        match="Audio file is empty.",
    ):
        transcribe_audio(str(audio_file))


def test_unsupported_audio_format(tmp_path: Path):
    audio_file = tmp_path / "unsupported.txt"
    audio_file.write_text("test audio content")

    with pytest.raises(
        AudioValidationError,
        match="Unsupported audio format.",
    ):
        transcribe_audio(str(audio_file))


def test_stt_provider_402_error(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio data")

    class FakeResponse:
        status_code = 402
        ok = False

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.voice.audio.requests.post",
        fake_post,
    )

    with pytest.raises(STTProviderError) as exc_info:
        transcribe_audio(str(audio_file))

    error = exc_info.value

    assert error.status_code == 402
    assert error.reason_code == "STT_CREDITS_REQUIRED"


def test_audio_file_size_limit(tmp_path: Path):
    audio_file = tmp_path / "large.wav"
    audio_file.write_bytes(
        b"0" * (10 * 1024 * 1024 + 1)
    )

    with pytest.raises(
        AudioValidationError,
        match="Audio file exceeds the 10 MB size limit.",
    ):
        transcribe_audio(str(audio_file))


def test_stt_provider_detected_language(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio data")

    class FakeResponse:
        status_code = 200
        ok = True

        def json(self):
            return {
                "text": "What is retrieval augmented generation?",
                "language": "en",
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.voice.audio.requests.post",
        fake_post,
    )

    result = transcribe_audio(str(audio_file))

    assert result["text"] == (
        "What is retrieval augmented generation?"
    )
    assert result["language"] == "en"
    assert result["model"] == "openai/whisper-large-v3-turbo"
    assert isinstance(result["latency_ms"], int)