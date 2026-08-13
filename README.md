# Day 5 — Document Preprocessing and Chunking

## Overview

Day 5 focuses on preparing approved documents for the **Retrieval-Augmented Generation (RAG)** pipeline.

The goal is to build a reliable preprocessing pipeline that converts source documents into clean, meaningful, traceable, and retrieval-ready chunks.

The current implementation processes **30 approved sample documents** and generates a normalized **JSONL dataset containing 47 chunks**, with metadata attached to every chunk.

---

## Day 5 Objectives

The preprocessing pipeline is designed to:

- Load approved Markdown, text, or HTML documents.
- Assign a stable document ID to every document.
- Remove unnecessary document front matter.
- Clean and normalize document text.
- Preserve meaningful Markdown headings.
- Split documents into logical sections.
- Create configurable chunks using chunk size and overlap.
- Preserve useful context between chunks using overlap.
- Avoid unnecessary splitting of Markdown code blocks.
- Attach complete metadata to every chunk.
- Generate an inspectable JSONL dataset.
- Detect and report document-processing failures.
- Validate chunking behavior using automated tests.
- Inspect representative chunks for quality.
- Correct document-content issues identified during review.

---

## Day 5 Processing Flow

```text
Approved Documents
        │
        ▼
Read Documents
        │
        ▼
Remove Front Matter
        │
        ▼
Clean & Normalize Text
        │
        ▼
Detect Markdown Sections
        │
        ▼
Create Chunks
        │
        ├── Small Sections → Combine
        │
        └── Large Sections → Split
        │
        ▼
Apply Chunk Overlap
        │
        ▼
Attach Metadata
        │
        ▼
Generate JSONL Dataset
        │
        ▼
Validate Dataset
        │
        ▼
Run Automated Tests
```
---


## Day 5 Processing Flow
```text
app/
└── rag/
    └── chunking.py

scripts/
└── preprocess_documents.py

tests/
└── test_chunking.py

sample_data/
└── day5_documents/
    ├── DOC001_python_basics.md
    ├── DOC002_python_functions.md
    ├── DOC003_python_exception_handling.md
    ├── DOC004_python_modules.md
    ├── DOC005_python_virtual_environments.md
    ├── DOC006_python_testing.md
    ├── ...
    └── DOC030_ai_natural_language_processing.md

results/
├── chunks.jsonl
└── chunk_quality_review.md
        │
        ▼
Inspect Chunk Quality
```
