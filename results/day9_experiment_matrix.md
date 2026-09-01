# Day 9 — Controlled Experiment Matrix

## Experiment Rule

Each experiment changes exactly one primary retrieval variable.

All other baseline parameters remain frozen:

- Embedding model: all-MiniLM-L6-v2
- Chunk size: 500
- Chunk overlap: 80
- Top-K: 3
- Minimum score: None
- Metadata filter: None

---

| Experiment | Question | Baseline | Single Variable | Proposed Change | Expected Result | Measurement |
|---|---|---|---|---|---|---|
| E01 | Q10 | Original query | Query wording | Rewrite query to distinguish machine learning from AI | DOC019 moves from rank 2 to rank 1 | Hit@1, Hit@3, MRR, rank, score margin |
| E02 | Q7 | Original query | Query wording | Make branch intent more explicit | DOC008 separates further from DOC007 | Hit@1, Hit@3, MRR, score margin |
| E03 | Q4 | Original query | Query wording | Make Python module intent more explicit | DOC004 remains rank 1 with stronger separation | Hit@1, MRR, score margin |
| E04 | Q8 | Top-K = 3 | Top-K | Test a larger Top-K while keeping all other settings fixed | Determine whether additional useful evidence appears | Hit@1, Hit@3, MRR, unique-document count |
| E05 | Q1 | Original query | Query wording | Make variable intent more explicit | Determine whether semantic separation improves | Hit@1, MRR, score margin |

---

## Experiment Control

For every experiment:

1. Start from the frozen baseline.
2. Change only the listed primary variable.
3. Run the same fixed evaluation set.
4. Record per-question retrieval results.
5. Calculate Hit@1, Hit@3, and MRR.
6. Compare against the frozen baseline.
7. Accept or reject the hypothesis based on measured evidence.

## Baseline Reference

Hit@1: 0.90

Hit@3: 1.00

MRR: 0.95

## Important Constraint

No experiment may simultaneously change:

- chunk size and overlap
- Top-K and score threshold
- query wording and metadata filter
- embedding model and chunking

A result is considered interpretable only when one primary variable
has changed.