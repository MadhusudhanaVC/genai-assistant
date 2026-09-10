# GenAI Assistant

A production-oriented Generative AI assistant built with Python, FastAPI, RAG, vector search, reranking, citations, and database-backed document processing.

The project is developed incrementally through a 20-Day GenAI Engineering Roadmap, with each day adding a specific engineering capability.

---

## Project Status

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
| Day 11 | FastAPI service contracts and endpoints | ✅ Completed |

---

# Features

- Document ingestion
- Text chunking
- Embedding generation
- Vector search
- Query rewriting
- Cross-encoder reranking
- Grounded answer generation
- Citation generation and validation
- Metadata-aware retrieval
- Database persistence
- Processing event logging
- FastAPI REST API
- Pydantic request and response validation
- OpenAPI / Swagger documentation
- API endpoint testing
- Safety and response validation
- Voice processing support

---

# Architecture

The current RAG pipeline follows this flow:

```text
User Question
      ↓
Query Rewrite
      ↓
Top-5 Vector Retrieval
      ↓
Cross-Encoder Reranking
      ↓
Final Top-3 Results
      ↓
Grounded Context
      ↓
LLM Answer Generation
      ↓
Citation Validation
      ↓
API Response
```

Document ingestion follows:

```text
Documents
    ↓
Document Loading
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Store
    ↓
Database Metadata
```

The FastAPI layer exposes the existing pipeline without duplicating the RAG logic:

```text
FastAPI
   │
   ├── /health
   │
   ├── /ingest
   │       ↓
   │   ingest_documents()
   │
   ├── /ask
   │       ↓
   │   generate_grounded_answer()
   │
   └── /documents/{id}
           ↓
       get_document()
```

---

# Day 10 — Advanced Retrieval

## Objective

Improve retrieval quality by combining query rewriting, vector retrieval, and cross-encoder reranking.

The Day 10 work focused on improving the Day 9 retrieval baseline using controlled retrieval experiments. The goal was to identify and integrate configuration changes that provide measurable improvement without causing regressions.

The selected pipeline is:

```text
Query Rewrite
→ Top-5 Vector Retrieval
→ Cross-Encoder Reranking
→ Final Top-3
→ Grounded Context
→ LLM
→ Citation Validation
```

---

## Day 9 Frozen Baseline

### Baseline Configuration

| Setting | Value |
|---|---|
| Embedding model | all-MiniLM-L6-v2 |
| Normalization | true |
| Embedding dimension | 384 |
| Chunk size | 500 |
| Chunk overlap | 80 |
| Initial retrieval top-k | 3 |
| Minimum score | null |
| Metadata filter | null |
| Vector collection | day6_chunks |
| Evaluation dataset | datasets/day6_retrieval_test_cases.json |

### Baseline Metrics

| Metric | Value |
|---|---:|
| Hit@1 | 0.90 |
| Hit@3 | 1.00 |
| MRR | 0.95 |

The weak case was Q10, where the expected document was ranked second.

---

## Day 10 Implementation

### 1. Query Rewriting

A deterministic query-rewriting layer was added to convert selected questions into clearer, retrieval-oriented queries.

**File:**

```text
app/rag/query_rewriter.py
```

### Examples

```text
What is a Python variable?
→ What is a Python variable and what does it store?
```

```text
What is a Python module?
→ What is a Python module and how is it used to organize Python code?
```

```text
What is a Git branch?
→ What is a Git branch and how is it used for separate lines of development?
```

**Evaluation Result:** Aggregate metrics remained unchanged.

**Decision:** Retained as a supporting component, but not selected as the primary improvement.

---

### 2. Chunk Size Experiment

The chunk size was reduced from 500 to 400 tokens while maintaining an 80-token overlap in a separate vector store.

### Results

| Metric | Value |
|---|---:|
| Hit@1 | 0.90 |
| Hit@3 | 1.00 |
| MRR | 0.95 |

**Finding:** The Q10 expected document remained at rank 2. No measurable improvement was observed.

**Decision:** Rejected for the final configuration.

**Result file:**

```text
results/day10_experiments/chunk400_results.json
```

---

### 3. Top-k Experiment

The initial retrieval candidate count was increased from 3 to 5 to provide more context diversity.

**Finding:** Additional candidates did not improve the ranking of the weak Q10 case by themselves.

**Decision:** Not selected as a standalone improvement, but proved useful as part of the reranking pipeline.

---

### 4. Cross-Encoder Reranking

A cross-encoder reranker was implemented to improve document ranking.

**File:**

```text
app/rag/reranker.py
```

**Model:**

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Retrieval Flow

```text
User Question
    ↓
Query Rewriting
    ↓
Vector Retrieval (Top 5)
    ↓
Cross-Encoder Reranking
    ↓
Final Top 3 Results
    ↓
Grounded Generation
```

The reranker preserves retrieval information including:

- Original rank
- Original vector score
- Rerank score
- Final rank

**Decision:** Selected as the primary improvement driver.

---

## Final Day 10 Configuration

| Parameter | Value |
|---|---|
| Query rewriting | enabled |
| Initial retrieval top-k | 5 |
| Final top-k | 3 |
| Chunk size | 500 |
| Chunk overlap | 80 |
| Minimum score | null |
| Metadata filter | null |
| Embedding model | all-MiniLM-L6-v2 |
| Reranker model | cross-encoder/ms-marco-MiniLM-L-6-v2 |

The final generation flow is implemented through:

```text
app/rag/generate.py
```

---

## Retrieval Configuration

The final retrieval flow uses:

- Query rewriting before retrieval
- Top-5 vector retrieval
- Cross-encoder reranking
- Final Top-3 context
- Grounded answer generation
- Citation validation

This provides a two-stage retrieval strategy:

```text
Stage 1:
Vector Search
    ↓
Candidate Documents

Stage 2:
Cross-Encoder Reranking
    ↓
Best Relevant Documents
```

---

## Evaluation Results

The advanced retrieval pipeline improved the measured retrieval metrics.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Hit@1 | 0.90 | 1.00 | +0.10 |
| Hit@3 | 1.00 | 1.00 | 0.00 |
| MRR | 0.95 | 1.00 | +0.05 |

The improvement came primarily from reranking the initial vector-search candidates before selecting the final context.

---

## Q10 Ranking Improvement

For the Q10 evaluation query:

```text
Expected document: DOC019
```

### Baseline Ranking

```text
DOC020 → rank 1
DOC019 → rank 2
DOC029 → rank 3

Reciprocal rank: 0.50
```

### Final Reranked Result

```text
DOC019 → rank 1
DOC020 → rank 2
DOC029 → rank 3

Reciprocal rank: 1.00
```

### Improvement

```text
Hit@1: false → true
Rank: 2 → 1
RR: 0.50 → 1.00
```

This demonstrates the purpose of the reranking stage: vector search produces a candidate set, while the cross-encoder improves the ordering of those candidates.

---

## Performance Metrics

### Latency Measurement

| Component | Average Latency |
|---|---:|
| Retrieval | 2904.11 ms |
| Reranking | 1411.33 ms |
| **Total** | **4315.45 ms** |

The reranker provides measurable retrieval-quality improvement at the cost of additional inference latency and model complexity.

---

## Regression Check

The advanced retrieval changes were checked against the existing evaluation suite to ensure that retrieval improvements did not introduce regressions.

Final evaluation results:

```text
Hit@1: 1.00
Hit@3: 1.00
MRR:   1.00
```

No regressions were detected across the evaluated dataset.

---

## Experiment Summary

| Experiment | Change | Result | Decision |
|---|---|---|---|
| Query rewriting | Rewrite selected queries | Aggregate metrics unchanged | Retained as supporting component |
| Chunk size | 500 → 400 | Metrics unchanged | Rejected |
| Top-k | 3 → 5 | No direct ranking improvement | Not selected alone |
| Cross-encoder reranking | Rerank initial Top-5 | Hit@1: 0.90 → 1.00; MRR: 0.95 → 1.00 | Selected |

---

## Why Reranking Was Selected

Reranking was selected because it produced the clearest measurable improvement on the retrieval evaluation.

The final configuration improved:

- Hit@1: `0.90 → 1.00`
- MRR: `0.95 → 1.00`
- Q10 expected-document rank: `2 → 1`

Hit@3 remained unchanged at `1.00`.

The trade-off is additional inference latency:

```text
Retrieval: 2904.11 ms
Reranking: 1411.33 ms
Total:     4315.45 ms
```

Despite the additional latency and model complexity, reranking was selected because retrieval quality improved and no regression was detected across the evaluation set.

---

# Day 11 — FastAPI Service

## Objective

Expose document ingestion and question answering through a maintainable API with validated request and response models.

Day 11 focuses on creating service contracts around the existing RAG and database layers.

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health status |
| POST | `/ingest` | Run document ingestion |
| POST | `/ask` | Ask a question using the RAG pipeline |
| GET | `/documents/{document_id}` | Retrieve document metadata |

---

## `GET /health`

Returns a simple service health response.

### Example

```json
{
  "status": "healthy"
}
```

The endpoint does not expose API keys, secrets, or internal exception details.

---

## `POST /ingest`

Runs the existing document ingestion flow.

The endpoint delegates to:

```python
ingest_documents()
```

### Example Response

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

The API exposes the ingestion result without duplicating the ingestion logic inside the route.

---

## `POST /ask`

Accepts a validated question and optional retrieval parameters.

### Request

```json
{
  "question": "What is Python?",
  "top_k": 3,
  "min_score": null
}
```

### Validation

The request model validates:

- `question` must contain at least one character
- `top_k` must be at least `1`
- `min_score`, when supplied, must be between `0` and `1`

### Example Response

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
      "text": "...",
      "score": 0.7085,
      "document_id": "DOC001",
      "title": "Python Basics",
      "source_path": "sample_data\\day5_documents\\DOC001_python_basics.md",
      "updated_at": "2026-08-10",
      "chunk_index": 0,
      "category": "python"
    }
  ]
}
```

The endpoint calls the existing:

```python
generate_grounded_answer()
```

function instead of implementing another RAG pipeline.

---

## `GET /documents/{document_id}`

Returns stored document metadata and processing status.

### Example

```text
GET /documents/DOC001
```

### Example Response

```json
{
  "document_id": "DOC001",
  "title": "Python Basics",
  "content": "Python is a general-purpose programming language.",
  "source_path": "sample_data/DOC001_python_basics.md",
  "updated_at": "2026-08-10",
  "status": "completed"
}
```

If the requested document does not exist:

```json
{
  "detail": "Document not found"
}
```

The endpoint returns HTTP `404`.

---

# API Request and Response Models

Day 11 introduces dedicated Pydantic models in:

```text
app/models/api.py
```

The main models are:

```text
AskRequest
AskResponse
IngestResponse
DocumentResponse
```

These models provide explicit API contracts and allow FastAPI to automatically generate the corresponding OpenAPI schemas.

---

# Database Dependency Injection

The document endpoint uses FastAPI dependency injection for database sessions.

The route receives a database session through:

```python
db: Session = Depends(get_db)
```

The database dependency creates a session for the request and closes it after the request completes.

Document lookup is handled through the existing CRUD layer:

```python
get_document(db=db, document_id=document_id)
```

This keeps database logic outside the API route.

---

# Project Structure

```text
genai-assistant/
│
├── app/
│   ├── api/
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
├── sample_data/
│
├── tests/
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

---

# Configuration

Application configuration is centralized in:

```text
app/core/config.py
```

The project uses environment variables for configuration values such as:

```env
APP_NAME=GenAI Assistant
APP_ENV=development
DEBUG=True

DATABASE_URL=sqlite:///genai.db

LOG_LEVEL=INFO

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=nex-agi/nex-n2.5-mini:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

Real secrets should be stored only in `.env`.

The `.env` file must not be committed to Git.

Only `.env.example` should be committed.

---

---

# Git Ignore

Generated ChromaDB data should not be committed to Git.

The following paths should be ignored:

```text
results/chroma_db/
results/chroma_db_day10_chunk400/


# Running the Application

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### OpenAPI Schema

```text
http://127.0.0.1:8000/openapi.json
```

The OpenAPI schema was verified to contain:

```text
GET  /health
POST /ingest
POST /ask
GET  /documents/{document_id}
```

---

# Testing

The project uses `pytest` for automated testing.

Run the complete test suite:

```bash
pytest
```

Final Day 11 verification:

```text
26 passed in 856.02s (0:14:16)
```

The API-specific tests cover:

- Health endpoint
- Empty question validation
- Invalid `top_k`
- Invalid `min_score`
- Unknown document handling
- Successful `/ask`
- Successful `/ingest`
- Successful document lookup

---

# API Validation Verification

Invalid requests are rejected by FastAPI/Pydantic validation.

## Empty Question

```json
{
  "question": "",
  "top_k": 3,
  "min_score": null
}
```

Expected response:

```text
422 Unprocessable Entity
```

## Invalid `top_k`

```json
{
  "question": "What is Python?",
  "top_k": 0,
  "min_score": null
}
```

Expected response:

```text
422 Unprocessable Entity
```

## Invalid `min_score`

```json
{
  "question": "What is Python?",
  "top_k": 3,
  "min_score": 2
}
```

Expected response:

```text
422 Unprocessable Entity
```

---

# Manual Endpoint Verification

The following endpoints were manually verified using the running FastAPI application:

```text
GET  /health       → 200
POST /ingest       → 200
POST /ask          → 200
GET  /documents/{id}
```

Document behavior was also verified for both:

```text
GET /documents/doc-001 → 404
GET /documents/DOC001  → 200
```

This confirms that unknown document IDs are handled separately from valid stored documents.

---

# Engineering Principles

The project follows several engineering principles.

## Thin API Routes

API routes should coordinate existing application modules rather than duplicate business logic.

```text
Route
  ↓
Application/RAG function
  ↓
Existing implementation
```

## Explicit Contracts

Pydantic models define the expected request and response structures.

## Centralized Configuration

Configuration is accessed through the application settings rather than being hardcoded across modules.

## Database Separation

Database operations are kept in the database/CRUD layer instead of being embedded directly into business logic.

## Grounded Generation

The LLM receives retrieved context rather than relying only on its internal knowledge.

## Citation Validation

Generated answers are checked against the retrieved evidence and citation structure.

## Evaluation-Driven Retrieval

Retrieval changes are evaluated using measurable retrieval metrics before being selected.

---

# Day 10 Key Achievements

- Added query rewriting to the retrieval flow.
- Added cross-encoder reranking.
- Improved Hit@1 from `0.90` to `1.00`.
- Maintained Hit@3 at `1.00`.
- Improved MRR from `0.95` to `1.00`.
- Improved Q10 relevant-document rank from `2` to `1`.
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
- Added Pydantic API request/response models.
- Added database dependency injection.
- Added document lookup through the CRUD layer.
- Added API validation tests.
- Verified Swagger/OpenAPI documentation.
- Verified all four endpoints manually.
- Completed the full automated test suite with 26 passing tests.

---

# Current RAG Pipeline

The current end-to-end question-answering flow is:

```text
User
  ↓
FastAPI /ask
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
AskResponse
  ↓
User
```

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

The goal is to ensure that each roadmap milestone is supported by working code, tests/evaluation evidence, documentation, and a reviewed Git change.

---

# Day 11 Completion Status

Day 11 is complete.

The service now exposes:

```text
GET  /health
POST /ingest
POST /ask
GET  /documents/{document_id}
```

Validation, database integration, OpenAPI generation, manual endpoint verification, and automated testing have been completed.

Final automated test result:

```text
26 passed in 856.02s (0:14:16)
```

---

# Next Step

The next roadmap milestone after Day 11 is Day 12.

Day 12 continues the service-layer work with the next set of API/database engineering requirements defined by the roadmap.

---

# License

This project is intended for learning and engineering practice as part of the GenAI Engineering Roadmap.