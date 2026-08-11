# Day 5 — Document Preprocessing and Chunking

## Overview

Day 5 focuses on preparing approved documents for the Retrieval-Augmented Generation (RAG) pipeline.

The goal is to build a reliable preprocessing pipeline that converts a collection of documents into clean, traceable, retrieval ready chunks.

The pipeline processes 30 approved sample documents and produces a normalized JSONL dataset containing chunk text and metadata.

---

## Day 5 Objective

Build a preprocessing pipeline that:

- Loads approved Markdown, text, or HTML documents.
- Assigns a stable document ID to every document.
- Cleans and normalizes document text.
- Preserves meaningful Markdown headings.
- Splits documents into configurable chunks.
- Uses configurable chunk size and overlap.
- Attaches complete metadata to every chunk.
- Produces an inspectable JSONL dataset.
- Detects and reports document processing failures.
- Provides automated tests for the chunking logic.
- Includes a chunk-quality review for selected documents.

---

## Project Structure

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
    ├── ...
    └── DOC030_ai_natural_language_processing.md

results/
├── chunks.jsonl
└── chunk_quality_review.md
