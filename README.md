# GenAI Assistant

A production-ready Generative AI Assistant project built using Python and FastAPI.

---

## 📌 Project Overview

This project is being developed as part of the GenAI Team Practical Roadmap.

Current Features

- Project Structure
- Virtual Environment
- Configuration Management
- Git Repository
- Smoke Test

Future Features

- RAG Pipeline
- Vector Database
- FastAPI APIs
- Guardrails
- Evaluation
- Voice Assistant

---

## Project Structure

```text
genai-assistant/

app/
    api/
    core/
    db/
    rag/
    safety/
    voice/

tests/
scripts/
evals/
docs/

requirements.txt
.env.example
.gitignore
README.md
```

---

## Setup

### Clone Repository

```bash
git clone <repository-url>
```

### Go to Project

```bash
cd genai-assistant
```

### Create Virtual Environment

```bash
py -3.11 -m venv .venv
```

### Activate Environment

Windows

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Run Smoke Test

```bash
python -m app.main
```

Expected Output

```
Project setup completed successfully!
```

---

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- Pytest

---

## Author

GenAI Team