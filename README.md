# Day 10: Advanced Retrieval and Measured Improvement

## Overview

Day 10 focused on improving the Day 9 retrieval baseline using controlled retrieval experiments. The goal was to identify and integrate configuration changes that provide measurable improvement without causing regressions.

## Objectives

- ✓ Implement query rewriting
- ✓ Conduct chunk-size experimentation
- ✓ Conduct top-k experimentation
- ✓ Implement cross-encoder reranking
- ✓ Perform before/after evaluation
- ✓ Check for regressions
- ✓ Measure latency and complexity

---

## Day 9 Frozen Baseline

### Baseline Configuration

| Setting | Value |
|---------|-------|
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
|--------|-------|
| Hit@1 | 0.90 |
| Hit@3 | 1.00 |
| MRR | 0.95 |

**Note:** The weak case was Q10, where expected document DOC019 was ranked second behind DOC020.

---

## Day 10 Implementation

### 1. Query Rewriting

A deterministic query-rewriting layer was added to convert selected questions into clearer, retrieval-oriented queries.

**File:** `app/rag/query_rewriter.py`

**Examples:**

```
What is a Python variable?
→ What is a Python variable and what does it store?

What is a Python module?
→ What is a Python module and how is it used to organize Python code?

What is a Git branch?
→ What is a Git branch and how is it used for separate lines of development?
```

**Evaluation Result:** Aggregate metrics remained unchanged.

**Decision:** ✓ **Retained as a supporting component; not selected as the primary improvement.**

---

### 2. Chunk Size Experiment

Tested reducing chunk size from 500 to 400 tokens with 80-token overlap in a separate vector store.

**Results:**

| Metric | Value |
|--------|-------|
| Hit@1 | 0.90 |
| Hit@3 | 1.00 |
| MRR | 0.95 |

**Finding:** Q10 expected document remained at rank 2. No measurable improvement.

**Decision:** ✗ **Rejected** for final configuration.

**Result file:** `results/day10_experiments/chunk400_results.json`

---

### 3. Top-k Experiment

Increased retrieval candidate count from 3 to 5 to provide more context diversity.

**Finding:** Additional candidates did not improve ranking of weak Q10 case.

**Decision:** ✗ **Not selected alone**, but proved useful as part of the reranking pipeline.

---

### 4. Cross-Encoder Reranking

Implemented a cross-encoder reranker to improve document ranking.

**File:** `app/rag/reranker.py`

**Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Retrieval Flow:**

```
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

**Reranker Tracking:** Preserves original retrieval information including:
- Original rank
- Original vector score
- Rerank score
- Final rank

**Decision:** ✓ **Selected** as primary improvement driver.

---

## Final Day 10 Configuration

### Integrated Configuration

| Parameter | Value |
|-----------|-------|
| Query rewriting | enabled |
| Initial retrieval top-k | 5 |
| Final top-k | 3 |
| Chunk size | 500 |
| Chunk overlap | 80 |
| Minimum score | null |
| Metadata filter | null |
| Embedding model | all-MiniLM-L6-v2 |
| Reranker model | cross-encoder/ms-marco-MiniLM-L-6-v2 |

**File:** `app/rag/generate.py`

---

## Results: Before vs After

### Overall Metrics

| Metric | Day 9 Baseline | Day 10 Final | Change |
|--------|----------------|--------------|--------|
| Hit@1 | 0.90 | 1.00 | **+0.10** ✓ |
| Hit@3 | 1.00 | 1.00 | 0.00 |
| MRR | 0.95 | 1.00 | **+0.05** ✓ |

### Q10 Improvement (Key Case)

**Expected document:** DOC019

**Baseline Ranking:**
- DOC020 → rank 1
- DOC019 → rank 2
- DOC029 → rank 3
- Reciprocal rank: 0.50

**Final Reranked Result:**
- DOC019 → rank 1
- DOC020 → rank 2
- DOC029 → rank 3
- Reciprocal rank: 1.00

**Improvement Summary:**
- Hit@1: false → **true** ✓
- Rank: 2 → **1** ✓
- RR: 0.50 → **1.00** ✓

---

## Performance Metrics

### Latency Measurement

| Component | Average Latency |
|-----------|-----------------|
| Retrieval | 2904.11 ms |
| Reranking | 1411.33 ms |
| **Total** | **4315.45 ms** |

**Trade-off:** The reranker provides measurable quality improvement at the cost of additional inference latency and model complexity.

### Regression Check

✓ **No regressions detected**

All previously passing questions remained passing in the final evaluation.

---

## Experiment Summary

| Experiment | Change | Result | Decision |
|------------|--------|--------|----------|
| Query rewriting | Rewrite selected queries | Aggregate metrics unchanged | ✓ Retained |
| Chunk size | 500 → 400 | Metrics unchanged | ✗ Rejected |
| Top-k | 3 → 5 | No direct ranking improvement | – Not selected alone |
| Cross-encoder reranking | Rerank initial top 5 | Hit@1: 0.90→1.00; MRR: 0.95→1.00 | ✓ Selected |

---

## Why Reranking Was Selected

Reranking was selected because it produced the clearest measurable improvement on the complete retrieval evaluation.

The final configuration improved:

- Hit@1: 0.90 → 1.00
- MRR: 0.95 → 1.00
- Q10 expected-document rank: 2 → 1

Hit@3 remained unchanged at 1.00.

The trade-off is additional inference latency:

- Retrieval: 2904.11 ms average
- Reranking: 1411.33 ms average
- Total: 4315.45 ms average

Despite the additional latency and model complexity, reranking was selected because retrieval quality improved and no regression was detected across the 10-question evaluation set.

---

## Project Structure

```
genai-assistant/
│
├── app/
│   ├── cli/
│   ├── config/
│   ├── db/
│   ├── llm/
│   │   ├── client.py
│   │   └── validator.py
│   ├── models/
│   │   └── prompt_outputs.py
│   └── rag/
│       ├── embeddings.py
│       ├── vector_store.py
│       ├── retrieve.py
│       ├── ingest.py
│       ├── generate.py
│       ├── query_rewriter.py          # NEW
│       └── reranker.py                 # NEW
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
│   ├── day10_query_rewrite_results.json          # NEW
│   ├── day10_reranker_results.json               # NEW
│   ├── day10_before_after_report.json            # NEW
│   ├── day10_experiments/
│   │   └── chunk400_results.json                 # NEW
│   └── chroma_db/
│
├── scripts/
│   ├── build_vector_index.py
│   ├── ingest_documents.py
│   ├── run_retrieval_tests.py
│   ├── day9_experiment.py
│   ├── day10_query_rewrite_evaluation.py         # NEW
│   ├── day10_reranker_evaluation.py              # NEW
│   ├── day10_test_reranker.py                    # NEW
│   ├── day10_chunk_size_experiment.py            # NEW
│   └── day10_final_report.py                     # NEW
│
├── tests/
│   ├── test_citation_validation.py
│   ├── test_grounded_validator.py
│   └── test_grounded_generation.py
│
├── verify_day8.py
├── README.md
├── .gitignore
└── ...
```

---

## Git Ignore

Generated ChromaDB data should not be committed to Git.

The following paths should be ignored:

```text
results/chroma_db/
results/chroma_db_day10_chunk400/
```

---

## Final RAG Pipeline

```
Question
   ↓
[Query Rewriting]
   ↓
[Vector Retrieval — Top 5]
   ↓
[Cross-Encoder Reranking]
   ↓
[Final Top 3]
   ↓
[Grounded Context]
   ↓
[LLM Answer]
   ↓
[Citation Validation]
```

---

## Validation

✓ Full test suite execution: **18 tests passed**

✓ Retrieval evaluation results:
- Hit@1 = 1.00
- Hit@3 = 1.00
- MRR = 1.00

---

## Deliverables

- ✓ Query rewriting implementation
- ✓ Chunk-size experiment (with results)
- ✓ Top-k experiment (with results)
- ✓ Cross-encoder reranking implementation
- ✓ Selected retrieval configuration
- ✓ Before/after metric report
- ✓ Per-question evaluation results
- ✓ Regression check across complete dataset
- ✓ Latency measurement
- ✓ Complexity trade-off documentation
- ✓ Rejected experiment evidence (preserved)
- ✓ Final RAG integration
- ✓ Full test suite validation

---

## Key Achievements

| Achievement | Evidence |
|-------------|----------|
| Weak case improved | Q10: rank 2 → 1 |
| Hit@1 improvement | 0.90 → 1.00 (+10%) |
| MRR improvement | 0.95 → 1.00 (+5%) |
| Zero regressions | All previous passes maintained |
| Perfect Hit@1 | All 10 expected documents ranked at #1 |
| Measured latency | 4.3s total (2.9s retrieval + 1.4s reranking) |

---

## Status

### ✅ COMPLETED

**Final Strategy:**

```
Query Rewrite
     +
Initial Vector Retrieval (Top 5)
     +
Cross-Encoder Reranking
     ↓
Final Top 3 Grounded Context
```

The Day 10 RAG system successfully advanced from a frozen baseline to a measured, improved, and validated retrieval pipeline with zero regressions.

---

## Files Reference

- **Configuration:** `app/rag/generate.py`
- **Query Rewriting:** `app/rag/query_rewriter.py`
- **Reranking:** `app/rag/reranker.py`
- **Evaluation Dataset:** `datasets/day6_retrieval_test_cases.json`
- **Results:** `results/day10_*.json`
- **Test Suite:** `tests/`