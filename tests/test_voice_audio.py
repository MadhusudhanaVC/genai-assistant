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


def test_local_stt_transcription(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio data")

    class FakeSegment:
        def __init__(self, text):
            self.text = text

    class FakeInfo:
        language = "en"

    class FakeModel:
        def transcribe(self, audio_path, language=None):
            assert audio_path == str(audio_file)
            assert language is None

            return (
                [
                    FakeSegment("What is retrieval augmented generation?")
                ],
                FakeInfo(),
            )

    monkeypatch.setattr(
        "app.voice.audio.get_stt_model",
        lambda: FakeModel(),
    )

    result = transcribe_audio(str(audio_file))

    assert result["text"] == (
        "What is retrieval augmented generation?"
    )
    assert result["language"] == "en"
    assert result["model"] == "small"
    assert isinstance(result["latency_ms"], int)
    assert result["latency_ms"] >= 0


def test_local_stt_with_requested_language(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio data")

    class FakeSegment:
        text = "What is RAG?"

    class FakeInfo:
        language = "en"

    class FakeModel:
        def transcribe(self, audio_path, language=None):
            assert language == "en"

            return (
                [FakeSegment()],
                FakeInfo(),
            )

    monkeypatch.setattr(
        "app.voice.audio.get_stt_model",
        lambda: FakeModel(),
    )

    result = transcribe_audio(
        str(audio_file),
        language="en",
    )

    assert result["text"] == "What is RAG?"
    assert result["language"] == "en"
    assert result["model"] == "small"


def test_local_stt_failure(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio data")

    class FakeModel:
        def transcribe(self, audio_path, language=None):
            raise RuntimeError("transcription failed")

    monkeypatch.setattr(
        "app.voice.audio.get_stt_model",
        lambda: FakeModel(),
    )

    with pytest.raises(STTProviderError) as exc_info:
        transcribe_audio(str(audio_file))

    error = exc_info.value

    assert error.reason_code == "STT_LOCAL_ERROR"


def test_empty_transcript(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio data")

    class FakeSegment:
        text = "   "

    class FakeInfo:
        language = "en"

    class FakeModel:
        def transcribe(self, audio_path, language=None):
            return (
                [FakeSegment()],
                FakeInfo(),
            )

    monkeypatch.setattr(
        "app.voice.audio.get_stt_model",
        lambda: FakeModel(),
    )

    with pytest.raises(STTProviderError) as exc_info:
        transcribe_audio(str(audio_file))

    error = exc_info.value

    assert error.reason_code == "STT_EMPTY_TRANSCRIPT"