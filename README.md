# GenAI Assistant

A modular Python-based **Generative AI Assistant** built as part of a structured **20-Day AI Engineering Roadmap**.

The project focuses on learning and implementing production-oriented AI engineering concepts such as structured outputs, prompt engineering, validation, testing, database integration, and LLM application development.

The goal is to gradually evolve this project into a complete AI Assistant with Retrieval-Augmented Generation (RAG), vector databases, FastAPI services, voice capabilities, AI safety guardrails, and production deployment.

---

# Project Highlights

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

---

# Features by Roadmap

## ✅ Day 1 – Project Foundation

- Python project structure
- Virtual environment setup
- Dependency management
- Git repository initialization
- Modular application architecture

---

## ✅ Day 2 – Data Validation & Storage

- JSON document validation using Pydantic
- CLI document loader
- SQLite database integration
- SQLAlchemy ORM
- Processing event logging
- Database viewer
- Automated testing using Pytest

---

## ✅ Day 3 – Prompt Playground

Implemented a reusable Prompt Playground capable of handling multiple business-oriented AI tasks.

### Features

- Shared OpenRouter/OpenAI client wrapper
- Model latency measurement
- Prompt templates stored separately
- Prompt placeholder replacement
- Reusable prompt execution pipeline

### Supported Tasks

- Text Summarization
- Information Extraction
- Text Classification

### Deliverables

- Prompt Playground
- Prompt Templates
- Sample Inputs
- Sample Outputs
- Shared LLM Client

---

## ✅ Day 4 – Structured Outputs & Prompt Testing

Implemented a production-style prompt evaluation framework.

### Features

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

### Deliverables

- Pydantic Output Models
- Prompt Dataset
- Prompt Test Harness
- Prompt Comparison Report
- JSON Test Results

---

# Project Structure

```text
genai-assistant/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── llm/
│   ├── models/
│   ├── rag/
│   ├── safety/
│   └── voice/
│
├── datasets/
│   └── prompt_test_cases.json
│
├── prompts/
│   ├── summarization.txt
│   ├── summarization_v1.txt
│   ├── summarization_v2.txt
│   ├── extraction.txt
│   └── classification.txt
│
├── results/
│   ├── prompt_test_results_v1.json
│   ├── prompt_test_results_v2.json
│   ├── prompt_outputs_v1.md
│   └── prompt_outputs_v2.md
│
├── sample_data/
│   ├── valid.json
│   └── invalid.json
│
├── sample_inputs/
│   ├── summarization/
│   ├── extraction/
│   └── classification/
│
├── sample_outputs/
│   ├── summarization/
│   ├── extraction/
│   └── classification/
│
├── scripts/
│
├── tests/
│
├── .env.example
├── .gitignore
├── PROMPT_COMPARISON.md
├── README.md
└── requirements.txt
```

---

# Technology Stack

## Programming Language

- Python 3.11

## AI

- OpenRouter API
- OpenAI Python SDK

## Database

- SQLite
- SQLAlchemy

## Validation

- Pydantic

## Testing

- Pytest

## Environment

- python-dotenv

## Version Control

- Git
- GitHub

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd genai-assistant
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

---

## Activate Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free

OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

DATABASE_URL=sqlite:///genai.db
```

---

## Verify OpenRouter Connection

```bash
python -m scripts.test_openrouter
```

---

## Test Shared LLM Client

```bash
python -m scripts.test_client
```

---

## Create Database

```bash
python -m scripts.create_database
```

---

## Load Sample Documents

```bash
python -m scripts.load_documents sample_data/valid.json
```

---

## View Database

```bash
python -m scripts.view_database
```

---

# Prompt Playground

The Prompt Playground provides a reusable interface for executing different AI tasks using prompt templates stored separately from the application logic.

## Supported Tasks

### 1. Text Summarization

Generate concise summaries from input documents.

```bash
python -m scripts.prompt_playground summarization sample_inputs/summarization/normal.txt
```

---

### 2. Information Extraction

Extract structured information from documents into JSON format.

```bash
python -m scripts.prompt_playground extraction sample_inputs/extraction/normal.txt
```

---

### 3. Text Classification

Classify text into predefined categories.

```bash
python -m scripts.prompt_playground classification sample_inputs/classification/normal.txt
```

---

# Structured Output Validation

The project validates every AI response using **Pydantic models** to ensure reliable and predictable outputs.

## Output Models

- SummaryOutput
- ExtractionOutput
- ClassificationOutput

Validation includes:

- JSON parsing
- Schema validation
- Required field validation
- Data type validation
- Error categorization

Supported failure categories:

- JSON_PARSE_ERROR
- VALIDATION_ERROR
- CONFIG_ERROR

---

# Prompt Test Harness

The Prompt Test Harness automatically evaluates prompts against a fixed dataset and validates the generated responses.

## Features

- Executes multiple prompt test cases
- Measures model latency
- Records prompt version
- Records model version
- Validates structured outputs
- Generates machine-readable result files
- Reports validation failures

---

## Run Prompt Tests

### Prompt Version 1

```bash
python -m scripts.run_prompt_tests --prompt-version v1
```

### Prompt Version 2

```bash
python -m scripts.run_prompt_tests --prompt-version v2
```

---

# Prompt Test Dataset

The dataset includes representative scenarios for each supported task.

Dataset Categories:

- Normal
- Long
- Ambiguous
- Incomplete

Tasks Covered:

- Summarization
- Information Extraction
- Classification

---

# Prompt Version Comparison

Two versions of the summarization prompt were evaluated using the same dataset.

## Version 1

- Summary under 100 words
- Return valid JSON

## Version 2

- Summary under 80 words
- Exactly 2–3 concise sentences
- Return valid JSON

## Results

| Metric | Version 1 | Version 2 |
|---------|-----------|-----------|
| Total Test Cases | 10 | 10 |
| Passed | 10 | 10 |
| Failed | 0 | 0 |

### Observation

Both prompt versions successfully passed schema validation for all test cases.

Version 2 produced shorter and more consistent summaries while preserving the important information from the source text.

**Preferred Prompt:** Version 2

---

# Automated Testing

Run all project tests:

```bash
python -m pytest
```

---

# Sample Outputs

Generated outputs are automatically saved to:

```text
sample_outputs/
├── summarization/
├── extraction/
└── classification/
```

Prompt test results are saved to:

```text
results/
├── prompt_test_results_v1.json
└── prompt_test_results_v2.json
```

---

# Current Progress

## ✅ Day 1 – Project Foundation

- Project setup
- Modular architecture
- Virtual environment
- Dependency management
- Git repository initialization

---

## ✅ Day 2 – Data Validation & Storage

- JSON document validation
- CLI document loader
- SQLite database integration
- SQLAlchemy ORM
- Processing event logging
- Database viewer
- Pytest automation

---

## ✅ Day 3 – Prompt Playground

- Shared LLM client
- Prompt templates
- Prompt execution pipeline
- Summarization
- Information extraction
- Text classification
- Sample inputs
- Sample outputs
- Latency measurement

---

## ✅ Day 4 – Structured Outputs & Prompt Testing

- Pydantic output models
- JSON response validation
- Prompt validation
- Prompt test dataset
- Prompt test runner
- Machine-readable test results
- Prompt version comparison
- Structured output testing
- Validation error reporting

---

# Future Roadmap

Upcoming features include:

- Retrieval-Augmented Generation (RAG)
- Embedding generation
- Vector database integration
- Semantic search
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

# Learning Outcomes

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
- Git & GitHub Workflow

---

# Author

**Madhusudhana V C**

GitHub:
https://github.com/MadhusudhanaVC

---

# License

This project is developed for learning, experimentation, and educational purposes as part of a structured AI Engineering roadmap.
