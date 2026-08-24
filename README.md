# GenAI Assistant

A modular Python-based **Generative AI Assistant** built as part of a structured **20-Day AI Engineering Roadmap**.

The project focuses on learning and implementing production-oriented AI engineering concepts such as structured outputs, prompt engineering, validation, testing, database integration, embeddings, vector databases, semantic search, and Retrieval-Augmented Generation (RAG).

The goal is to gradually evolve this project into a complete AI Assistant with Retrieval-Augmented Generation (RAG), vector databases, FastAPI services, voice capabilities, AI safety guardrails, and production deployment.

---

## 📋 Project Highlights

- Modular project architecture
- OpenRouter/OpenAI compatible LLM integration
- Structured prompt engineering
- Pydantic-based output validation
- SQLite database integration
- Prompt testing framework
- JSON schema validation
- Command Line Interface (CLI)
- Automated testing using Pytest
- Versioned prompt templates
- AI response latency tracking
- Document preprocessing and chunking
- Sentence Transformer embeddings
- `all-MiniLM-L6-v2` embedding model
- 384-dimensional embedding vectors
- ChromaDB vector database
- Semantic search
- Top-K retrieval
- Metadata filtering
- Minimum similarity score filtering
- Retrieval evaluation
- Retrieval result reporting

---

## 🚀 Features by Roadmap

### ✅ Day 1 – Project Foundation

- Python project structure
- Virtual environment setup
- Dependency management
- Git repository initialization
- Modular application architecture

---

### ✅ Day 2 – Data Validation & Storage

- JSON document validation using Pydantic
- CLI document loader
- SQLite database integration
- SQLAlchemy ORM
- Processing event logging
- Database viewer
- Automated testing using Pytest

---

### ✅ Day 3 – Prompt Playground

Implemented a reusable Prompt Playground capable of handling multiple business-oriented AI tasks.

**Features:**
- Shared OpenRouter/OpenAI client wrapper
- Model latency measurement
- Prompt templates stored separately
- Prompt placeholder replacement
- Reusable prompt execution pipeline

**Supported Tasks:**
- Text Summarization
- Information Extraction
- Text Classification

**Deliverables:**
- Prompt Playground
- Prompt Templates
- Sample Inputs
- Sample Outputs
- Shared LLM Client

---

### ✅ Day 4 – Structured Outputs & Prompt Testing

Implemented a production-style prompt evaluation framework.

**Features:**
- Structured outputs using Pydantic
- Response validation
- JSON parsing
- Prompt validation
- Prompt test dataset
- Prompt test runner
- Machine-readable JSON results
- Prompt version comparison
- Prompt reliability testing
- Validation error reporting

**Deliverables:**
- Pydantic Output Models
- Prompt Dataset
- Prompt Test Harness
- Prompt Comparison Report
- JSON Test Results

---

### ✅ Day 5 – Document Preprocessing & Chunking

Prepared documents for the Retrieval-Augmented Generation pipeline.

**Features:**
- Document preprocessing
- Front matter removal
- Text cleaning
- Markdown section handling
- Document chunking
- Chunk overlap
- Chunk metadata generation
- JSONL chunk dataset

**Results:**
- 30 documents processed
- 47 chunks generated
- Chunk metadata preserved
- Chunking output stored in `results/chunks.jsonl`

---

### ✅ Day 6 – Vector Indexing & Semantic Search

Implemented the first working vector retrieval pipeline.

**Features:**
- Sentence Transformer embeddings
- `all-MiniLM-L6-v2` embedding model
- 384-dimensional vectors
- Batch embedding generation
- Cached embedding model
- Same embedding model for documents and queries
- ChromaDB vector database
- Persistent vector collection
- Chunk text storage
- Metadata storage
- Content hash tracking
- Embedding model tracking
- Repeatable vector index creation
- Top-K semantic search
- Similarity scores
- Metadata filtering
- Minimum score threshold
- 10-question retrieval evaluation
- Retrieval result report

**Day 6 Dataset:**
- 15 selected documents
- 26 selected chunks
- 26 chunks successfully indexed

**Retrieval Evaluation:**
```
Total Questions: 10
Passed: 10
Failed: 0
Top-3 Retrieval Accuracy: 100%
```

**Day 6 Completion Gate:**
- [x] Embeddings generated successfully
- [x] Same embedding model used for documents and queries
- [x] 384-dimensional vectors verified
- [x] ChromaDB vector collection created
- [x] 26 chunks indexed
- [x] Chunk text and metadata stored
- [x] Top-K semantic search implemented
- [x] Similarity scores returned
- [x] Metadata filtering implemented
- [x] Minimum score threshold implemented
- [x] Retrieval test dataset created
- [x] 10 retrieval questions evaluated
- [x] Top-3 retrieval evaluation completed
- [x] 10/10 tests passed
- [x] Retrieval result report generated
- [x] Successful retrieval examples documented
- [x] Weak retrieval example documented

---

### ✅ Day 7 – Baseline RAG Ingestion & Retrieval

Connected document loading, chunking, embeddings, vector indexing, retrieval, and generation-ready context into one understandable RAG pipeline.

**Features:**
- Separate RAG ingestion module
- Separate retrieval module
- Generation-ready context preparation
- Document ingestion command
- Document cleaning and chunking
- Batch embedding generation
- ChromaDB vector indexing
- Processing event logging
- Re-ingestion handling
- Content hash tracking
- Embedding model tracking
- Top-K semantic retrieval
- Similarity scores
- Metadata filtering
- Minimum score threshold
- Stable source labels
- Duplicate chunk removal
- Context size limits
- Integration testing
- Failed-document isolation

**Day 7 Ingestion:**
```
Documents processed: 30
Documents completed: 30
Documents failed: 0
Chunks processed: 47
Indexed chunks: 47

Re-ingestion Verification:

The approved document set was ingested twice.

First ingestion:
47 indexed chunks

Second ingestion:
47 indexed chunks

The indexed chunk count remained 47, confirming that re-ingestion does not create uncontrolled duplicate chunks.

Processing Events:

STARTED / SUCCESS    219
COMPLETED / SUCCESS  219
FAILED / FAILED       2

Processing events are persisted in SQLite, including successful and failed processing attempts. Failed documents are logged without stopping successful document processing. The two failed events shown here are accumulated from earlier runs and tests, not from the final successful 30-document ingestion.
```

**Retrieval Context Example:**

**Question:**
```
What is a Python variable?
```

**Top result:**
```
DOC001_CHUNK_001 | DOC001 | Python Basics | score=0.8288
```

**Generation-ready source label:**
```
[DOC001 | DOC001_CHUNK_001]
Title: Python Basics
Source: sample_data\day5_documents\DOC001_python_basics.md
```

The context preparation step removes duplicate chunks and limits the final context by chunk count and character count.

**Day 7 Integration Tests:**
```
test_ingest_then_retrieve                          PASSED
test_failed_document_does_not_stop_other_documents PASSED

2 passed
```

**Day 7 Commands:**

Ingest the approved document set:
```bash
python -m scripts.ingest_documents
```

Display retrieval context:
```bash
python -m scripts.show_retrieval_context "What is a Python variable?"
```

Run Day 7 integration tests:
```bash
python.exe -m pytest tests/test_rag_pipeline.py -v
```

**Day 7 Completion Gate:**
- [x] Full basic RAG flow is visible in code
- [x] Separate ingestion, retrieval, and context modules implemented
- [x] Approved document ingestion command created
- [x] Re-ingestion does not create uncontrolled duplicate chunks
- [x] Retrieved context includes stable source labels
- [x] Integration tests pass
- [x] Failed document handling verified
- [x] Ingest-then-retrieve flow verified
- [x] End-to-end document-to-context flow demonstrated

**End-of-Day Evidence:**

```
Raw document
    ↓
Document cleaning
    ↓
Chunking
    ↓
Embedding generation
    ↓
ChromaDB vector storage
    ↓
Semantic retrieval
    ↓
Generation-ready context
```

**Example document:**
```
DOC001 — Python Basics
```

**Retrieved chunk:**
```
DOC001_CHUNK_001
```

**Retrieved source label:**
```
[DOC001 | DOC001_CHUNK_001]
```

---

## 📁 Project Structure

```
genai-assistant/

├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── llm/
│   ├── models/
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── generate.py
│   │   ├── ingest.py
│   │   ├── retrieve.py
│   │   └── vector_store.py
│   ├── safety/
│   └── voice/
│
├── datasets/
│   ├── prompt_test_cases.json
│   └── day6_retrieval_test_cases.json
│
├── prompts/
│   ├── summarization.txt
│   ├── summarization_v1.txt
│   ├── summarization_v2.txt
│   ├── extraction.txt
│   └── classification.txt
│
├── results/
│   ├── chunks.jsonl
│   ├── day6_retrieval_report.json
│   └── chroma_db/
│
├── sample_data/
│   └── day5_documents/
│
├── scripts/
│   ├── build_vector_index.py
│   ├── ingest_documents.py
│   ├── run_retrieval_tests.py
│   └── show_retrieval_context.py
│
├── tests/
│   └── test_rag_pipeline.py
│
├── .env.example
├── README.md
└── requirements.txt
```

---

## 🛠️ Technology Stack

**Programming Language:**
- Python 3.11

**AI / LLM:**
- OpenRouter API
- OpenAI Python SDK

**Embeddings:**
- Sentence Transformers
- all-MiniLM-L6-v2
- 384-dimensional embeddings

**Vector Database:**
- ChromaDB

**Database:**
- SQLite
- SQLAlchemy

**Validation:**
- Pydantic

**Testing:**
- Pytest

**Environment:**
- python-dotenv

**Version Control:**
- Git
- GitHub

---

## 📦 Installation

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔧 Usage & Testing

### Day 6 – Build Vector Index

After the Day 5 chunking process is completed, build the vector index using:

```bash
python -m scripts.build_vector_index
```

**Expected output:**
```
Selected chunks: 26
Chunks embedded: 26
Chunks skipped: 0
Total indexed chunks: 26
```

---

### Verify Vector Database

Run:
```bash
python -c "from app.rag.vector_store import get_collection, get_collection_count; collection=get_collection(); print('Collection:', collection.name); print('Count:', get_collection_count())"
```

**Expected:**
```
Collection: day6_chunks
Count: 26
```

---

### Verify Embedding Dimension

Run:
```bash
python -c "from app.rag.embeddings import get_embedding_dimension; print('Embedding dimension:', get_embedding_dimension())"
```

**Expected:**
```
Embedding dimension: 384
```

---

### Test Semantic Search

Run:
```bash
python -c "from app.rag.retrieve import retrieve_documents; results=retrieve_documents('What is a Python variable?'); print('Results:', len(results)); [print(r) for r in results]"
```

The retrieval system returns:
- Chunk ID
- Document ID
- Text
- Title
- Similarity score
- Source path
- Metadata

---

### Metadata Filtering

Metadata filtering can be tested using:

```bash
python -c "from app.rag.retrieve import retrieve_documents; results=retrieve_documents('What is a Python variable?', top_k=3, where={'category':'python'}); print('Results:', len(results)); [print(r['document_id'], r['title'], r['score'], r['category']) for r in results]"
```

**Example:**
```
DOC001 Python Basics 0.8288 python
DOC002 Python Functions 0.5284 python
DOC004 Python Modules 0.5112 python
```

---

### Minimum Score Threshold

The retrieval system supports a minimum score threshold.

**Example:**
```bash
python -c "from app.rag.retrieve import retrieve_documents; results=retrieve_documents('What is a Python variable?', top_k=3, min_score=0.6); print('Results:', len(results)); [print(r['document_id'], r['title'], r['score']) for r in results]"
```

**Example result:**
```
Results: 1
DOC001 Python Basics 0.8288
```

---

### Retrieval Evaluation

The Day 6 retrieval test dataset is stored in:
```
datasets/day6_retrieval_test_cases.json
```

The dataset contains:
- 10 questions
- Expected document IDs
- Manually selected source documents

Run the evaluation using:
```bash
python -m scripts.run_retrieval_tests
```

**Expected final result:**
```
Passed: 10/10
Failed: 0/10
Report saved to: results\day6_retrieval_report.json
```

---

### Retrieval Result Report

The generated report is stored at:
```
results/day6_retrieval_report.json
```

The report contains:
- Embedding model
- Top-K value
- Total test questions
- Passed count
- Failed count
- Accuracy
- Question
- Expected document
- Top-3 results
- Similarity scores
- Document IDs
- Titles
- Source paths
- Chunk IDs
- Metadata
- PASS/FAIL result

---

### Retrieval Examples

#### Successful Retrieval Example 1

**Question:**
```
What is a Python variable?
```

**Retrieved:**
```
DOC001 — Python Basics
Score: 0.8288
```

**Result:** ✅ PASS

---

#### Successful Retrieval Example 2

**Question:**
```
What is machine learning?
```

**Expected document:**
```
DOC019
```

The retrieval system successfully returned the Artificial Intelligence Basics document containing the Machine Learning section.

**Result:** ✅ PASS

---

#### Weak Retrieval Example

**Question:**
```
Tell me something about programming.
```

**Top results:**
```
DOC001 — Python Basics — 0.3595
DOC019 — Artificial Intelligence Basics — 0.3355
DOC019 — Artificial Intelligence Basics — 0.3239
```

This is considered a weak retrieval example because the query is broad and the similarity scores are relatively low.

This can be improved later using advanced RAG techniques such as query improvement, better chunking, reranking, and result diversification.

---

### Automated Testing

Run all project tests:

```bash
python.exe -m pytest
```

---

## 📊 Current Progress

| Day | Feature | Status |
|-----|---------|--------|
| 1 | Project Foundation | ✅ Complete |
| 2 | Data Validation & Storage | ✅ Complete |
| 3 | Prompt Playground | ✅ Complete |
| 4 | Structured Outputs & Prompt Testing | ✅ Complete |
| 5 | Document Preprocessing & Chunking | ✅ Complete |
| 6 | Vector Indexing & Semantic Search | ✅ Complete |
| 7 | Baseline RAG Ingestion & Retrieval | ✅ Complete |

---

## 🗓️ Future Roadmap

Upcoming features include:

- Grounded generation with LLM answer generation using retrieved chunks
- Citation generation from retrieved sources
- Retrieval reranking
- Advanced chunking strategies
- Query optimization
- FastAPI REST APIs
- User authentication
- Voice assistant integration
- AI safety guardrails
- Conversation memory
- Streaming responses
- Docker support
- CI/CD pipeline
- Cloud deployment

---

## 📚 Learning Outcomes

This project demonstrates practical experience with:

- Prompt Engineering
- Large Language Model (LLM) Integration
- Structured AI Outputs
- Pydantic Validation
- Prompt Evaluation
- AI Testing Frameworks
- JSON Schema Validation
- Python Backend Development
- SQLite & SQLAlchemy
- OpenRouter API Integration
- Modular Software Design
- Document Preprocessing
- Text Chunking
- Text Embeddings
- Sentence Transformers
- Vector Databases
- ChromaDB
- Semantic Search
- Top-K Retrieval
- Metadata Filtering
- Retrieval Evaluation
- RAG Foundations
- Git & GitHub Workflow

---

## 👨‍💻 Author

**Madhusudhana V C**

GitHub: https://github.com/MadhusudhanaVC

---

## 📄 License

This project is developed for learning, experimentation, and educational purposes as part of a structured AI Engineering roadmap.