# GenAI Assistant

## Day 17: Integrate Speech-to-Text with the RAG API

A FastAPI-based Retrieval-Augmented Generation (RAG) assistant with input guardrails, grounded answer generation, request/stage logging, and voice-question support through local speech-to-text.

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
- Voice-question support through local speech-to-text

Day 17 extends the existing text-based RAG API so a user can submit a short audio question, transcribe it locally, and receive the same type of grounded RAG response produced by the existing `/ask` pipeline.

---

## 2. Day 17 Objective

**Integrate Speech-to-Text with the RAG API.**

The objective of Day 17 is to accept a short audio question, transcribe it using local speech-to-text, and send the resulting transcript through the existing `/ask` RAG pipeline.

> The implementation does **not** create a separate RAG implementation for voice input.

The intended flow is:

```text
Audio Question
      │
      ▼
Audio Validation
      │
      ▼
Local Speech-to-Text
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

Day 16 is retained as the foundation for Day 17.

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

- Process valid audio using the local speech-to-text implementation.
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
- Transcript
- RAG latency
- Total request latency
- Failed stage, when applicable

---

## 5. Day 17 Implementation

Day 17 adds a voice endpoint and local STT integration while preserving the existing `/ask` behavior.

The main implementation consists of:

1. Audio upload validation
2. Temporary audio-file handling
3. Local speech-to-text transcription
4. Transcript validation
5. Reuse of the existing RAG question-processing function
6. STT stage logging
7. RAG stage logging
8. Total request logging through existing request logging
9. Safe transcription handling
10. Automated voice tests

The local STT implementation uses:

```text
faster-whisper==1.2.1
```

The configured model and runtime settings are:

```text
Model:         small
Device:        cpu
Compute type:  int8
```

The Whisper model is loaded lazily and reused for subsequent transcription requests.

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

### Verified unsupported-file behavior

An unsupported audio file was tested through `/voice/ask` and was safely rejected:

```text
HTTP 400 Bad Request

{
  "error_code": "HTTP_ERROR",
  "message": "Unsupported audio format.",
  "request_id": "<request-id>"
}
```

The unsupported file is rejected before it reaches the transcription and RAG stages.

### Verified empty-file behavior

An empty audio file was tested and was safely rejected:

```text
HTTP 400 Bad Request

{
  "error_code": "HTTP_ERROR",
  "message": "Audio file is empty.",
  "request_id": "<request-id>"
}
```

### Verified excessive-size behavior

An audio file larger than the 10 MB limit was tested and was safely rejected:

```text
HTTP 400 Bad Request

{
  "error_code": "HTTP_ERROR",
  "message": "Audio file exceeds the 10 MB size limit.",
  "request_id": "<request-id>"
}
```

---

## 7. Speech-to-Text Integration

The STT implementation is located in:

```text
app/voice/audio.py
```

The implementation uses the local `faster-whisper` package rather than a remote STT API.

**STT package:**

```text
faster-whisper==1.2.1
```

**STT model:**

```text
small
```

**Runtime:**

```text
device=cpu
compute_type=int8
```

The local transcription function:

- Validates the audio path.
- Validates the file size.
- Validates the audio extension.
- Loads the local Whisper model when required.
- Transcribes the audio.
- Combines the returned segments into a transcript.
- Captures detected language when available.
- Measures STT latency.
- Returns the transcript, language, latency, and model information.

The returned STT result contains:

| Field | Description |
|---|---|
| `text` | The transcript |
| `language` | Detected or requested language |
| `latency_ms` | STT latency in milliseconds |
| `model` | STT model used |

### STT failure handling

Local transcription failures are converted into a controlled `STTProviderError` with a reason code.

Example logged failure:

```text
Stage: STT
Status: FAILED
Reason code: STT_LOCAL_ERROR
```

An empty transcription result is handled separately with:

```text
STT_EMPTY_TRANSCRIPT
```

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
       ├── Failure ───────► STT failure + stage log
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

The transcript is passed to the same question-processing path used by the normal text request. This ensures voice input does not bypass the application's existing RAG, grounding, guardrail, and output controls.

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

The total request latency is recorded separately by the existing request logging mechanism.

### Verified successful request

A real successful `/voice/ask` request was verified with:

```text
Request ID:
e1a1e90e-3e39-4b6b-b08d-c399c9c4d9a9

STT:
SUCCESS
Latency: 93448 ms

RAG:
SUCCESS
Latency: 73305 ms

Total request:
SUCCESS
Latency: 170689 ms
```

The corresponding `APIRequest` record contained:

```text
endpoint: /voice/ask
total_latency_ms: 170689
outcome: SUCCESS
error_category: None
```

This verifies that STT, RAG, and total request timing are available separately.

### STT failure logging

A failed STT request was also verified in the database:

```text
Stage: STT
Status: FAILED
Reason code: STT_LOCAL_ERROR
```

This confirms that the failed processing stage can be identified.

### STT details

Successful STT stage details can include:

```text
filename
content_type
size_bytes
language
model
transcript
```

---

## 10. Database Changes

The `RequestStage` model provides stage-level timing and details.

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

The stage logging helper is implemented in:

```text
app/db/crud.py
```

The existing request-level logging records total request latency through:

```text
app/middleware/request_logging.py
```

The Day 17 implementation therefore provides both stage-level and request-level observability.

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
| `app/voice/audio.py` | Audio validation, local speech-to-text, transcript handling, and STT latency |
| `app/api/routes.py` | `/voice/ask` endpoint and connection from transcript to existing RAG processing |
| `app/models/api.py` | Voice response model |
| `app/api/errors.py` | Structured API error responses for voice processing |
| `app/main.py` | Registers API error handlers |
| `app/db/models.py` | Request-stage database fields for latency and details |
| `app/db/crud.py` | Persists stage-level logs |
| `app/middleware/request_logging.py` | Records request-level total latency and outcome |
| `tests/test_voice_audio.py` | Unit tests for audio validation and STT behavior |
| `tests/test_voice_api.py` | Voice API endpoint and error-path tests |
| `requirements.txt` | Project dependencies including `faster-whisper` and `python-multipart` |

Existing RAG files are reused for the actual answer-generation path.

---

## 14. Automated Test Evidence

### Voice API Test Suite

File:

```text
tests/test_voice_api.py
```

Verified result:

```text
8 passed
```

The tests cover:

```text
voice request success
clear audio
background noise
domain terms
empty audio
unsupported audio type
audio size limit
local STT failure handling
```

### Voice Audio Unit Tests

File:

```text
tests/test_voice_audio.py
```

Verified result:

```text
8 passed
```

The tests cover:

```text
missing audio file
empty audio file
unsupported audio format
audio file size limit
local STT transcription
requested language handling
local STT failure
empty transcript
```

### Combined Voice Test Evidence

The voice audio and voice API test suites were also executed together:

```text
16 passed
```

This verifies the automated Day 17 voice test coverage.

### Python Syntax Verification

The API routes file was checked with:

```cmd
python -m py_compile app\api\routes.py
```

The syntax check passed.

---

## 15. Voice Test Cases

The Day 17 voice test coverage includes the required input categories.

| Test Case | Expected Behavior | Result |
|---|---|---|
| Clear audio | Transcribe and continue to RAG | ✅ Verified |
| Mild background noise | Continue when transcription succeeds | ✅ Verified |
| Domain terms | Preserve useful domain terminology in transcript | ✅ Verified |
| Empty audio | Reject safely | ✅ Verified |
| Unsupported format/type | Reject safely | ✅ Verified |
| Excessive audio size | Reject safely | ✅ Verified |
| Local STT failure | Identify STT failure safely | ✅ Verified |

### Real transcript examples

**Clear audio:**

```text
What is the main purpose of this gen AI assistant?
```

The local STT transcription was successful.

**Background noise:**

```text
What is cloud computing?
```

The transcript was successfully produced.

**Domain terms:**

```text
Explain retrieval augmented generation and vector embeddings.
```

The transcript preserved the domain terminology correctly.

---

## 16. Real Audio Validation

Real audio files were prepared for Day 17 validation, including:

```text
day17_clear_question.wav.m4a
day17_supported_question.m4a.m4a
day17_background_noise.m4a.m4a
day17_domain_terms.m4a.m4a
empty.wav
```

The clear audio question:

```text
What is the main purpose of this gen AI assistant?
```

was transcribed successfully by the local `faster-whisper` implementation.

The supported-question audio:

```text
What are some common applications of artificial intelligence?
```

produced the transcript:

```text
What are some common applications of artificial intelligence?
```

The corresponding voice request returned a grounded RAG answer with citation:

```text
[DOC019 | DOC019_CHUNK_001]
```

---

## 17. Evidence and Verification

### Voice vs Text Verification

The same question was tested through both the text and voice paths:

```text
Question:
What are some common applications of artificial intelligence?
```

The text request through:

```text
POST /ask
```

returned a grounded answer with:

```text
[DOC019 | DOC019_CHUNK_001]
```

The voice request through:

```text
POST /voice/ask
```

produced the same transcript and the same grounded citation:

```text
[DOC019 | DOC019_CHUNK_001]
```

This verifies that valid voice input reaches the same existing RAG processing path as equivalent text input.

### Successful Voice Pipeline Evidence

A successful real voice request produced:

```text
Request ID:
e1a1e90e-3e39-4b6b-b08d-c399c9c4d9a9

Endpoint:
/voice/ask

STT:
SUCCESS
Latency: 93448 ms

RAG:
SUCCESS
Latency: 73305 ms

Total request:
SUCCESS
Latency: 170689 ms

Outcome:
SUCCESS
```

### Unsupported Audio Evidence

An unsupported audio format was tested through the real API:

```text
HTTP 400 Bad Request

message:
Unsupported audio format.
```

### Empty Audio Evidence

An empty audio file was tested through the real API:

```text
HTTP 400 Bad Request

message:
Audio file is empty.
```

### Excessive Audio Evidence

An audio file larger than 10 MB was tested through the real API:

```text
HTTP 400 Bad Request

message:
Audio file exceeds the 10 MB size limit.
```

### Failed-Stage Evidence

A local STT failure was recorded as:

```text
Stage:
STT

Status:
FAILED

Reason code:
STT_LOCAL_ERROR
```

This confirms that failures identify the stage where processing stopped.

---

## 18. Completion Gate

| Completion Gate | Evidence | Status |
|---|---|---|
| Valid audio produces a grounded response | Real voice validation | ✅ Verified |
| Valid audio can enter the voice API | Voice API tests | ✅ Verified |
| Empty audio is rejected safely | Real API + automated tests | ✅ Verified |
| Unsupported audio is rejected safely | Real API + automated tests | ✅ Verified |
| Excessive audio is rejected safely | Real API + automated tests | ✅ Verified |
| STT integration is implemented | `app/voice/audio.py` | ✅ Verified |
| Transcript is passed to existing RAG | Voice vs text verification | ✅ Verified |
| STT latency is recorded | Request-stage evidence | ✅ Verified |
| RAG latency is recorded | Request-stage evidence | ✅ Verified |
| Total request latency is recorded | API request evidence | ✅ Verified |
| Failed stage is identifiable | STT failure stage log | ✅ Verified |
| Voice API tests pass | 8 passed | ✅ Verified |
| STT unit tests pass | 8 passed | ✅ Verified |
| Combined voice tests pass | 16 passed | ✅ Verified |

### Completion Assessment

The Day 17 implementation and automated validation requirements are complete.

The voice workflow accepts validated audio, performs local speech-to-text, sends the transcript through the existing RAG pipeline, records stage-level timing, identifies failed stages, and safely handles unsupported, empty, and oversized audio.

---

## 19. Verification Commands

### Verify Voice Audio Tests

```cmd
python -m pytest tests\test_voice_audio.py -v
```

Expected result:

```text
8 passed
```

### Verify Voice API Tests

```cmd
python -m pytest tests\test_voice_api.py -v
```

Expected result:

```text
8 passed
```

### Verify Both Voice Test Suites

```cmd
python -m pytest tests\test_voice_audio.py tests\test_voice_api.py -v
```

Expected result:

```text
16 passed
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
Local STT
 │
 ├── Failed ───────────────► STT failure + stage log
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

### ✅ Day 17: COMPLETE — IMPLEMENTED, TESTED, AND VERIFIED

**Speech-to-text integration • Audio validation • Unsupported-file handling • Empty-file handling • Size validation • Voice API endpoint • Existing RAG reuse • STT/RAG stage logging • Total latency logging • Failed-stage identification • Voice automated tests**

Verified automated evidence:

```text
Voice API tests:     8 passed
Voice audio tests:   8 passed
Combined voice:     16 passed
```

Verified real API behavior:

```text
Unsupported audio:   HTTP 400
Empty audio:         HTTP 400
Oversized audio:     HTTP 400
STT failure:         STT FAILED + reason code
Voice → RAG:         Verified
```

Verified successful request observability:

```text
STT latency:          93448 ms
RAG latency:          73305 ms
Total request:       170689 ms
Outcome:             SUCCESS
```

Day 16 functionality remains available as the foundation for Day 17, while this README focuses on the Day 17 speech-to-text and voice-to-RAG implementation.
