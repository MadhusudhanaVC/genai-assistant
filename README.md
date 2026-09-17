# GenAI Assistant

A Retrieval-Augmented Generation (RAG) assistant built with Python.

The project demonstrates document ingestion, chunking, embeddings, vector retrieval, query rewriting, cross-encoder reranking, grounded answer generation, citation validation, database integration, FastAPI service contracts, SQL observability, structured error handling, and API testing.

---

## Features

- Document ingestion and processing
- Text chunking
- Sentence-transformer embeddings
- ChromaDB vector search
- Query rewriting
- Cross-encoder reranking
- Grounded answer generation
- Citation validation
- SQLAlchemy database integration
- FastAPI REST API
- Pydantic request and response validation
- Swagger / OpenAPI documentation
- Retrieval evaluation and regression testing
- SQL request observability
- Request ID tracking
- Request stage logging
- Source and retrieval score logging
- Centralized API error handling
- Provider error handling

---

## RAG Pipeline

```text
Question
   ↓
Query Rewriting
   ↓
Vector Retrieval — Top 5
   ↓
Cross-Encoder Reranking
   ↓
Final Top 3
   ↓
Grounded Context
   ↓
LLM Answer
   ↓
Citation Validation
```

---

# Day 10 — Advanced Retrieval

Day 10 focused on improving retrieval quality through controlled experiments.

## Final Configuration

| Parameter | Value |
|---|---|
| Query rewriting | Enabled |
| Initial retrieval | Top 5 |
| Final results | Top 3 |
| Chunk size | 500 |
| Chunk overlap | 80 |
| Embedding model | `all-MiniLM-L6-v2` |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |

## Results

| Metric | Day 9 | Day 10 |
|---|---:|---:|
| Hit@1 | 0.90 | 1.00 |
| Hit@3 | 1.00 | 1.00 |
| MRR | 0.95 | 1.00 |

The main improvement came from cross-encoder reranking.

## Q10 Improvement

```text
Before:
DOC019 → Rank 2

After:
DOC019 → Rank 1
```

No regressions were detected during evaluation.

---

# Day 11 — FastAPI Service

Day 11 exposes the existing RAG pipeline through a FastAPI service with validated request and response models.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check service health |
| POST | `/ingest` | Ingest documents |
| POST | `/ask` | Ask a question using the RAG pipeline |
| GET | `/documents/{document_id}` | Retrieve document metadata and content |

## Run the API

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

---

## API Examples

### Health

```text
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

### Ask

```text
POST /ask
```

Request:

```json
{
  "question": "What is Python?",
  "top_k": 3,
  "min_score": null
}
```

Response:

```json
{
  "answer": "Python is a general-purpose programming language commonly used for automation, web applications, data processing, and scripting.",
  "status": "answered",
  "citations": [
    "[DOC001 | DOC001_CHUNK_001]"
  ],
  "sources": [
    {
      "chunk_id": "DOC001_CHUNK_001",
      "document_id": "DOC001",
      "title": "Python Basics"
    }
  ]
}
```

### Ingest

```text
POST /ingest
```

Example response:

```json
{
  "processed_documents": 30,
  "completed_documents": 30,
  "failed_documents": 0,
  "chunks": 47,
  "indexed_chunks": 47,
  "status": "completed"
}
```

### Get Document

```text
GET /documents/DOC001
```

Example response:

```json
{
  "document_id": "DOC001",
  "title": "Python Basics",
  "content": "...",
  "source_path": "...",
  "updated_at": "2026-08-10",
  "status": "completed"
}
```

Unknown documents return:

```text
404 Not Found
```

---

## API Validation

The API uses Pydantic models for request and response validation.

### `AskRequest`

| Field | Constraint |
|---|---|
| `question` | Required, minimum length: 1 |
| `top_k` | Default: 3, minimum: 1 |
| `min_score` | Optional, range: 0 to 1 |

### Validation Behavior

| Input | Response |
|---|---:|
| Empty question | 422 |
| `top_k = 0` | 422 |
| `min_score = 2` | 422 |
| Valid request | 200 |

---

## Day 11 Testing

The Day 11 API tests covered:

- Health endpoint
- `/ask` request validation
- `/ask` successful response
- `/ingest` successful response
- Document not-found handling
- Document retrieval response

At the Day 11 checkpoint, the full project test suite contained:

```text
26 tests passed
```

After the Day 12 changes, the complete regression suite was expanded and verified with:

```text
28 tests passed
```

---

# Day 12 — Observability and Error Handling

Day 12 focuses on making the FastAPI service observable, diagnosable, and safer to operate while preserving the existing RAG architecture.

---

## SQL Observability

The service records request-level information in three database tables:

| Table | Purpose |
|---|---|
| `api_requests` | Request ID, endpoint, timing, model version, prompt version, outcome, and error category |
| `request_sources` | Retrieved source/chunk IDs and retrieval scores |
| `request_stages` | Major processing stages and their status |

---

## Request Metadata

Each request records:

- Request ID
- Endpoint
- Start time
- Total latency in milliseconds
- Model version
- Prompt version
- Outcome
- Error category

Request IDs are accepted from the `X-Request-ID` request header when supplied. Otherwise, the application generates a UUID.

The request ID is returned through the `X-Request-ID` response header and is also included in structured error responses.

---

## Request Outcomes

Requests can be recorded with the following outcomes:

```text
IN_PROGRESS
SUCCESS
ERROR
```

Error categories include:

```text
PROVIDER_ERROR
INTERNAL_ERROR
```

---

## Stage Logging

The `/ask` RAG pipeline records major stages:

```text
RETRIEVAL
    ↓
GENERATION
```

Each stage can be recorded as:

```text
STARTED
SUCCESS
FAILED
```

A successful request is recorded as:

```text
RETRIEVAL  → STARTED
RETRIEVAL  → SUCCESS
GENERATION → STARTED
GENERATION → SUCCESS
```

A generation failure is recorded as:

```text
RETRIEVAL  → STARTED
RETRIEVAL  → SUCCESS
GENERATION → STARTED
GENERATION → FAILED
```

Stage logging is connected to the existing RAG pipeline through a stage logging callback.

---

## Source Logging

Retrieved source IDs and retrieval scores are stored in `request_sources`.

Example:

```text
DOC019_CHUNK_001 → 0.6434
DOC029_CHUNK_001 → 0.5342
DOC019_CHUNK_002 → 0.5945
```

The request observability records store source identifiers and scores rather than unnecessarily storing full generated responses or other restricted request data.

---

## Consistent Error Responses

Centralized error handlers provide stable error codes and safe client-facing messages.

| Error | HTTP Status | Error Code |
|---|---:|---|
| Invalid request | 422 | `VALIDATION_ERROR` |
| Document not found | 404 | `DOCUMENT_NOT_FOUND` |
| LLM provider failure | 502 | `PROVIDER_ERROR` |
| Unexpected application failure | 500 | `INTERNAL_ERROR` |

### Validation Error

Example:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "The request data is invalid.",
  "request_id": "..."
}
```

### Document Not Found

Example:

```json
{
  "error_code": "DOCUMENT_NOT_FOUND",
  "message": "The requested document was not found.",
  "request_id": "..."
}
```

### Provider Error

Example:

```json
{
  "error_code": "PROVIDER_ERROR",
  "message": "The language model provider could not complete the request.",
  "request_id": "..."
}
```

### Internal Error

Unexpected application failures return:

```text
500 Internal Server Error
```

with the stable:

```text
INTERNAL_ERROR
```

error code and a safe client-facing message.

Provider-specific details and internal stack traces are not returned to API clients.

---

## LLM Provider Handling

The LLM client uses a dedicated `ProviderError` exception for provider failures and invalid provider responses.

The client handles cases such as:

- Provider request failure
- Provider returning no choices
- Provider returning an empty response

The provider response is checked before the application attempts to access the generated message.

This prevents unexpected provider responses from producing unhandled application errors.

---

## Blocking / Async Review

Synchronous database logging inside the asynchronous request middleware is executed through:

```python
run_in_threadpool()
```

This ensures blocking SQL operations are not performed directly on the asynchronous event loop.

The synchronous FastAPI routes continue to use the existing RAG, database, document, and LLM operations without duplicating application logic.

---

# Day 12 API Tests

The Day 12 API test suite covers:

- Health endpoint
- Empty question validation
- Invalid `top_k`
- Invalid `min_score`
- Unknown document handling
- Successful `/ask`
- Missing evidence handling
- Provider failure handling
- Successful `/ingest`
- Successful document lookup

Run the API tests with:

```bash
pytest tests/test_api.py -v
```

Final result:

```text
10 tests passed
```

---

# Day 12 Regression Test

The complete project test suite was rerun after the Day 12 changes.

Run:

```bash
pytest -v
```

Final result:

```text
28 passed in 201.94s (0:03:21)
```

All existing tests passed after the Day 12 implementation.

---

# Manual Verification

The `/ask` endpoint was manually verified with a successful grounded response.

Example result:

```text
HTTP/1.1 200 OK
```

The response included:

- Grounded answer
- Citation
- Source metadata
- Retrieval scores
- `X-Request-ID` response header

Example request ID:

```text
b5fc92f9-6b75-448f-bee3-9cffb469a13b
```

The corresponding SQL observability record contained:

```text
Endpoint: /ask
Outcome: SUCCESS
Error category: None
```

Recorded stages:

```text
RETRIEVAL  → STARTED
RETRIEVAL  → SUCCESS
GENERATION → STARTED
GENERATION → SUCCESS
```

Retrieved sources and scores were also recorded in the `request_sources` table.

---

## Provider Failure Verification

A provider failure was manually tested.

The API correctly returned:

```text
HTTP/1.1 502 Bad Gateway
```

with:

```json
{
  "error_code": "PROVIDER_ERROR",
  "message": "The language model provider could not complete the request.",
  "request_id": "..."
}
```

The request ID was returned in both the response body and the `X-Request-ID` response header.

The corresponding request stages were recorded as:

```text
RETRIEVAL  → STARTED
RETRIEVAL  → SUCCESS
GENERATION → STARTED
GENERATION → FAILED
```

This confirms that provider failures are handled separately from normal successful requests.

---

# Day 10 Retrieval Evaluation

| Metric | Score |
|---|---:|
| Hit@1 | 1.00 |
| Hit@3 | 1.00 |
| MRR | 1.00 |

---

# Project Structure

```text
genai-assistant/
│
├── app/
│   ├── api/
│   │   ├── errors.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── crud.py
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── llm/
│   │   ├── client.py
│   │   └── validator.py
│   │
│   ├── middleware/
│   │   └── request_logging.py
│   │
│   ├── models/
│   │   ├── api.py
│   │   ├── document.py
│   │   └── prompt_outputs.py
│   │
│   ├── rag/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── generate.py
│   │   ├── ingest.py
│   │   ├── query_rewriter.py
│   │   ├── reranker.py
│   │   ├── retrieve.py
│   │   └── vector_store.py
│   │
│   └── main.py
│
├── datasets/
│   └── day6_retrieval_test_cases.json
│
├── prompts/
│   └── grounded_answer.txt
│
├── results/
│   ├── chunks.jsonl
│   ├── day9_baseline_metrics.json
│   ├── day10_query_rewrite_results.json
│   ├── day10_reranker_results.json
│   ├── day10_before_after_report.json
│   └── day10_experiments/
│
├── tests/
│   ├── test_api.py
│   ├── test_chunking.py
│   ├── test_cli_loader.py
│   ├── test_database.py
│   ├── test_document_validation.py
│   ├── test_grounded_generation.py
│   └── test_rag_pipeline.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── pyproject.toml
└── README.md
```

---

# Main Components

| Component | Location |
|---|---|
| FastAPI application | `app/main.py` |
| API routes | `app/api/routes.py` |
| API error handlers | `app/api/errors.py` |
| Request logging middleware | `app/middleware/request_logging.py` |
| API models | `app/models/api.py` |
| Configuration | `app/core/config.py` |
| Database | `app/db/` |
| LLM | `app/llm/` |
| RAG pipeline | `app/rag/` |
| Evaluation datasets | `datasets/` |
| Prompts | `prompts/` |
| Results | `results/` |
| Tests | `tests/` |

---

# Testing

The project includes tests for:

- Grounded answer generation
- Citation validation
- Grounded response validation
- Retrieval evaluation
- API request validation
- API endpoint behavior
- Database functionality
- Document validation
- Text chunking
- RAG pipeline behavior
- Provider failure handling
- Missing evidence handling
- Document not-found handling

---

# Configuration

The application uses environment variables for configuration.

Create a local `.env` file based on `.env.example`.

Example:

```env
APP_NAME=GenAI Assistant
APP_ENV=development
DEBUG=True

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_model
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

Never commit real API keys or other secrets to Git.

---

# Git Ignore

Generated local files and vector database files should not be committed.

Examples:

```text
.env
genai.db
results/chroma_db/
results/chroma_db_day10_chunk400/
```

---

# Project Status

| Day | Focus | Status |
|---|---|---|
| Day 1 | Project setup and configuration | ✅ Completed |
| Day 2 | Document processing | ✅ Completed |
| Day 3 | Embeddings and vector storage | ✅ Completed |
| Day 4 | Retrieval pipeline | ✅ Completed |
| Day 5 | RAG pipeline | ✅ Completed |
| Day 6 | Database and persistence | ✅ Completed |
| Day 7 | Safety and validation | ✅ Completed |
| Day 8 | Voice capability | ✅ Completed |
| Day 9 | Retrieval evaluation | ✅ Completed |
| Day 10 | Advanced retrieval and reranking | ✅ Completed |
| Day 11 | FastAPI service | ✅ Completed |
| Day 12 | Observability, error handling, and API tests | ✅ Completed |

---

# Day 10 Completion

Day 10 advanced retrieval improvements were implemented and evaluated.

Completed:

- Query rewriting
- Top-5 initial retrieval
- Cross-encoder reranking
- Final Top-3 selection
- Retrieval evaluation
- Regression testing
- Q10 ranking improvement

Final metrics:

```text
Hit@1: 1.00
Hit@3: 1.00
MRR:   1.00
```

---

# Day 11 Completion

Day 11 FastAPI service implementation is complete.

Completed:

- FastAPI application created
- `/health` endpoint implemented
- `/ingest` endpoint implemented
- `/ask` endpoint implemented
- `/documents/{document_id}` endpoint implemented
- Pydantic API models added
- Database dependency injection added
- Document lookup added to CRUD layer
- Swagger / OpenAPI documentation verified
- API validation tested

---

# Day 12 Completion

Day 12 SQL observability, structured error handling, blocking/async review, and API regression testing are complete.

Completed:

- SQL request logging added
- Request ID generation and propagation added
- Request latency tracking added
- Model and prompt version tracking added
- Request outcome and error category tracking added
- Retrieval source and score logging added
- Retrieval and generation stage logging added
- Centralized API error handlers added
- Provider error handling added
- Safe error response contracts added
- Blocking database logging moved through `run_in_threadpool()`
- API test suite updated and verified
- 10 API tests passed
- 28 full regression tests passed
- Manual `/ask` success verified
- Provider failure path verified
- SQL observability verified

---

# Quick Start

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Set up environment

Copy `.env.example` to `.env` and add your OpenRouter API key.

## 3. Run the API

```bash
uvicorn app.main:app --reload
```

## 4. Access Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

## 5. Run tests

```bash
pytest -q
```

---

# API Documentation

Once the application is running, the available API documentation can be accessed through:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### OpenAPI Schema

```text
http://127.0.0.1:8000/openapi.json
```

Available endpoints:

```text
GET  /health
POST /ingest
POST /ask
GET  /documents/{document_id}
```

---

# End-to-End Request Flow

The current end-to-end question-answering flow is:

```text
User
  ↓
FastAPI /ask
  ↓
Request ID Middleware
  ↓
AskRequest Validation
  ↓
Query Rewrite
  ↓
Vector Retrieval
  ↓
Top-5 Candidates
  ↓
Cross-Encoder Reranking
  ↓
Top-3 Results
  ↓
Grounded Context
  ↓
LLM Generation
  ↓
Citation Validation
  ↓
Source Logging
  ↓
AskResponse
  ↓
User
```

Request observability runs alongside the request:

```text
API Request
    │
    ├── Request ID
    ├── Endpoint
    ├── Start Time
    ├── Total Latency
    ├── Model Version
    ├── Prompt Version
    ├── Outcome
    ├── Error Category
    │
    ├── Request Stages
    │      ├── Retrieval
    │      └── Generation
    │
    └── Request Sources
           ├── Source ID
           └── Retrieval Score
```

---

# Engineering Principles

The project follows several engineering principles.

## Thin API Routes

API routes coordinate existing application modules rather than duplicating business logic.

```text
Route
  ↓
Application / RAG function
  ↓
Existing implementation
```

## Explicit Contracts

Pydantic models define the expected request and response structures.

## Centralized Configuration

Configuration is accessed through the application settings rather than being hardcoded across modules.

## Database Separation

Database operations are kept in the database / CRUD layer instead of being embedded directly into business logic.

## Grounded Generation

The LLM receives retrieved context rather than relying only on its internal knowledge.

## Citation Validation

Generated answers are checked against the retrieved evidence and citation structure.

## Evaluation-Driven Retrieval

Retrieval changes are evaluated using measurable retrieval metrics before being selected.

## Observable API Execution

API requests record request IDs, latency, model and prompt versions, outcomes, stages, and retrieved sources to support diagnosis and debugging.

## Safe Error Handling

External provider failures and unexpected internal failures are represented using stable error codes and safe client-facing messages.

---

# Day 10 Key Achievements

- Added query rewriting to the retrieval flow.
- Added cross-encoder reranking.
- Improved Hit@1 from `0.90` to `1.00`.
- Maintained Hit@3 at `1.00`.
- Improved MRR from `0.95` to `1.00`.
- Improved Q10 expected-document rank from `2` to `1`.
- Evaluated retrieval quality against the existing baseline.
- Measured the latency cost of reranking.
- Added regression verification.
- Selected a Top-5 retrieval → reranking → Top-3 final-context strategy.
- Documented rejected experiments and final configuration.

---

# Day 11 Key Achievements

- Added FastAPI application wiring.
- Added API route registration.
- Added `/health`.
- Added `/ingest`.
- Added `/ask`.
- Added `/documents/{document_id}`.
- Added Pydantic API request / response models.
- Added database dependency injection.
- Added document lookup through the CRUD layer.
- Added API validation tests.
- Verified Swagger / OpenAPI documentation.
- Verified API endpoints manually.
- Completed the Day 11 service implementation.

---

# Day 12 Key Achievements

- Added SQL request observability.
- Added request ID generation and propagation.
- Added request latency tracking.
- Added model and prompt version tracking.
- Added request outcome tracking.
- Added request error categories.
- Added retrieved source ID and score logging.
- Added retrieval stage logging.
- Added generation stage logging.
- Added centralized API error handling.
- Added stable error codes.
- Added safe error messages.
- Added dedicated provider error handling.
- Added provider response validation.
- Reviewed blocking database operations in asynchronous middleware.
- Added and updated API tests.
- Verified 10 API tests successfully.
- Verified the full suite with 28 passing tests.
- Manually verified successful `/ask` execution.
- Manually verified provider failure handling.
- Verified SQL request, stage, and source observability.

---

# Day 12 Verification Summary

## API Test Suite

```text
10 tests passed
```

## Full Regression Suite

```text
28 passed in 201.94s (0:03:21)
```

## Successful `/ask`

```text
HTTP/1.1 200 OK
```

Verified:

- Request ID
- Grounded answer
- Citation
- Retrieved sources
- Retrieval scores
- Request outcome
- Retrieval stages
- Generation stages

## Provider Failure

```text
HTTP/1.1 502 Bad Gateway
```

Verified:

- `PROVIDER_ERROR`
- Safe client-facing message
- Request ID
- Retrieval stage failure path
- Generation failure stage
- SQL error classification

---

# Development Workflow

Each roadmap day follows an incremental engineering workflow:

```text
Understand Requirement
        ↓
Implement
        ↓
Run Tests
        ↓
Evaluate
        ↓
Review Changes
        ↓
Document
        ↓
Commit
        ↓
Push
```

The goal is to ensure that each roadmap milestone is supported by working code, tests / evaluation evidence, documentation, and a reviewed Git change.

---

# Roadmap Progress

The project has completed:

```text
Day 1  → Project Setup
Day 2  → Document Processing
Day 3  → Embeddings and Vector Storage
Day 4  → Retrieval Pipeline
Day 5  → RAG Pipeline
Day 6  → Database and Persistence
Day 7  → Safety and Validation
Day 8  → Voice Capability
Day 9  → Retrieval Evaluation
Day 10 → Advanced Retrieval and Reranking
Day 11 → FastAPI Service
Day 12 → Observability, Error Handling and API Tests
```

---

# Next Steps

The next roadmap milestone is:

```text
Day 13
```

Planned areas include:

- Day 13 implementation
- Performance optimization
- Additional document type support
- Advanced query strategies
- Production deployment preparation
- Caching layer integration
