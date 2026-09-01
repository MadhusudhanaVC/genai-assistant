# Day 9 — Retrieval Failure Analysis

## Baseline Summary

The fixed retrieval baseline was evaluated on 10 questions.

- Hit@1: 90%
- Hit@3: 100%
- MRR: 0.95

The baseline is strong overall. Nine questions returned the expected
document at rank 1. One question returned the expected document at rank 2.

## Selection Method

The five weakest diagnostic questions were selected using:

1. Expected-document rank.
2. Reciprocal rank.
3. Similarity-score margin against competing results.
4. Competition from semantically related documents.
5. Top-K utilization and document/chunk diversity.

These are diagnostic cases, not five complete retrieval failures.

---

## Q10 — What is machine learning?

### Expected Source

DOC019

### Retrieved Evidence

1. DOC020 — score 0.7128
2. DOC019 — score 0.7100
3. DOC029 — score 0.4918

### Observed Result

The expected document DOC019 was retrieved at rank 2.

Hit@1: False

Hit@3: True

Reciprocal Rank: 0.5

### Failure Classification

Low ranking / semantic ambiguity.

### Root Cause Hypothesis

The query is broad and semantically close to both the machine-learning
document and the artificial-intelligence document. DOC020 narrowly
outranks the expected DOC019.

The score margin is:

0.7128 - 0.7100 = 0.0028

### Proposed Experiment

Change only the query wording.

### Confirmation Measurement

Measure:

- Expected document rank
- Hit@1
- Hit@3
- MRR
- Score margin between DOC019 and the competing result

The hypothesis is supported if a controlled query rewrite moves DOC019
to rank 1 without changing the retrieval configuration.

---

## Q7 — What is a Git branch?

### Expected Source

DOC008

### Retrieved Evidence

1. DOC008 — score 0.7093
2. DOC007 — score 0.7050
3. DOC010 — score 0.5691

### Observed Result

The expected document is rank 1, but DOC007 is an extremely close
semantic competitor.

The score margin is:

0.7093 - 0.7050 = 0.0043

### Failure Classification

Low ranking margin / semantic competition.

### Root Cause Hypothesis

The query contains the broad Git concept together with the specific
branch concept. The general Git document competes very closely with
the dedicated Git Branches document.

### Proposed Experiment

Change only the query wording.

### Confirmation Measurement

Measure:

- Expected document rank
- Hit@1
- Hit@3
- MRR
- Score margin against DOC007

The hypothesis is supported if the rewritten query increases the
separation between DOC008 and DOC007.

---

## Q4 — What is a Python module?

### Expected Source

DOC004

### Retrieved Evidence

1. DOC004 — score 0.7786
2. DOC001 — score 0.6512
3. DOC006 — score 0.5266

### Observed Result

The expected document is correctly ranked first.

### Failure Classification

Broad query / semantic competition.

### Root Cause Hypothesis

The query is short and generic. Other Python-related documents receive
meaningful similarity scores, although the intended module document
remains clearly ahead.

### Proposed Experiment

Change only the query wording.

### Confirmation Measurement

Measure:

- Expected document rank
- Hit@1
- Hit@3
- MRR
- Score margin against DOC001

This acts as a diagnostic control for whether query rewriting provides
additional separation when retrieval is already successful.

---

## Q8 — What causes a Git merge conflict?

### Expected Source

DOC009

### Retrieved Evidence

1. DOC009_CHUNK_001 — score 0.7784
2. DOC009_CHUNK_002 — score 0.6296
3. DOC012_CHUNK_002 — score 0.4453

### Observed Result

The expected document is ranked first.

However, two of the three retrieved positions belong to DOC009.

### Failure Classification

Same-document chunk concentration / Top-K utilization.

### Root Cause Hypothesis

The query strongly matches multiple chunks from the same document.
This can reduce document diversity within the Top-K result set.

### Proposed Experiment

Change only Top-K.

### Confirmation Measurement

Measure:

- Hit@1
- Hit@3
- MRR
- Number of unique documents retrieved
- Number of chunks per document

The hypothesis is supported or rejected based on whether changing Top-K
produces useful additional evidence or merely retrieves more chunks from
the same document.

---

## Q1 — What is a Python variable?

### Expected Source

DOC001

### Retrieved Evidence

1. DOC001 — score 0.8288
2. DOC002 — score 0.5284
3. DOC004 — score 0.5112

### Observed Result

The expected document is correctly ranked first.

### Failure Classification

Broad query / related-document competition.

### Root Cause Hypothesis

The query is short and general, so other Python documents also receive
non-trivial similarity scores. However, DOC001 has a strong lead.

### Proposed Experiment

Change only the query wording.

### Confirmation Measurement

Measure:

- Expected document rank
- Hit@1
- Hit@3
- MRR
- Score margin against the strongest competing document

If the result remains rank 1 with little improvement, this provides
evidence that query rewriting is unnecessary for this case.