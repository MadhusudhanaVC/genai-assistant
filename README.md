# GenAI Assistant — Day 8

## Grounded Generation, Citations & Abstention

Day 8 implements the grounded-generation layer on top of the existing RAG retrieval pipeline.

The goal is to make the assistant answer questions only from retrieved document evidence, return valid source citations, and safely abstain when the available evidence is insufficient.

---

## 🎯 Day 8 Objective

Build a grounded answer-generation pipeline that:

- Retrieves relevant document chunks.
- Builds a controlled context from retrieved evidence.
- Sends the question and evidence to the LLM.
- Validates the LLM response with Pydantic.
- Validates citations against the retrieved source chunks.
- Rejects unsupported citations.
- Requires valid citations for answered responses.
- Abstains when there is not enough evidence.

---

## 🔄 Day 8 RAG Flow

```text
User Question
      ↓
Document Retrieval
      ↓
Similarity / Evidence Threshold
      ↓
Context Preparation
      ↓
Grounded Prompt
      ↓
LLM Generation
      ↓
Pydantic Response Validation
      ↓
Citation Validation
      ↓
 ┌───────────────┐
 │               │
Answered     Insufficient
 + valid      evidence
citation        ↓
      ↓       Safe abstention
   Response
```

---

## 🧠 Grounded Generation

The grounded generation pipeline is implemented in:

```text
app/rag/generate.py
```

The pipeline:

- Validates the question.
- Retrieves relevant documents using `retrieve_documents()`.
- Applies the configured similarity threshold.
- Builds a limited context from retrieved chunks.
- Loads the grounded prompt template.
- Sends the grounded prompt to the LLM.
- Validates the returned structured response.
- Validates returned citations against retrieved evidence.
- Returns either a grounded answer or an abstention response.

---

## 📚 Context Preparation

Retrieved chunks are converted into a controlled context containing:

```text
[DOCUMENT_ID | CHUNK_ID]

Title: ...

Source: ...

Retrieved chunk text
```

Example:

```text
[DOC001 | DOC001_CHUNK_001]
Title: Python Basics
Source: documents/python.md

A Python variable stores a value that can be used later in a program.
```

The context preparation logic also provides:

- Maximum context chunk limit.
- Maximum context character limit.
- Duplicate chunk removal.
- Source labels for citation tracking.
- Empty-content filtering.

---

## 📝 Grounded Prompt

The grounded prompt template is stored separately:

```text
prompts/grounded_answer.txt
```

The prompt provides the LLM with:

- The user's question.
- Retrieved document evidence.
- Instructions to stay grounded in the supplied evidence.
- Instructions for producing the expected structured response.

Keeping the prompt in a separate file makes it easier to maintain and version independently from application code.

---

## 📦 Grounded Response Schema

The structured response model is implemented in:

```text
app/models/prompt_outputs.py
```

The expected response contains:

```json
{
  "answer": "A Python variable stores a value.",
  "status": "answered",
  "citations": [
    "[DOC001 | DOC001_CHUNK_001]"
  ]
}
```

Supported statuses:

```text
answered
insufficient_evidence
```

---

## 🔗 Citation Validation

Citations must match the retrieved source format:

```text
[DOC001 | DOC001_CHUNK_001]
```

Citation validation is implemented in:

```text
app/rag/generate.py
```

A citation is considered valid only when it corresponds to a retrieved document/chunk pair.

For example:

```text
Retrieved:
[DOC001 | DOC001_CHUNK_001]

LLM citation:
[DOC001 | DOC001_CHUNK_001]

Result:
VALID
```

An unsupported citation is rejected.

For example:

```text
Retrieved:
[DOC001 | DOC001_CHUNK_001]

LLM citation:
[DOC999 | DOC999_CHUNK_999]

Result:
INVALID
```

If the LLM reports:

```text
status = answered
```

but no valid citation remains after validation, the application converts the result to:

```text
status = insufficient_evidence
```

---

## 🛑 Safe Abstention

When the retrieved evidence is insufficient, the system does not invent an answer.

It returns:

```text
I don't have enough evidence in the provided documents to answer this question.
```

with:

```json
{
  "status": "insufficient_evidence",
  "citations": []
}
```

This provides a safe fallback for unsupported questions.

---

## 🧪 Day 8 Test Coverage

Day 8 includes tests for three important cases.

### 1. Answerable Question

The question can be answered using the retrieved evidence.

Expected:

```text
status: answered
valid citation returned
```

### 2. Partially Answerable Question

Only part of the question is supported by the available evidence.

Expected:

```text
answer uses supported evidence
valid citations are retained
```

### 3. Unanswerable Question

The retrieved evidence does not support the question.

Expected:

```text
status: insufficient_evidence
citations: []
```

---

## ✅ Day 8 Tests

Test file:

```text
tests/test_grounded_generation.py
```

Run:

```bat
python.exe -m pytest tests/test_grounded_generation.py -v
```

Verified result:

```text
3 passed
```

The three verified tests are:

```text
test_answerable_question_returns_cited_answer
test_partially_answerable_question_uses_supported_evidence
test_unanswerable_question_abstains
```

---

## 🔍 Day 8 Verification

### Verify grounded response model

```bat
python.exe -c "from app.models.prompt_outputs import GroundedAnswerOutput; print(GroundedAnswerOutput(answer='Test answer', status='answered', citations=['[DOC001 | DOC001_CHUNK_001]']))"
```

### Verify grounded response validator

```bat
python.exe test_grounded_validator.py
```

Expected:

```text
(True, GroundedAnswerOutput(...), None)
```

### Verify citation validation

```bat
python.exe test_citation_validation.py
```

Expected:

```text
Validated citations:
['[DOC001 | DOC001_CHUNK_001]']
```

### Verify grounded generation import

```bat
python.exe -c "from app.rag.generate import generate_grounded_answer; print('Grounded generation import: OK')"
```

### Verify unsupported-question abstention

```bat
python.exe -c "from app.rag.generate import generate_grounded_answer; result=generate_grounded_answer('What is the capital of Mars?', min_score=0.99); print(result)"
```

Expected behavior:

```text
status: insufficient_evidence
citations: []
```

### Run Day 8 verification

```bat
python.exe verify_day8.py
```

Expected:

```text
============================================================
DAY 8 GROUNDED GENERATION VERIFICATION
============================================================

1. ANSWERABLE QUESTION
------------------------------------------------------------
Answer: A Python variable stores a value.
Status: answered
Citations: ['[DOC001 | DOC001_CHUNK_001]']

2. UNSUPPORTED QUESTION
------------------------------------------------------------
Answer: I don't have enough evidence in the provided documents to answer this question.
Status: insufficient_evidence
Citations: []

============================================================
DAY 8 VERIFICATION PASSED
============================================================
```

---

## 🧪 Full Test Suite

Run:

```bat
python.exe -m pytest tests -v
```

Verified result:

```text
18 passed
```

This confirms that the Day 8 changes did not break the existing project tests.

---

## 📁 Project Structure

```text
genai-assistant/
│
├── app/
│   ├── llm/
│   │   ├── client.py
│   │   ├── validator.py
│   │   └── ...
│   │
│   ├── models/
│   │   └── prompt_outputs.py
│   │
│   └── rag/
│       ├── generate.py
│       ├── retrieve.py
│       ├── embeddings.py
│       ├── vector_store.py
│       └── ...
│
├── prompts/
│   └── grounded_answer.txt
│
├── tests/
│   ├── test_grounded_generation.py
│   └── test_rag_pipeline.py
│
├── scripts/
│   └── test_client.py
│
├── test_citation_validation.py
├── test_grounded_validator.py
├── verify_day8.py
│
├── .env.example
├── README.md
└── requirements.txt
```

---

## 🏁 Day 8 Completion Gate

- [x] Grounded answer prompt implemented
- [x] Grounded response schema implemented
- [x] Pydantic response validation implemented
- [x] Citation validation implemented
- [x] Invalid citations rejected
- [x] Answered responses require valid citations
- [x] Safe abstention implemented
- [x] Answerable question tested
- [x] Partially answerable question tested
- [x] Unanswerable question tested
- [x] Day 8 verification passed
- [x] Full project test suite passed

---

## 📊 Day 8 Final Status

```text
Day 8
-----

Grounded Generation       : COMPLETE
Structured Response       : COMPLETE
Citation Validation       : COMPLETE
Safe Abstention           : COMPLETE
Day 8 Tests               : 3/3 PASSED
Full Project Tests        : 18/18 PASSED
Verification              : PASSED
```

---

## 🚀 Day 8 Outcome

The RAG system now has a complete grounded-generation layer:

```text
Retrieve Evidence
       ↓
Prepare Context
       ↓
Generate Grounded Answer
       ↓
Validate Response
       ↓
Validate Citations
       ↓
Return Cited Answer
       OR
Abstain Safely
```

**Day 8 Status: ✅ COMPLETE**