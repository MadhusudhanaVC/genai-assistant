# Day 9 — Controlled Retrieval Experiment Results

## Overview

Day 9 evaluates controlled retrieval experiments using the frozen baseline configuration.

Each experiment changes only one primary retrieval variable while keeping all other baseline settings unchanged.

The purpose is to determine whether the proposed retrieval changes improve ranking, evidence coverage, or separation from competing documents.

---

## Frozen Baseline

The baseline configuration is:

- Embedding model: `all-MiniLM-L6-v2`
- Embedding normalization: `true`
- Embedding dimension: `384`
- Chunk size: `500`
- Chunk overlap: `80`
- Top-K: `3`
- Minimum score: `None`
- Metadata filter: `None`
- Collection: `day6_chunks`
- Vector store: `results/chroma_db`
- Evaluation dataset: `datasets/day6_retrieval_test_cases.json`

### Baseline Metrics

- Total questions: `10`
- Hit@1: `0.90`
- Hit@3: `1.00`
- MRR: `0.95`

Nine of the ten expected documents were ranked first.

Q10 was the only question where the expected document was ranked below first place.

---

# E01 — Q10 Machine Learning

## Variable Changed

`query_wording`

## Baseline

Query:

`What is machine learning?`

Expected document:

`DOC019`

Result:

- Expected rank: `2`
- Hit@1: `False`
- Hit@3: `True`
- MRR: `0.5`

Retrieved competition:

- `DOC020` — score `0.7128`
- `DOC019` — score `0.7100`

Baseline score margin:

`0.7128 - 0.7100 = 0.0028`

## Experiment

Query:

`What is machine learning and how is it defined?`

Result:

- Expected rank: `2`
- Hit@1: `False`
- Hit@3: `True`
- MRR: `0.5`

Retrieved competition:

- `DOC020` — score `0.6696`
- `DOC019` — score `0.6663`

Experiment score margin:

`0.6696 - 0.6663 = 0.0033`

## Conclusion

**Hypothesis rejected.**

The query rewrite did not move `DOC019` to rank 1.

The expected document remained at rank 2 and the competing document remained ahead.

The score separation also did not improve in the desired direction.

### Root Cause Finding

The machine-learning query remains ambiguous with the competing AI-related document.

### Measurement

Expected rank, Hit@1, Hit@3, MRR, and score margin were used to evaluate the hypothesis.

---

# E02 — Q7 Git Branch

## Variable Changed

`query_wording`

## Baseline

Query:

`What is a Git branch?`

Expected document:

`DOC008`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Scores:

- `DOC008` — `0.7093`
- `DOC007` — `0.7050`

Baseline margin:

`0.7093 - 0.7050 = 0.0043`

## Experiment

Query:

`What is a Git branch and how is it used for separate lines of development?`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Scores:

- `DOC008` — `0.7281`
- `DOC007` — `0.6683`

Experiment margin:

`0.7281 - 0.6683 = 0.0598`

## Conclusion

**Hypothesis supported.**

The expected document remained rank 1, while the score separation from the competing Git document increased substantially.

Margin:

`0.0043 → 0.0598`

### Root Cause Finding

The original query was semantically close to the general Git document.

Adding explicit branch-development intent improved separation from that competing document.

### Measurement

Expected rank, Hit@1, Hit@3, MRR, and score margin were used.

---

# E03 — Q4 Python Module

## Variable Changed

`query_wording`

## Baseline

Query:

`What is a Python module?`

Expected document:

`DOC004`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Scores:

- `DOC004` — `0.7786`
- `DOC001` — `0.6512`

Baseline margin:

`0.7786 - 0.6512 = 0.1274`

## Experiment

Query:

`What is a Python module and how is it used to organize Python code?`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Scores:

- `DOC004` — `0.7365`
- `DOC001` — `0.5970`

Experiment margin:

`0.7365 - 0.5970 = 0.1395`

## Conclusion

**Hypothesis supported for score separation.**

The expected document was already rank 1, so Hit@1, Hit@3, and MRR did not improve.

However, the score margin increased:

`0.1274 → 0.1395`

### Root Cause Finding

The original query was short and generic. The more explicit module-focused wording increased separation from another Python document.

### Measurement

Expected rank, Hit@1, MRR, and score margin were used.

---

# E04 — Q8 Git Merge Conflict

## Variable Changed

`top_k`

## Baseline

Query:

`What causes a Git merge conflict?`

Top-K:

`3`

Expected document:

`DOC009`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Retrieved documents:

1. `DOC009_CHUNK_001`
2. `DOC009_CHUNK_002`
3. `DOC012_CHUNK_002`

Unique documents:

`3`

## Experiment

Top-K:

`5`

All other baseline parameters remained unchanged.

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Retrieved documents:

1. `DOC009_CHUNK_001`
2. `DOC009_CHUNK_002`
3. `DOC012_CHUNK_002`
4. `DOC010_CHUNK_001`
5. `DOC007_CHUNK_001`

Unique documents:

`4`

## Conclusion

**Hypothesis supported.**

Increasing Top-K from 3 to 5 exposed an additional unique document while keeping the expected document at rank 1.

The experiment did not improve ranking accuracy because the baseline was already correct.

### Root Cause Finding

The baseline Top-K contains multiple chunks from the same expected document.

Increasing Top-K provides additional document evidence, but the usefulness of that additional evidence must be evaluated based on the downstream question.

### Measurement

Hit@1, Hit@3, MRR, unique-document count, and chunks-per-document were used.

---

# E05 — Q1 Python Variable

## Variable Changed

`query_wording`

## Baseline

Query:

`What is a Python variable?`

Expected document:

`DOC001`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Scores:

- `DOC001` — `0.8288`
- `DOC004` — `0.5284`

Baseline margin:

`0.8288 - 0.5284 = 0.3004`

## Experiment

Query:

`What is a Python variable and what does it store?`

Result:

- Expected rank: `1`
- Hit@1: `True`
- Hit@3: `True`
- MRR: `1.0`

Scores:

- `DOC001` — `0.7820`
- `DOC004` — `0.4990`

Experiment margin:

`0.7820 - 0.4990 = 0.2830`

## Conclusion

**Hypothesis rejected.**

The expected document remained rank 1, but the score margin decreased:

`0.3004 → 0.2830`

Therefore, the query rewrite did not provide a measurable retrieval improvement for this case.

### Root Cause Finding

The original query already provided strong separation from related Python documents.

Additional query wording was unnecessary and did not improve the retrieval result.

### Measurement

Expected rank, Hit@1, Hit@3, MRR, and score margin were used.

---

# Overall Experiment Results

| Experiment | Variable | Baseline Result | Experiment Result | Conclusion |
|---|---|---|---|---|
| E01 | Query wording | DOC019 rank 2 | DOC019 rank 2 | Rejected |
| E02 | Query wording | DOC008 rank 1, margin 0.0043 | DOC008 rank 1, margin 0.0598 | Supported |
| E03 | Query wording | DOC004 rank 1, margin 0.1274 | DOC004 rank 1, margin 0.1395 | Supported |
| E04 | Top-K | 3 unique documents | 4 unique documents | Supported |
| E05 | Query wording | DOC001 margin 0.3004 | DOC001 margin 0.2830 | Rejected |

---

# Root Cause Findings

## Q10 — Machine Learning

Primary issue:

**Low ranking / semantic ambiguity**

The expected machine-learning document competes closely with another AI-related document.

Query rewriting tested in E01 did not resolve the ranking problem.

---

## Q7 — Git Branch

Primary issue:

**Low ranking margin / semantic competition**

The general Git document was extremely close to the specific Git Branch document.

Explicit branch-focused wording improved separation.

---

## Q4 — Python Module

Primary issue:

**Broad query / related-document competition**

The original query was already successful, but explicit module-focused wording slightly improved score separation.

---

## Q8 — Git Merge Conflict

Primary issue:

**Same-document chunk concentration / Top-K utilization**

The expected document occupied two of the first three retrieved positions.

Increasing Top-K exposed another unique document.

---

## Q1 — Python Variable

Primary issue:

**Broad query / related-document competition**

However, the baseline already had strong separation.

E05 showed that the query rewrite was unnecessary for this case.

---

# Final Day 9 Findings

The controlled experiments demonstrate that retrieval improvements must be evaluated on a per-case basis.

Query rewriting:

- Improved separation for Q7.
- Improved separation for Q4.
- Did not improve Q10.
- Did not improve Q1.

Top-K adjustment:

- Increased unique document coverage for Q8.
- Did not change the correct document's rank.

Therefore:

**Query rewriting should not be treated as a universal retrieval fix.**

The frozen baseline should remain the reference configuration, and retrieval changes should be introduced only when measurements demonstrate a meaningful improvement.

---

# Day 9 Completion Evidence

- Frozen baseline configuration recorded.
- Five diagnostic questions analyzed.
- Expected source document identified for each question.
- Failure classifications documented.
- Root-cause hypotheses documented.
- Controlled experiment matrix created.
- E01 completed.
- E02 completed.
- E03 completed.
- E04 completed.
- E05 completed.
- Per-question experiment results saved.
- Hypotheses evaluated using measured retrieval evidence.
- Final experiment conclusions documented.

## Day 9 Status
**COMPLETE**