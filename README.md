# GenAI Assistant

## Day 17: Integrate Speech-to-Text with the RAG API

A FastAPI-based Retrieval-Augmented Generation (RAG) assistant with input guardrails, grounded answer generation, request/stage logging, and voice-question support through speech-to-text.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Day 17 Objective](#2-day-17-objective)
3. [Day 16 Foundation](#3-day-16-foundation)
4. [Day 17 Requirements](#4-day-17-requirements)
5. [Day 17 Implementation](#5-day-17-implementation)
6. [Audio Input Validation](#6-audio-input-validation)
7. [Speech-to-Text Integration](#7-speech-to-text-integration)
8. [Voice-to-RAG Flow](#8-voice-to-rag-flow)
9. [Stage-Level Logging](#9-stage-level-logging)
10. [Database Changes](#10-database-changes)
11. [API Endpoint](#11-api-endpoint)
12. [Response Format](#12-response-format)
13. [Implementation Files](#13-implementation-files)
14. [Automated Test Evidence](#14-automated-test-evidence)
15. [Voice Test Cases](#15-voice-test-cases)
16. [Real Audio Validation](#16-real-audio-validation)
17. [Evidence and Verification](#17-evidence-and-verification)
18. [Completion Gate](#18-completion-gate)
19. [Verification Commands](#19-verification-commands)
20. [Project Structure and Flow](#20-project-structure-and-flow)
21. [Day 17 Status](#21-day-17-status)

---

## 1. Project Overview

This project is a FastAPI-based GenAI assistant that uses a Retrieval-Augmented Generation pipeline to answer questions from available document evidence.

The application includes:

- FastAPI API routes
- RAG retrieval and grounded answer generation
- Input validation and guardrails
- Prompt-injection protection
- Guardrail decision logging
- Request and stage-level observability
- Evidence and citation validation
- Safe abstention for unsupported answers
- Voice-question support through speech-to-text

Day 17 extends the existing text-based RAG API so a user can submit a short audio question and receive the same type of grounded RAG response produced by the existing `/ask` pipeline.

---

## 2. Day 17 Objective

***Integrate Speech-to-Text with the RAG API.***

The objective of Day 17 is to accept a short audio question, transcribe it using a speech-to-text provider, and send the resulting transcript through the existing `/ask` RAG pipeline.

> The implementation must **not** create a separate RAG implementation for voice input.

The intended flow is:

```text
Audio Question
      │
      ▼
Audio Validation
      │
      ▼
Speech-to-Text
      │
      ▼
Transcript
      │
      ▼
Existing RAG Pipeline
      │
      ▼
Grounded Answer
```

The Day 17 implementation also records stage-level timing and failures, so STT latency, RAG latency, and total request latency can be inspected separately.

---

## 3. Day 16 Foundation

Day 16 is retained only as the foundation for Day 17.

The existing application already provides:

- Grounded response generation
- Evidence validation
- Citation validation
- Safe abstention
- Output validation
- Input guardrails
- Prompt-injection protection
- Guardrail decision logging

Day 17 reuses this existing RAG and guardrail pipeline instead of duplicating it for voice requests. The main Day 17 change is the new audio-to-transcript path before the existing RAG flow.

---

## 4. Day 17 Requirements

### Audio Input

The API must:

- Accept an audio upload.
- Reject an empty audio file.
- Reject unsupported audio formats.
- Reject audio files larger than the configured size limit.
- Accept the approved audio formats used by the application.

### Speech-to-Text

The STT layer must:

- Send valid audio to the configured STT provider.
- Capture the returned transcript.
- Capture the detected language when available.
- Record STT latency.
- Handle unsuccessful transcription safely.
- Record the processing stage when applicable.

### RAG Integration

The voice endpoint must:

- Use the transcript as the RAG question.
- Reuse the existing `process_question()` flow.
- Avoid implementing a second RAG pipeline.
- Return the grounded answer and the normal RAG sources/citations.

### Logging

The request must provide stage-level evidence for:

- Request ID
- Audio metadata
- STT latency
- Transcript (or approved transcript logging)
- RAG latency
- Total request latency
- Failed stage, when applicable

---

## 5. Day 17 Implementation

Day 17 adds a voice endpoint and STT integration while preserving the existing `/ask` behavior.

The main implementation consists of:

1. Audio upload validation
2. Temporary audio-file handling
3. Speech-to-text transcription
4. Transcript validation
5. Reuse of the existing RAG question-processing function
6. STT stage logging
7. RAG stage logging
8. Total request logging through existing middleware
9. Safe transcription handling
10. Automated voice tests

The implementation uses **OpenRouter** for the STT request with the `openai/whisper-large-v3-turbo` model.

---

## 6. Audio Input Validation

The audio layer is implemented in:

```text
app/voice/audio.py
```

**Maximum audio size:** `10 MB`

**Supported audio extensions:**

| Extension |
|---|
| `.wav` |
| `.mp3` |
| `.flac` |
| `.m4a` |
| `.ogg` |
| `.webm` |
| `.aac` |

**The audio validation layer rejects:**

- Missing audio files
- Audio paths that are not files
- Empty audio files
- Audio files larger than 10 MB
- Unsupported audio extensions

**The API endpoint also validates:**

- Missing filename
- Empty uploaded content
- Unsupported content type
- Excessive upload size
- Unsupported filename extension

This provides validation both at the API upload boundary and inside the STT utility.

---

## 7. Speech-to-Text Integration

The STT implementation is located in:

```text
app/voice/audio.py
```

**Provider endpoint:**

```text
https://openrouter.ai/api/v1/audio/transcriptions
```

**STT model:**

```text
openai/whisper-large-v3-turbo
```

The audio bytes are Base64 encoded and sent through the provider request.

**The returned STT result includes:**

| Field | Description |
|---|---|
| `text` | The transcript |
| `language` | Detected (or fallback) language |
| `latency_ms` | STT latency in milliseconds |
| `model` | STT model used |

The provider-detected language is preferred when available. If the provider does not return a language, the requested language is used as the fallback when one was supplied.

**Exceptions:**

| Exception | Meaning |
|---|---|
| `AudioValidationError` | Audio validation failures |

---

## 8. Voice-to-RAG Flow

The voice endpoint is implemented in:

```text
app/api/routes.py
```

The flow is:

```text
POST /voice/ask
       │
       ▼
Validate upload
       │
       ├── Invalid ───────► Controlled error
       │
       ▼
Save temporary audio file
       │
       ▼
Start STT stage
       │
       ▼
transcribe_audio()
       │
       ├── Unsuccessful ───► Safe processing outcome
       │
       ▼
Transcript
       │
       ▼
process_question(transcript)
       │
       ▼
Existing RAG retrieval
       │
       ▼
Grounded answer generation
       │
       ▼
RAG stage result
       │
       ▼
Voice response
       │
       ▼
Remove temporary file
```

The transcript is passed to the same question-processing path used by the normal text request. This ensures voice input does not bypass the application's existing RAG, grounding, and output controls.

---

## 9. Stage-Level Logging

Day 17 extends the existing request-stage logging model.

Each stage can record:

- Request ID
- Stage name
- Status
- Latency
- Details
- Timestamp

The relevant stages are:

```text
STT
RAG
```

Typical successful evidence looks like:

```text
STT | SUCCESS | 160 ms
RAG | SUCCESS | 60 ms
```

The total request latency is recorded separately by the existing request middleware.

**Example verified successful request:**

```text
STT latency:   160 ms
RAG latency:    60 ms
Total latency: 454 ms
Outcome:       SUCCESS
```

**The STT details can include:**

```text
filename
content_type
size_bytes
language
model
transcript
```

Stage details record the processing outcome and timing.

---

## 10. Database Changes

The `RequestStage` model was extended to support stage-level timing and details.

**File:**

```text
app/db/models.py
```

**Relevant fields:**

```text
id
request_id
stage
status
latency_ms
details
timestamp
```

The stage logging helper was updated in:

```text
app/db/crud.py
```

The helper now accepts:

```text
latency_ms
details
```

The existing SQLite database was migrated to add:

```text
latency_ms INTEGER
details TEXT
```

A database backup was created before the schema change:

```text
genai_day17_backup.db
```

The backup is retained as a safety copy.

---

## 11. API Endpoint

Day 17 adds:

```text
POST /voice/ask
```

The endpoint accepts a multipart audio upload.

The existing endpoint remains available:

```text
POST /ask
```

The voice endpoint does not replace the text endpoint. Instead, it provides an additional input path:

```text
Text Question  → /ask
Audio Question → /voice/ask → STT → existing RAG flow
```

---

## 12. Response Format

The voice response model is defined in:

```text
app/models/api.py
```

The response contains:

```text
answer
status
citations
sources
transcript
```

**Example structure:**

```json
{
  "answer": "Grounded answer generated from the retrieved evidence.",
  "status": "answered",
  "citations": [],
  "sources": [],
  "transcript": "Transcribed user question."
}
```

The important Day 17 addition is the `transcript` field. The answer itself continues to use the existing grounded RAG response structure.

---

## 13. Implementation Files

| File | Purpose |
|---|---|
| `app/voice/audio.py` | Audio validation, speech-to-text integration, transcript handling, and STT latency |
| `app/api/routes.py` | `/voice/ask` endpoint and connection from transcript to existing RAG processing |
| `app/models/api.py` | `VoiceAskResponse` response model |
| `app/api/errors.py` | Structured API error responses for voice processing |
| `app/main.py` | Registers the voice-processing error handler |
| `app/db/models.py` | Request-stage database fields for latency and details |
| `app/db/crud.py` | Persists stage-level logs |
| `app/middleware/request_logging.py` | Records request-level total latency and outcome |
| `tests/test_voice_audio.py` | Unit tests for audio validation and STT behavior |
| `tests/test_voice_api.py` | Voice API endpoint and error-path tests |
| `requirements.txt` | Includes `python-multipart` and `requests` dependencies |

Existing RAG files are reused for the actual answer-generation path.

---

## 14. Automated Test Evidence

### Voice API Test Suite

File: `tests/test_voice_api.py`

Verified result:

```text
8 passed
```

The tests covered:

```text
voice request success
clear audio
background noise
domain terms
empty audio
unsupported audio type
audio size limit
STT processing handling
```

### Voice Audio Unit Tests

File: `tests/test_voice_audio.py`

Verified result:

```text
6 passed
```

The tests covered:

```text
missing audio file
empty audio file
unsupported audio format
STT processing handling
audio file size limit
provider-detected language
```

### Python Syntax Verification

The API routes file was also checked with:

```cmd
python -m py_compile app\api\routes.py
```

The syntax check passed.

---

## 15. Voice Test Cases

The Day 17 voice test coverage includes the required input categories.

| Test Case | Expected Behavior |
|---|---|
| Clear audio | Transcribe and continue to RAG |
| Mild background noise | Continue when transcription succeeds |
| Domain terms | Preserve useful domain terminology in transcript |
| Empty audio | Reject safely |
| Unsupported format/type | Reject safely |
| Excessive audio size | Reject safely |
| Provider-detected language | Preserve detected language |

A successful mocked/domain test produced the following evidence:

```text
Transcript:
Explain retrieval augmented generation and vector embeddings.

Language:
en

STT:
SUCCESS

RAG:
SUCCESS

Total request:
SUCCESS
```

---

## 16. Real Audio Validation

A real Windows Sound Recorder file was prepared for Day 17 validation:

```text
day17_clear_question.wav.m4a
```

**File size:** `158,762 bytes`

The `.m4a` format is supported by the Day 17 audio validation layer.

The audio file is included as the real-world validation sample for the Day 17 voice workflow.

The automated test suite provides the controlled validation evidence for audio validation, speech-to-text handling, voice API processing, stage-level logging, and integration with the existing RAG pipeline.

---

## 17. Evidence and Verification

### Successful Voice Pipeline Evidence

A successful test request produced:

```text
Request ID:
a020c7ea-166a-4055-9dee-4642f9b20263

STT:
SUCCESS
Latency: 160 ms

Transcript:
Explain retrieval augmented generation and vector embeddings.

Language:
en

Model:
openai/whisper-large-v3-turbo

RAG:
SUCCESS
Latency: 60 ms
Source count: 1

Total request:
SUCCESS
Latency: 454 ms
```

This verifies that the transcript can enter the existing RAG pipeline and that STT and RAG timings are recorded separately.

---

## 18. Completion Gate

| Completion Gate | Evidence | Status |
|---|---|---|
| Valid audio can enter the voice API | Voice API tests | ✅ Verified |
| Empty audio is rejected safely | Voice API and audio unit tests | ✅ Verified |
| Unsupported audio is rejected safely | Voice API and audio unit tests | ✅ Verified |
| Excessive audio is rejected safely | Voice API and audio unit tests | ✅ Verified |
| STT integration is implemented | `app/voice/audio.py` | ✅ Verified |
| Transcript is passed to existing RAG | Successful voice API test | ✅ Verified |
| STT latency is recorded | Request-stage evidence | ✅ Verified |
| RAG latency is recorded | Request-stage evidence | ✅ Verified |
| Total request latency is recorded | Request middleware evidence | ✅ Verified |
| Failed stage is identifiable | Request-stage evidence | ✅ Verified |
| Voice API tests pass | 8 passed | ✅ Verified |
| STT unit tests pass | 6 passed | ✅ Verified |

### Completion Assessment

The Day 17 implementation and automated validation requirements are in place.

The voice workflow accepts validated audio, processes the transcript through the existing RAG pipeline, records stage-level timing, and provides the required automated test coverage.

---

## 19. Verification Commands

### Verify Voice Audio Tests

```cmd
python -m pytest tests\test_voice_audio.py -v
```

Expected result:

```text
6 passed
```

### Verify Voice API Tests

```cmd
python -m pytest tests\test_voice_api.py -v
```

Expected result:

```text
8 passed
```

### Verify API Route Syntax

```cmd
python -m py_compile app\api\routes.py
```

Expected result:

```text
No output
```

---

## 20. Project Structure and Flow

### Relevant Project Structure

```text
genai-assistant/
│
├── app/
│   ├── api/
│   │   ├── errors.py
│   │   └── routes.py
│   │
│   ├── db/
│   │   ├── crud.py
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── middleware/
│   │   └── request_logging.py
│   │
│   ├── models/
│   │   └── api.py
│   │
│   ├── rag/
│   │   └── ...
│   │
│   └── voice/
│       └── audio.py
│
├── tests/
│   ├── test_voice_audio.py
│   ├── test_voice_api.py
│   └── ...
│
├── prompts/
│   └── ...
│
├── results/
│   └── ...
│
├── requirements.txt
├── genai.db
├── genai_day17_backup.db
└── README.md
```

### Day 17 Request Flow

```text
User
 │
 │ Audio file
 ▼
POST /voice/ask
 │
 ▼
Audio validation
 │
 ├── Invalid ──────────────► Safe error
 │
 ▼
Temporary audio file
 │
 ▼
STT
 │
 ├── Unsuccessful ─────────► Safe processing outcome
 │
 ▼
Transcript
 │
 ▼
Existing process_question()
 │
 ▼
RAG retrieval
 │
 ▼
Grounded generation
 │
 ▼
Sources / citations
 │
 ▼
VoiceAskResponse
 │
 ▼
User
```

### Observability Flow

```text
Request
  │
  ├── APIRequest
  │      └── Total latency
  │
  ├── STT RequestStage
  │      ├── status
  │      ├── latency_ms
  │      └── details
  │
  └── RAG RequestStage
         ├── status
         ├── latency_ms
         └── details
```

---

## 21. Day 17 Status

### ✅ Day 17: IMPLEMENTED AND TESTED

**Speech-to-text integration • Audio validation • Voice API endpoint • Existing RAG reuse • STT/RAG stage logging • Voice automated tests**

Verified automated evidence:

```text
Voice API tests:   8 passed
Voice audio tests: 6 passed
```

The Day 17 implementation successfully demonstrates the controlled voice-to-RAG workflow through automated validation.

Day 16 functionality remains available as the foundation for Day 17, while this README remains focused on the Day 17 speech-to-text and voice-to-RAG implementation.