GenAI Assistant — Day 9

Retrieval Diagnosis, Failure Analysis & Controlled Experiments

Day 9 focuses on diagnosing retrieval weaknesses in the existing RAG pipeline and designing controlled, measurable experiments to understand why retrieval succeeds or fails.

The goal is to use the weakest baseline questions to identify retrieval problems, classify their likely causes, and test one retrieval variable at a time without changing multiple factors simultaneously.

🎯 Day 9 Objective

Build a retrieval-diagnosis and controlled-experiment workflow that:

Freezes the current retrieval configuration before experimentation.

Uses the existing Day 6 retrieval evaluation dataset.

Measures baseline retrieval performance using Hit@1, Hit@3, and MRR.

Identifies the five weakest diagnostic questions.

Records the expected source document for every diagnostic question.

Analyzes the retrieved evidence for each question.

Classifies the observed retrieval behavior.

Defines a root-cause hypothesis for each weak question.

Creates controlled experiments that change only one primary variable.

Runs query-rewriting and Top-K experiments.

Records per-question experiment results.

Compares experiment results against the frozen baseline.

Uses measured retrieval evidence to support or reject hypotheses.

🔄 Day 9 Retrieval Diagnosis Flow

Fixed Evaluation Dataset

        ↓

Frozen Baseline Configuration

        ↓

Baseline Retrieval

        ↓

Per-Question Metrics

        ↓

Identify Weak / Diagnostic Questions

        ↓

Inspect Retrieved Evidence

        ↓

Failure Classification

        ↓

Root-Cause Hypothesis

        ↓

Controlled Experiment

        ↓

Change ONE Variable

        ↓

Measure Retrieval Again

        ↓

Compare With Baseline

        ↓

Support / Reject Hypothesis

🧊 Frozen Baseline Configuration

Before running controlled experiments, the existing retrieval configuration was recorded and frozen.

The frozen configuration is stored in:

results/day9_baseline_config.json

Baseline configuration:

Embedding model: all-MiniLM-L6-v2

Embedding normalization: True

Embedding dimension: 384

Chunk size: 500

Chunk overlap: 80

Top-K: 3

Minimum score: None

Metadata filter: None

Collection name: day6_chunks

Chroma path: results/chroma_db

Evaluation dataset:

datasets/day6_retrieval_test_cases.json

The grounded prompt version is also recorded:

prompts/grounded_answer.txt

Prompt version:

current Day 8 grounded-answer template

Freezing these values ensures that later experiments can be compared fairly against the same baseline.

📊 Baseline Retrieval Measurement

The baseline retrieval measurement is implemented in:

scripts/day9_baseline.py

The script uses the fixed Day 6 retrieval evaluation dataset and runs every question using the frozen retrieval configuration.

The baseline measures:

Hit@1

Hit@3

Reciprocal Rank

Mean Reciprocal Rank (MRR)

The script also records the complete retrieved results for every question, including:

Document ID

Chunk ID

Similarity score

Title

Source path

Expected document rank

This makes the baseline reproducible and allows individual retrieval behavior to be inspected rather than relying only on an overall average.

▶️ Run Baseline Measurement

Run:

python.exe scripts/day9_baseline.py

Baseline results are saved to:

results/day9_baseline_metrics.json

📈 Baseline Results

The fixed evaluation dataset contains 10 questions.

Baseline metrics:

Hit@1: 0.90

Hit@3: 1.00

MRR: 0.95

Interpretation:

9 out of 10 expected documents were ranked first.

All 10 expected documents were retrieved within the top 3 results.

The only Hit@1 failure was the machine-learning question, where the expected document appeared at rank 2.

The baseline is therefore strong overall, but the ranking differences provide useful diagnostic cases for controlled experimentation.

🔎 Five Diagnostic Questions

Day 9 uses five diagnostic questions selected from the fixed retrieval evaluation set.

The selection considers:

Expected-document rank.

Reciprocal rank.

Similarity-score margin against competing documents.

Semantic competition.

Top-K utilization.

Document/chunk diversity.

These are diagnostic cases rather than five complete retrieval failures.

The five selected questions are:

Q10 — What is machine learning?

Expected document:

DOC019

Q7 — What is a Git branch?

Expected document:

DOC008

Q4 — What is a Python module?

Expected document:

DOC004

Q8 — What causes a Git merge conflict?

Expected document:

DOC009

Q1 — What is a Python variable?

Expected document:

DOC001

🔬 Failure Classification

Each diagnostic question is classified using the actual retrieved evidence.

The purpose of classification is to create a measurable root-cause hypothesis rather than simply guessing why retrieval behaved a certain way.

Possible diagnostic categories include:

Poor chunk boundary

Vocabulary mismatch

Broad query

Missing metadata

Low ranking

Semantic competition

Same-document chunk concentration

Excessive context

For Day 9, the observed cases were primarily related to semantic competition, broad queries, ranking margin, and Top-K document diversity.

❓ Q10 — What is machine learning?

Expected source:

DOC019

Retrieved evidence:

1. DOC020 — score 0.7128
2. DOC019 — score 0.7100
3. DOC029 — score 0.4918

Observed result:

The expected document DOC019 was retrieved at rank 2.

Hit@1: False

Hit@3: True

Reciprocal Rank: 0.5

Failure classification:

Low ranking / semantic ambiguity.

Root-cause hypothesis:

The query is broad and semantically close to both the machine-learning document and the artificial-intelligence document.

DOC020 narrowly outranks DOC019.

Score margin:

0.7128 - 0.7100 = 0.0028

Proposed experiment:

Change only the query wording.

Confirmation measurement:

Expected document rank

Hit@1

Hit@3

MRR

Score margin between DOC019 and DOC020

The hypothesis is supported if a controlled query rewrite moves DOC019 to rank 1 without changing the retrieval configuration.

❓ Q7 — What is a Git branch?

Expected source:

DOC008

Retrieved evidence:

1. DOC008 — score 0.7093
2. DOC007 — score 0.7050
3. DOC010 — score 0.5691

Observed result:

The expected document is ranked first, but DOC007 is an extremely close semantic competitor.

Score margin:

0.7093 - 0.7050 = 0.0043

Failure classification:

Low ranking margin / semantic competition.

Root-cause hypothesis:

The query contains the broad Git concept together with the specific branch concept.

The general Git document therefore competes closely with the dedicated Git Branches document.

Proposed experiment:

Change only the query wording.

Confirmation measurement:

Expected document rank

Hit@1

Hit@3

MRR

Score margin against DOC007

The hypothesis is supported if the rewritten query increases the separation between DOC008 and DOC007.

❓ Q4 — What is a Python module?

Expected source:

DOC004

Retrieved evidence:

1. DOC004 — score 0.7786
2. DOC001 — score 0.6512
3. DOC006 — score 0.5266

Observed result:

The expected document is correctly ranked first.

Failure classification:

Broad query / semantic competition.

Root-cause hypothesis:

The query is short and generic.

Other Python-related documents receive meaningful similarity scores, although the intended module document remains clearly ahead.

Proposed experiment:

Change only the query wording.

Confirmation measurement:

Expected document rank

Hit@1

Hit@3

MRR

Score margin against DOC001

This acts as a diagnostic control for whether query rewriting provides additional separation when retrieval is already successful.

❓ Q8 — What causes a Git merge conflict?

Expected source:

DOC009

Retrieved evidence:

1. DOC009_CHUNK_001 — score 0.7784
2. DOC009_CHUNK_002 — score 0.6296
3. DOC012_CHUNK_002 — score 0.4453

Observed result:

The expected document is ranked first.

However, two of the three retrieved positions belong to DOC009.

Failure classification:

Same-document chunk concentration / Top-K utilization.

Root-cause hypothesis:

The query strongly matches multiple chunks from the same document.

This can reduce document diversity within the Top-K result set.

Proposed experiment:

Change only Top-K.

Confirmation measurement:

Hit@1

Hit@3

MRR

Number of unique documents retrieved

Number of chunks per document

The hypothesis is supported or rejected based on whether changing Top-K produces useful additional evidence or merely retrieves more chunks from the same document.

❓ Q1 — What is a Python variable?

Expected source:

DOC001

Retrieved evidence:

1. DOC001 — score 0.8288
2. DOC002 — score 0.5284
3. DOC004 — score 0.5112

Observed result:

The expected document is correctly ranked first.

Failure classification:

Broad query / related-document competition.

Root-cause hypothesis:

The query is short and general, so other Python documents also receive non-trivial similarity scores.

However, DOC001 has a strong lead.

Proposed experiment:

Change only the query wording.

Confirmation measurement:

Expected document rank

Hit@1

Hit@3

MRR

Score margin against the strongest competing document

If the result remains rank 1 with little improvement, this provides evidence that query rewriting is unnecessary for this case.

🧪 Controlled Experiment Design

The controlled experiment runner is implemented in:

scripts/day9_experiment.py

Each experiment starts from the frozen baseline configuration.

Only one primary retrieval variable is changed.

All other baseline parameters remain unchanged.

Frozen parameters:

Embedding model: all-MiniLM-L6-v2

Chunk size: 500

Chunk overlap: 80

Top-K: 3

Minimum score: None

Metadata filter: None

The experiment runner records:

Experiment ID

Question number

Variable changed

Hypothesis

Baseline configuration

Experiment configuration

Expected document

Expected rank

Hit@1

Hit@3

Reciprocal Rank

Similarity scores

Score margin

Retrieved documents

Unique document count

Chunks per document

This makes each experiment independently measurable and reproducible.

📋 Experiment Matrix

The experiment plan is stored in:

results/day9_experiment_matrix.md

The five controlled experiments are:

E01 — Q10

Variable changed:

Query wording

Change:

Rewrite the machine-learning query to make the intent more explicit.

Expected result:

DOC019 moves from rank 2 to rank 1.

E02 — Q7

Variable changed:

Query wording

Change:

Make branch intent more explicit.

Expected result:

DOC008 separates further from DOC007.

E03 — Q4

Variable changed:

Query wording

Change:

Make Python module intent more explicit.

Expected result:

DOC004 remains rank 1 with stronger separation.

E04 — Q8

Variable changed:

Top-K

Change:

Increase Top-K from 3 to 5.

Expected result:

Determine whether additional useful evidence appears.

E05 — Q1

Variable changed:

Query wording

Change:

Make variable intent more explicit.

Expected result:

Determine whether semantic separation improves.

🧪 Experiment E01 — Machine Learning

Baseline query:

What is machine learning?

Experiment query:

What is machine learning and how is it defined?

Baseline:

Expected document: DOC019

Rank: 2

Hit@1: False

Hit@3: True

MRR: 0.5

Experiment:

Expected document: DOC019

Rank: 2

Hit@1: False

Hit@3: True

MRR: 0.5

Experiment score comparison:

Expected score: 0.6663

Competitor: DOC020

Competitor score: 0.6696

Score margin: -0.0033

Result:

The expected document remained at rank 2.

The query rewrite did not improve the ranking.

Conclusion:

E01 is rejected.

The tested query rewrite did not resolve the ranking competition between DOC019 and DOC020.

🧪 Experiment E02 — Git Branch

Baseline query:

What is a Git branch?

Experiment query:

What is a Git branch and how is it used for separate lines of development?

Baseline:

Expected document: DOC008

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment:

Expected document: DOC008

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment score comparison:

Expected score: 0.7281

Competitor: DOC007

Competitor score: 0.6683

Score margin: 0.0598

Result:

DOC008 remained at rank 1.

The rewritten query produced a strong separation from DOC007.

Conclusion:

E02 supports the hypothesis that more explicit branch-focused wording can improve semantic separation.

🧪 Experiment E03 — Python Module

Baseline query:

What is a Python module?

Experiment query:

What is a Python module and how is it used to organize Python code?

Baseline:

Expected document: DOC004

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment:

Expected document: DOC004

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment score comparison:

Expected score: 0.7365

Competitor: DOC001

Competitor score: 0.5970

Score margin: 0.1395

Result:

DOC004 remained at rank 1.

The rewritten query produced a clear separation from the competing Python document.

Conclusion:

E03 supports the hypothesis that explicit module-focused wording can improve semantic separation.

🧪 Experiment E04 — Git Merge Conflict

Baseline:

Query:

What causes a Git merge conflict?

Top-K: 3

Expected document: DOC009

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment:

Top-K: 5

Expected document: DOC009

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Retrieved documents:

Rank 1: DOC009_CHUNK_001

Rank 2: DOC009_CHUNK_002

Rank 3: DOC012_CHUNK_002

Rank 4: DOC010_CHUNK_001

Rank 5: DOC007_CHUNK_001

Unique documents:

4

Expected score:

0.7784

Competitor score:

0.4453

Score margin:

0.3331

Result:

The expected document remained rank 1.

Increasing Top-K from 3 to 5 introduced additional retrieved evidence and increased the number of unique documents from the baseline set.

Conclusion:

E04 supports the diagnostic purpose of testing Top-K for additional evidence coverage.

The experiment also confirms that the first two retrieved chunks still belong to DOC009, so increasing Top-K does not eliminate same-document concentration.

🧪 Experiment E05 — Python Variable

Baseline query:

What is a Python variable?

Experiment query:

What is a Python variable and what does it store?

Baseline:

Expected document: DOC001

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment:

Expected document: DOC001

Rank: 1

Hit@1: True

Hit@3: True

MRR: 1.0

Experiment score comparison:

Expected score: 0.7820

Competitor: DOC004

Competitor score: 0.4990

Score margin: 0.2830

Result:

The expected document remained at rank 1.

The experiment did not improve the ranking position.

The expected document already had a strong lead.

Conclusion:

E05 is rejected as an improvement experiment.

The baseline was already successful, and the query rewrite did not provide a meaningful retrieval improvement.

This provides evidence that query rewriting is unnecessary for this case.

📊 Day 9 Experiment Results

Final experiment outcomes:

E01 — Query rewriting for machine learning

Result: REJECTED

DOC019 remained rank 2.

E02 — Query rewriting for Git branch

Result: SUPPORTED

DOC008 remained rank 1 and showed stronger separation from DOC007.

E03 — Query rewriting for Python module

Result: SUPPORTED

DOC004 remained rank 1 with clear separation from competing Python documents.

E04 — Top-K increase

Result: SUPPORTED FOR DIAGNOSTIC COVERAGE

Increasing Top-K from 3 to 5 exposed additional evidence and increased retrieved document diversity.

E05 — Query rewriting for Python variable

Result: REJECTED

DOC001 was already rank 1 and the rewrite did not provide a meaningful improvement.

Detailed experiment results are stored in:

results/day9_experiment_results.md

Individual experiment results are stored in:

results/day9_experiments/

Files:

e01_result.json

e02_result.json

e03_result.json

e04_result.json

e05_result.json

📏 Day 9 Metrics

The primary retrieval metrics are:

Hit@1

Measures whether the expected source document appears at rank 1.

Hit@3

Measures whether the expected source document appears within the top 3 results.

Reciprocal Rank

Calculated as:

1 / rank

If the expected document is not retrieved, the reciprocal rank is:

0

Mean Reciprocal Rank (MRR)

MRR is the average reciprocal rank across all evaluation questions.

These metrics allow ranking quality to be measured numerically rather than judged only by visual inspection.

🧠 Why One Variable at a Time?

Controlled experiments are important because changing multiple retrieval parameters simultaneously makes it impossible to determine which change caused the result.

For example, changing:

Chunk size

and

Top-K

at the same time

would not allow us to determine whether the improvement came from chunking or retrieval depth.

Therefore every Day 9 experiment changes exactly one primary variable.

This makes the experiment results interpretable and reproducible.

🔁 Reproducibility

The Day 9 baseline can be rerun using:

python.exe scripts/day9_baseline.py

The controlled experiments can be rerun using:

python.exe -m scripts.day9_experiment E01

python.exe -m scripts.day9_experiment E02

python.exe -m scripts.day9_experiment E03

python.exe -m scripts.day9_experiment E04

python.exe -m scripts.day9_experiment E05

The fixed dataset and frozen configuration ensure that results can be compared consistently.

📁 Day 9 Project Structure

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
│       ├── chunking.py
│       ├── ingest.py
│       └── ...
│
├── datasets/
│   └── day6_retrieval_test_cases.json
│
├── prompts/
│   └── grounded_answer.txt
│
├── results/
│   ├── chroma_db/
│   │
│   ├── chunks.jsonl
│   ├── chunk_quality_review.md
│   ├── day6_retrieval_report.json
│   │
│   ├── day9_baseline_config.json
│   ├── day9_baseline_metrics.json
│   ├── day9_failure_analysis.md
│   ├── day9_experiment_matrix.md
│   ├── day9_experiment_results.md
│   │
│   └── day9_experiments/
│       ├── e01_result.json
│       ├── e02_result.json
│       ├── e03_result.json
│       ├── e04_result.json
│       └── e05_result.json
│
├── scripts/
│   ├── day9_baseline.py
│   ├── day9_experiment.py
│   └── ...
│
├── tests/
│   ├── test_chunking.py
│   ├── test_document_validation.py
│   ├── test_rag_pipeline.py
│   ├── test_grounded_generation.py
│   └── ...
│
├── test_citation_validation.py
├── test_grounded_validator.py
├── verify_day8.py
│
├── .env.example
├── README.md
└── requirements.txt