# GenAI Assistant

## Project Overview

This project is a backend foundation for a GenAI Assistant.

Day 2 features include:

- JSON document validation using Pydantic
- Command Line Interface (CLI) document loader
- SQLite database integration
- Processing event logging
- Automated testing using Pytest

---

## Project Structure

```
genai-assistant/
│
├── app/
│   ├── db/
│   ├── models/
│   ├── rag/
│   ├── safety/
│   └── voice/
│
├── sample_data/
├── scripts/
├── tests/
├── README.md
└── requirements.txt
```

---

## Setup

Create Virtual Environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Install Packages

```bash
pip install -r requirements.txt
```

---

## Create Database

```bash
python -m scripts.create_database
```

---

## Load Documents

```bash
python -m scripts.load_documents sample_data/valid.json
```

---

## View Database

```bash
python -m scripts.view_database
```

---

## Run Tests

```bash
python -m pytest
```

---

## Technologies Used

- Python 3.11
- SQLite
- SQLAlchemy
- Pydantic
- Pytest
- Git