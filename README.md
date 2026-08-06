# GenAI Assistant

## Project Overview

GenAI Assistant is a backend foundation for building AI-powered applications.

The project is being developed through a structured 20-day roadmap, where each day introduces new AI engineering concepts and practical implementations.

### Current Features

### Day 2
- JSON document validation using Pydantic
- Command Line Interface (CLI) document loader
- SQLite database integration
- SQL processing event logging
- Automated testing using Pytest

### Day 3
- Shared OpenRouter/OpenAI model client wrapper
- Prompt playground for AI tasks
- Summarization prompt
- Information extraction prompt
- Text classification prompt
- Prompt templates stored separately from code
- Latency measurement for every AI request
- Sample inputs and generated outputs

---

# Project Structure

```
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
├── prompts/
│   ├── summarization.txt
│   ├── extraction.txt
│   └── classification.txt
│
├── sample_data/
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
├── README.md
└── requirements.txt
```

---

# Technologies Used

- Python 3.11
- OpenRouter API
- OpenAI Python SDK
- SQLite
- SQLAlchemy
- Pydantic
- Pytest
- python-dotenv
- Git
- GitHub

---

# Setup

## 1. Clone Repository

```bash
git clone <your_repository_url>
cd genai-assistant
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

---

## 3. Activate Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-oss-20b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

DATABASE_URL=sqlite:///genai.db
```

---

# Create Database

```bash
python -m scripts.create_database
```

---

# Document Loader

Validate JSON documents and store them in SQLite.

```bash
python -m scripts.load_documents sample_data/valid.json
```

---

# View Database

```bash
python -m scripts.view_database
```

---

# Prompt Playground

The Prompt Playground supports three AI tasks.

## 1. Summarization

```bash
python -m scripts.prompt_playground summarization sample_inputs/summarization/normal.txt
```

---

## 2. Information Extraction

```bash
python -m scripts.prompt_playground extraction sample_inputs/extraction/normal.txt
```

---

## 3. Text Classification

```bash
python -m scripts.prompt_playground classification sample_inputs/classification/normal.txt
```

---

# Test OpenRouter Connection

```bash
python -m scripts.test_openrouter
```

---

# Test LLM Client

```bash
python -m scripts.test_client
```

---

# Run All Tests

```bash
python -m pytest
```

---

# Current Progress

## ✅ Day 2
- JSON validation
- CLI document loader
- SQLite database
- SQL event logging
- Pytest automation

## ✅ Day 3
- Shared LLM client wrapper
- Prompt playground
- Summarization
- Information extraction
- Text classification
- Prompt templates
- Sample inputs
- Sample outputs
- Latency measurement

---

# Future Roadmap

Upcoming features include:

- Retrieval-Augmented Generation (RAG)
- Embedding generation
- Vector database integration
- Semantic search
- FastAPI backend
- Authentication
- Voice support
- AI safety guardrails
- Production deployment

---

# Author

**Madhusudhana VC**

GitHub:
https://github.com/MadhusudhanaVC