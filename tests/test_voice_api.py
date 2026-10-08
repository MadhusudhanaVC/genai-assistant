from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_voice_ask_success(monkeypatch):
    def fake_transcribe_audio(audio_path):
        return {
            "text": "What is artificial intelligence?",
            "language": "en",
            "latency_ms": 120,
            "model": "small",
        }

    def fake_generate_grounded_answer(
        question,
        top_k,
        min_score,
        stage_logger,
    ):
        assert question == "What is artificial intelligence?"

        return {
            "answer": "Artificial intelligence enables machines to perform tasks that normally require human intelligence.",
            "status": "answered",
            "citations": ["doc-1"],
            "sources": [
                {
                    "chunk_id": "chunk-1",
                    "score": 0.91,
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.routes.transcribe_audio",
        fake_transcribe_audio,
    )

    monkeypatch.setattr(
        "app.api.routes.generate_grounded_answer",
        fake_generate_grounded_answer,
    )

    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "question.wav",
                b"fake audio data",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transcript"] == "What is artificial intelligence?"
    assert data["status"] == "answered"
    assert data["answer"] != ""
    assert data["citations"] == ["doc-1"]


def test_voice_ask_clear_audio(monkeypatch):
    def fake_transcribe_audio(audio_path):
        return {
            "text": "What is machine learning?",
            "language": "en",
            "latency_ms": 110,
            "model": "small",
        }

    def fake_generate_grounded_answer(
        question,
        top_k,
        min_score,
        stage_logger,
    ):
        assert question == "What is machine learning?"

        return {
            "answer": "Machine learning enables systems to learn patterns from data.",
            "status": "answered",
            "citations": ["doc-clear"],
            "sources": [
                {
                    "chunk_id": "chunk-clear",
                    "score": 0.92,
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.routes.transcribe_audio",
        fake_transcribe_audio,
    )

    monkeypatch.setattr(
        "app.api.routes.generate_grounded_answer",
        fake_generate_grounded_answer,
    )

    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "clear_question.wav",
                b"clear audio sample",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transcript"] == "What is machine learning?"
    assert data["status"] == "answered"
    assert data["citations"] == ["doc-clear"]


def test_voice_ask_background_noise(monkeypatch):
    def fake_transcribe_audio(audio_path):
        return {
            "text": "What is cloud computing?",
            "language": "en",
            "latency_ms": 145,
            "model": "small",
        }

    def fake_generate_grounded_answer(
        question,
        top_k,
        min_score,
        stage_logger,
    ):
        assert question == "What is cloud computing?"

        return {
            "answer": "Cloud computing provides on-demand access to computing resources.",
            "status": "answered",
            "citations": ["doc-noise"],
            "sources": [
                {
                    "chunk_id": "chunk-noise",
                    "score": 0.87,
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.routes.transcribe_audio",
        fake_transcribe_audio,
    )

    monkeypatch.setattr(
        "app.api.routes.generate_grounded_answer",
        fake_generate_grounded_answer,
    )

    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "background_noise.wav",
                b"audio with mild background noise",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transcript"] == "What is cloud computing?"
    assert data["status"] == "answered"
    assert data["citations"] == ["doc-noise"]


def test_voice_ask_domain_terms(monkeypatch):
    def fake_transcribe_audio(audio_path):
        return {
            "text": "Explain retrieval augmented generation and vector embeddings.",
            "language": "en",
            "latency_ms": 160,
            "model": "small",
        }

    def fake_generate_grounded_answer(
        question,
        top_k,
        min_score,
        stage_logger,
    ):
        assert question == (
            "Explain retrieval augmented generation and vector embeddings."
        )

        return {
            "answer": "RAG combines retrieval with generation, while vector embeddings represent information numerically.",
            "status": "answered",
            "citations": ["doc-domain"],
            "sources": [
                {
                    "chunk_id": "chunk-domain",
                    "score": 0.94,
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.routes.transcribe_audio",
        fake_transcribe_audio,
    )

    monkeypatch.setattr(
        "app.api.routes.generate_grounded_answer",
        fake_generate_grounded_answer,
    )

    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "domain_terms.wav",
                b"domain terminology audio",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transcript"] == (
        "Explain retrieval augmented generation and vector embeddings."
    )
    assert data["status"] == "answered"
    assert data["citations"] == ["doc-domain"]


def test_voice_ask_empty_audio():
    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "empty.wav",
                b"",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "HTTP_ERROR"


def test_voice_ask_unsupported_audio_type():
    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "question.txt",
                b"not audio",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "HTTP_ERROR"


def test_voice_ask_audio_size_limit():
    large_audio = b"0" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "large.wav",
                large_audio,
                "audio/wav",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "HTTP_ERROR"


def test_voice_ask_stt_local_failure(monkeypatch):
    from app.voice.audio import STTProviderError

    def fake_transcribe_audio(audio_path):
        raise STTProviderError(
            "Local STT transcription failed.",
            reason_code="STT_LOCAL_ERROR",
        )

    monkeypatch.setattr(
        "app.api.routes.transcribe_audio",
        fake_transcribe_audio,
    )

    response = client.post(
        "/voice/ask",
        files={
            "audio": (
                "question.wav",
                b"fake audio data",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 502
    assert response.json()["error_code"] == "STT_LOCAL_ERROR"