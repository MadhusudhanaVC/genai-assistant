# Day 17: Integrate Speech-to-Text with the RAG API

**# GenAI Assistant**



A FastAPI-based Retrieval-Augmented Generation (RAG) assistant with input guardrails, grounded answer generation, request/stage logging, and voice-question support through speech-to-text.



**## Table of Contents**



1\. [Project Overview]\(#1-project-overview)

2\. [Day 17 Objective]\(#2-day-17-objective)

3\. [Day 16 Foundation]\(#3-day-16-foundation)

4\. [Day 17 Requirements]\(#4-day-17-requirements)

5\. [Day 17 Implementation]\(#5-day-17-implementation)

6\. [Audio Input Validation]\(#6-audio-input-validation)

7\. [Speech-to-Text Integration]\(#7-speech-to-text-integration)

8\. [Voice-to-RAG Flow]\(#8-voice-to-rag-flow)

9\. [Stage-Level Logging]\(#9-stage-level-logging)

10\. [Error Handling]\(#10-error-handling)

11\. [Database Changes]\(#11-database-changes)

12\. [API Endpoint]\(#12-api-endpoint)

13\. [Response Format]\(#13-response-format)

14\. [Implementation Files]\(#14-implementation-files)

15\. [Automated Test Evidence]\(#15-automated-test-evidence)

16\. [Voice Test Cases]\(#16-voice-test-cases)

17\. [Real Audio Validation]\(#17-real-audio-validation)

18\. [Evidence and Verification]\(#18-evidence-and-verification)

19\. [Completion Gate]\(#19-completion-gate)

20\. [Verification Commands]\(#20-verification-commands)

21\. [Project Structure and Flow]\(#21-project-structure-and-flow)

22\. [Day 17 Status]\(#22-day-17-status)



**---**



**## 1. Project Overview**



This project is a FastAPI-based GenAI assistant that uses a Retrieval-Augmented Generation pipeline to answer questions from available document evidence.



The application includes:



\- FastAPI API routes

\- RAG retrieval and grounded answer generation

\- Input validation and guardrails

\- Prompt-injection protection

\- Guardrail decision logging

\- Request and stage-level observability

\- Evidence and citation validation

\- Safe abstention for unsupported answers

\- Voice-question support through speech-to-text



Day 17 extends the existing text-based RAG API so a user can submit a short audio question and receive the same type of grounded RAG response produced by the existing \`/ask\` pipeline.



**---**



**## 2. Day 17 Objective**



**### Day 17: Integrate Speech-to-Text with the RAG API**



The objective of Day 17 is to accept a short audio question, transcribe it using a speech-to-text provider, and send the resulting transcript through the existing \`/ask\` RAG pipeline.



The implementation must not create a separate RAG implementation for voice input.



The intended flow is:



\`\`\`text

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

\`\`\`



The Day 17 implementation also records stage-level timing and failures so STT latency, RAG latency, and total request latency can be inspected separately.



**---**



**## 3. Day 16 Foundation**



Day 16 is retained only as the foundation for Day 17.



The existing application already provides:



\- Grounded response generation

\- Evidence validation

\- Citation validation

\- Safe abstention

\- Output validation

\- Input guardrails

\- Prompt-injection protection

\- Guardrail decision logging



Day 17 reuses this existing RAG and guardrail pipeline instead of duplicating it for voice requests.



The main Day 17 change is therefore the new audio-to-transcript path before the existing RAG flow.



**---**



**## 4. Day 17 Requirements**



The Day 17 implementation covers the following requirements.



**### Audio Input**



The API must:



\- Accept an audio upload.

\- Reject an empty audio file.

\- Reject unsupported audio formats.

\- Reject audio files larger than the configured size limit.

\- Accept the approved audio formats used by the application.



**### Speech-to-Text**



The STT layer must:



\- Send valid audio to the configured STT provider.

\- Capture the returned transcript.

\- Capture detected language when available.

\- Record STT latency.

\- Handle provider errors safely.

\- Identify provider failure categories.



**### RAG Integration**



The voice endpoint must:



\- Use the transcript as the RAG question.

\- Reuse the existing \`process_question()\` flow.

\- Avoid implementing a second RAG pipeline.

\- Return the grounded answer and normal RAG sources/citations.



**### Logging**



The request must provide stage-level evidence for:



\- Request ID

\- Audio metadata

\- STT latency

\- Transcript or approved transcript logging

\- RAG latency

\- Total request latency

\- Failed stage

\- STT failure reason when applicable



**---**



**## 5. Day 17 Implementation**



Day 17 adds a voice endpoint and STT integration while preserving the existing \`/ask\` behavior.



The main implementation consists of:



1\. Audio upload validation.

2\. Temporary audio-file handling.

3\. Speech-to-text transcription.

4\. Transcript validation.

5\. Reuse of the existing RAG question-processing function.

6\. STT stage logging.

7\. RAG stage logging.

8\. Total request logging through existing middleware.

9\. Structured STT error handling.

10\. Automated voice tests.



The implementation uses OpenRouter for the STT request with the \`openai/whisper-large-v3-turbo\` model.



**---**



**## 6. Audio Input Validation**



The audio layer is implemented in:



\`\`\`text

app/voice/audio.py

\`\`\`



The configured maximum audio size is:



\`\`\`text

10 MB

\`\`\`



Supported audio extensions are:



\`\`\`text

.wav

.mp3

.flac

.m4a

.ogg

.webm

.aac

\`\`\`



The validation flow rejects:



\- Missing audio files

\- Audio paths that are not files

\- Empty audio files

\- Audio files larger than 10 MB

\- Unsupported audio extensions



The API endpoint also validates:



\- Missing filename

\- Empty uploaded content

\- Unsupported content type

\- Excessive upload size

\- Unsupported filename extension



This provides validation both at the API upload boundary and inside the STT utility.



**---**



**## 7. Speech-to-Text Integration**



The STT implementation is located in:



\`\`\`text

app/voice/audio.py

\`\`\`



The configured provider endpoint is:



\`\`\`text

https\://openrouter.ai/api/v1/audio/transcriptions

\`\`\`



The configured STT model is:



\`\`\`text

openai/whisper-large-v3-turbo

\`\`\`



The audio bytes are Base64 encoded and sent through the provider request.



The returned STT result includes:



\`\`\`text

text

language

latency_ms

model

\`\`\`



The provider-detected language is preferred when available.



If the provider does not return a language, the requested language is used as the fallback when one was supplied.



STT provider failures are represented by:



\`\`\`text

STTProviderError

\`\`\`



Audio validation failures are represented by:



\`\`\`text

AudioValidationError

\`\`\`



**---**



**## 8. Voice-to-RAG Flow**



The voice endpoint is implemented in:



\`\`\`text

app/api/routes.py

\`\`\`



The flow is:



\`\`\`text

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

       ├── STT failure ───► Log STT FAILED

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

\`\`\`



The transcript is passed to the same question-processing path used by the normal text request.



This ensures voice input does not bypass the application's existing RAG, grounding, and output controls.



**---**



**## 9. Stage-Level Logging**



Day 17 extends the existing request-stage logging model.



Each stage can record:



\- Request ID

\- Stage name

\- Status

\- Latency

\- Details

\- Timestamp



The relevant stages are:



\`\`\`text

STT

RAG

\`\`\`



Typical successful evidence looks like:



\`\`\`text

STT | SUCCESS | 160 ms

RAG | SUCCESS | 60 ms

\`\`\`



The total request latency is recorded separately by the existing request middleware.



Example verified successful request:



\`\`\`text

STT latency:   160 ms

RAG latency:    60 ms

Total latency: 454 ms

Outcome:       SUCCESS

\`\`\`



The STT details can include:



\`\`\`text

filename

content_type

size_bytes

language

model

transcript

\`\`\`



For failures, the stage details include the relevant error type and reason code.



**---**



**## 10. Error Handling**



Day 17 provides structured error handling for common STT failures.



The STT provider error reason codes include:



\`\`\`text

STT_PROVIDER_ERROR

STT_CREDITS_REQUIRED

STT_AUTHENTICATION_ERROR

STT_RATE_LIMITED

STT_NETWORK_ERROR

STT_INVALID_RESPONSE

STT_EMPTY_TRANSCRIPT

STT_CONFIGURATION_ERROR

\`\`\`



Provider-specific API errors are mapped to structured API responses.



For example:



\`\`\`text

HTTP 402

→ STT_CREDITS_REQUIRED

\`\`\`



\`\`\`text

HTTP 401

→ STT_AUTHENTICATION_ERROR

\`\`\`



\`\`\`text

HTTP 429

→ STT_RATE_LIMITED

\`\`\`



Network failures are mapped to:



\`\`\`text

STT_NETWORK_ERROR

\`\`\`



The failed stage is also recorded in \`request_stages\`.



This allows a failed voice request to be distinguished from a RAG failure.



**---**



**## 11. Database Changes**



The \`RequestStage\` model was extended to support stage-level timing and details.



File:



\`\`\`text

app/db/models.py

\`\`\`



The relevant fields are:



\`\`\`text

id

request_id

stage

status

latency_ms

details

timestamp

\`\`\`



The stage logging helper was updated in:



\`\`\`text

app/db/crud.py

\`\`\`



The helper now accepts:



\`\`\`text

latency_ms

details

\`\`\`



The existing SQLite database was migrated to add:



\`\`\`text

latency_ms INTEGER

details TEXT

\`\`\`



A database backup was created before the schema change:



\`\`\`text

genai_day17_backup.db

\`\`\`



The backup is retained as a safety copy.



**---**



**## 12. API Endpoint**



Day 17 adds:



\`\`\`text

POST /voice/ask

\`\`\`



The endpoint accepts a multipart audio upload.



The existing endpoint remains available:



\`\`\`text

POST /ask

\`\`\`



The voice endpoint does not replace the text endpoint.



Instead, it provides an additional input path:



\`\`\`text

Text Question → /ask

Audio Question → /voice/ask → STT → existing RAG flow

\`\`\`



**---**



**## 13. Response Format**



The voice response model is defined in:



\`\`\`text

app/models/api.py

\`\`\`



The response contains:



\`\`\`text

answer

status

citations

sources

transcript

\`\`\`



Example structure:



\`\`\`json

{

  "answer": "Grounded answer generated from the retrieved evidence.",

  "status": "answered",

  "citations": [],

  "sources": [],

  "transcript": "Transcribed user question."

}

\`\`\`



The important Day 17 addition is the \`transcript\` field.



The answer itself continues to use the existing grounded RAG response structure.



**---**



**## 14. Implementation Files**



\| File | Purpose |

\|---|---|

\| \`app/voice/audio.py\` | Audio validation, STT provider integration, transcript handling, STT latency, and provider errors |

\| \`app/api/routes.py\` | \`/voice/ask\` endpoint and connection from transcript to existing RAG processing |

\| \`app/models/api.py\` | \`VoiceAskResponse\` response model |

\| \`app/api/errors.py\` | Structured STT provider error responses |

\| \`app/main.py\` | Registers the STT provider error handler |

\| \`app/db/models.py\` | Request-stage database fields for latency and details |

\| \`app/db/crud.py\` | Persists stage-level logs |

\| \`app/middleware/request_logging.py\` | Records request-level total latency and outcome |

\| \`tests/test_voice_audio.py\` | Unit tests for audio validation and STT behavior |

\| \`tests/test_voice_api.py\` | Voice API endpoint and error-path tests |

\| \`requirements.txt\` | Includes \`python-multipart\` and \`requests\` dependencies |



Existing RAG files are reused for the actual answer-generation path.



**---**



**## 15. Automated Test Evidence**



**### Voice API Test Suite**



The complete voice API test suite was executed:



\`\`\`text

tests/test_voice_api.py

\`\`\`



Verified result:



\`\`\`text

8 passed

\`\`\`



The tests covered:



\`\`\`text

voice request success

clear audio

background noise

domain terms

empty audio

unsupported audio type

audio size limit

STT provider failure

\`\`\`



**### Voice Audio Unit Tests**



The audio/STT unit test suite was executed:



\`\`\`text

tests/test_voice_audio.py

\`\`\`



Verified result:



\`\`\`text

6 passed

\`\`\`



The tests covered:



\`\`\`text

missing audio file

empty audio file

unsupported audio format

STT provider 402 error

audio file size limit

provider-detected language

\`\`\`



**### Python Syntax Verification**



The API routes file was also checked with:



\`\`\`text

python -m py_compile app\api\routes.py

\`\`\`



The syntax check passed.



**---**



**## 16. Voice Test Cases**



The Day 17 voice test coverage includes the required input categories.



\| Test Case | Expected Behavior |

\|---|---|

\| Clear audio | Transcribe and continue to RAG |

\| Mild background noise | Continue when transcription succeeds |

\| Domain terms | Preserve useful domain terminology in transcript |

\| Empty audio | Reject safely |

\| Unsupported format/type | Reject safely |

\| Excessive audio size | Reject safely |

\| STT provider failure | Return structured STT error |

\| Provider-detected language | Preserve detected language |



A successful mocked/domain test produced the following evidence:



\`\`\`text

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

\`\`\`



**---**



**## 17. Real Audio Validation**



A real Windows Sound Recorder file was prepared for Day 17 validation:



```text

day17_clear_question.wav.m4a

```



The file size was:



```text

158,762 bytes

```



The `.m4a` format is supported by the Day 17 audio validation layer.



The audio file is included as the real-world validation sample for the Day 17 voice workflow.



The automated test suite provides the controlled validation evidence for audio validation, speech-to-text handling, voice API processing, stage-level logging, and integration with the existing RAG pipeline.



**---**



**## 18. Evidence and Verification**



**### Successful Voice Pipeline Evidence**



A successful test request produced:



\`\`\`text

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



Source count:

1



Total request:

SUCCESS

Latency: 454 ms

\`\`\`



This verifies that the transcript can enter the existing RAG pipeline and that STT and RAG timings are recorded separately.



**### Failed STT Evidence**



A provider failure produced:



\`\`\`text

Stage:

STT



Status:

FAILED



Reason:

STT_CREDITS_REQUIRED



Status code:

402

\`\`\`



The failed stage was persisted in the request-stage log.



The measured latency is allowed to be \`0 ms\` for an immediate mocked failure.



**---**



**## 19. Completion Gate**



| Completion Gate | Evidence | Status |

|---|---|---|

| Valid audio can enter the voice API | Voice API tests | Verified |

| Empty audio is rejected safely | Voice API and audio unit tests | Verified |

| Unsupported audio is rejected safely | Voice API and audio unit tests | Verified |

| Excessive audio is rejected safely | Voice API and audio unit tests | Verified |

| STT integration is implemented | `app/voice/audio.py` | Verified |

| Transcript is passed to existing RAG | Successful voice API test | Verified |

| STT latency is recorded | Request-stage evidence | Verified |

| RAG latency is recorded | Request-stage evidence | Verified |

| Total request latency is recorded | Request middleware evidence | Verified |

| Failed stage is identifiable | Request-stage evidence | Verified |

| Voice API tests pass | 8 passed | Verified |

| STT unit tests pass | 6 passed | Verified |



### Completion Assessment



The Day 17 implementation and automated validation requirements are in place.



The voice workflow accepts validated audio, processes the transcript through the existing RAG pipeline, records stage-level timing, and provides the required automated test coverage.



**## 20. Verification Commands**



Run these commands from the project root with the project virtual environment activated.



**### Verify Voice Audio Tests**



\`\`\`cmd

python -m pytest tests\test_voice_audio.py -v

\`\`\`



Expected result:



\`\`\`text

6 passed

\`\`\`



**### Verify Voice API Tests**



\`\`\`cmd

python -m pytest tests\test_voice_api.py -v

\`\`\`



Expected result:



\`\`\`text

8 passed

\`\`\`



**### Verify STT Provider Failure Test**



\`\`\`cmd

python -m pytest tests\test_voice_api.py -k "stt_provider_failure" -v

\`\`\`



Expected result:



\`\`\`text

1 passed

\`\`\`



**### Verify API Route Syntax**



\`\`\`cmd

python -m py_compile app\api\routes.py

\`\`\`



Expected result:



\`\`\`text

No output means the syntax check passed.

\`\`\`



**---**



**## 21. Project Structure and Flow**



**### Relevant Project Structure**



\`\`\`text

genai-assistant/

│

├── app/

│   ├── api/

│   │   ├── errors.py

│   │   └── routes.py

│   │

│   ├── db/

│   │   ├── crud.py

│   │   ├── database.py

│   │   └── models.py

│   │

│   ├── middleware/

│   │   └── request_logging.py

│   │

│   ├── models/

│   │   └── api.py

│   │

│   ├── rag/

│   │   └── ...

│   │

│   └── voice/

│       └── audio.py

│

├── tests/

│   ├── test_voice_audio.py

│   ├── test_voice_api.py

│   └── ...

│

├── prompts/

│   └── ...

│

├── results/

│   └── ...

│

├── requirements.txt

├── genai.db

├── genai_day17_backup.db

└── README.md

\`\`\`



**### Day 17 Request Flow**



\`\`\`text

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

 ├── Failed ───────────────► STT FAILED + structured error

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

\`\`\`



**### Observability Flow**



\`\`\`text

Request

  │

  ├── APIRequest

  │      └── Total latency

  │

  ├── STT RequestStage

  │      ├── status

  │      ├── latency_ms

  │      └── details

  │

  └── RAG RequestStage

         ├── status

         ├── latency_ms

         └── details

\`\`\`



**---**



**## 22. Day 17 Status**



**### Day 17: IMPLEMENTED AND TESTED**



Speech-to-text integration • Audio validation • Voice API endpoint • Existing RAG reuse • STT/RAG stage logging • Voice automated tests



Verified automated evidence:



```text

Voice API tests: 8 passed

Voice audio tests: 6 passed

```



The Day 17 implementation successfully demonstrates the controlled voice-to-RAG workflow through automated validation.



Day 16 functionality remains available as the foundation for Day 17, while this README remains focused on the Day 17 speech-to-text and voice-to-RAG implementation.



---





