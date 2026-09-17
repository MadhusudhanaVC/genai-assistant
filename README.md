Day 13 — Golden Set & Evaluation Runner

GenAI Engineering Roadmap · Day 13 Documentation

Day 13 focuses on building a representative golden evaluation dataset and a repeatable evaluation runner to measure the end-to-end quality of the RAG pipeline.

📌 Objectives

Create a reviewed golden evaluation dataset containing at least 25 cases.

Cover answerable, unanswerable, ambiguous, multi-document, and adversarial cases.

Define expected source mappings and answerability for each case.

Build a repeatable evaluation runner.

Capture answers, citations, retrieval results, status, latency, versions, configuration, and errors.

Generate timestamped, machine-readable result artifacts without overwriting previous runs.

📁 Project Structure

genai-assistant/
│
├── app/
│   └── ...                         # Existing RAG application
│
├── datasets/
│   ├── day6_retrieval_test_cases.json
│   ├── prompt_test_cases.json
│   └── golden_set.jsonl            # Day 13: 25 evaluation cases
│
├── docs/
│   └── day13_golden_set_review.md  # Day 13: review documentation
│
├── evals/
│   └── run_evals.py                # Day 13: evaluation runner
│
├── prompts/
│   └── grounded_answer.txt
│
├── results/
│   └── eval_runs/                  # Day 13: evaluation artifacts
│       ├── eval_20260916T101937Z.json
│       ├── eval_20260916T140012Z.json
│       └── eval_20260917T082522Z.json
│
├── sample_data/
│   └── day5_documents/             # Approved Day 5 corpus
│       └── DOC001 ... DOC030
│
├── sample_inputs/
├── sample_outputs/
│
├── scripts/
│   └── validate_golden_set.py      # Day 13: dataset validator
│
├── tests/
│   └── ...                         # Existing project tests
│
├── test_citation_validation.py
├── test_grounded_validator.py
├── verify_day8.py
│
├── .env
├── .env.example
├── .gitignore
├── genai.db
├── pytest.ini
├── pyproject.toml
└── README.md

Note: genai.db is the local runtime database and is not a Day 13 deliverable.

Day 13 Components

Component

Location

Purpose

🗂️ Golden Set

datasets/golden_set.jsonl

Stores the 25 evaluation cases

📝 Review Notes

docs/day13_golden_set_review.md

Documents dataset review

▶️ Evaluation Runner

evals/run_evals.py

Runs all golden-set cases

✅ Validator

scripts/validate_golden_set.py

Validates the golden set

📊 Result Artifacts

results/eval_runs/

Stores timestamped evaluation results

1. 🗂️ Golden Evaluation Dataset

Dataset File

datasets/golden_set.jsonl

The golden set contains 25 evaluation cases based on the approved Day 5 document corpus.

Evaluation Case Format

Each case contains:

Field

Description

case_id

Unique evaluation case ID

question

Question being evaluated

category

Evaluation category

expected_source_ids

Expected supporting source IDs

answerability

Expected answerability

Optional expected facts / answer notes

Additional evaluation guidance

Category Distribution

Category

Cases

Answerable

10

Multi-document

5

Ambiguous

4

Unanswerable

3

Adversarial

3

Total

25

Coverage requirement: Every answerable case has at least one expected source ID.

2. ✅ Golden Set Validation

The dataset validator is:

scripts/validate_golden_set.py

Run the Validator

Run from the repository root:

python scripts\validate_golden_set.py

Verified Output

Golden set validation PASSED
Total cases: 25

This verifies the required golden-set structure and category coverage.

3. 📝 Manual Review

The golden set was manually self-reviewed against the approved Day 5 corpus.

Review Checks

Question clarity

Category assignment

Expected source mappings

Answerability classification

Required category coverage

Alignment with the approved corpus

Review Results

Review Item

Result

Cases reviewed

25

Incorrect source mappings

0

Cases requiring correction

0

Corrections made

None

Review type

Manual self-review

No artificial correction was introduced because the review did not identify a genuine source-mapping or answerability defect.

Review Documentation

docs/day13_golden_set_review.md

Review limitation: The roadmap describes independent review by another intern. The team workflow for this task used manual self-review, so this repository does not claim independent peer review.

4. ▶️ Evaluation Runner

The Day 13 evaluation runner is:

evals/run_evals.py

The runner loads all cases from:

datasets/golden_set.jsonl

and executes them against the existing RAG pipeline.

Run the Evaluation

python evals\run_evals.py

Information Recorded

For every evaluation case, the runner records:

Field

Description

Case ID

Unique evaluation case identifier

Question

Question being evaluated

Category

Golden-set category

Expected source IDs

Expected supporting sources

Expected answerability

Expected answerability label

Actual answer

Generated answer

Actual status

Result status

Actual citations

Generated citations

Retrieval results

Retrieved source information

Latency

Case execution time

Model version

LLM model version

Prompt version

Prompt version used

Configuration

Evaluation configuration

Errors

Error information, if any

Execution: All 25 cases were executed without manual intervention.

5. ⚙️ Reproducible Evaluation Configuration

The latest verified evaluation run used:

top_k          : 3
min_score      : None
model_version  : openrouter/free
prompt_version : v1

The configuration is stored in the machine-readable evaluation result under:

configuration

This preserves the configuration and version information used for the evaluation run.

6. 📊 Evaluation Results

Evaluation artifacts are stored in:

results/eval_runs/

Available Evaluation Runs

eval_20260916T101937Z.json
eval_20260916T140012Z.json
eval_20260917T082522Z.json

Latest Verified Run

results/eval_runs/eval_20260917T082522Z.json

The latest run contains:

25 evaluation results

Generated answers

Citations

Retrieval results

Status

Latency

Model version

Prompt version

Evaluation configuration

Errors

Timestamped filenames preserve previous evaluation artifacts and prevent earlier runs from being overwritten.

7. 🔄 Evaluation Flow

┌──────────────────────────────────┐
│ datasets/golden_set.jsonl        │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Load 25 Evaluation Cases         │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Run Existing RAG Pipeline        │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Capture Answer & Citations       │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Capture Retrieval Results        │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Capture Status & Latency         │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Record Model / Prompt / Config   │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Save Timestamped JSON Result     │
└──────────────────────────────────┘

8. 🧪 Day 13 Verification Commands

The following commands are the important Day 13 execution and verification commands. Git commands are intentionally excluded.

8.1 Validate the Golden Set

python scripts\validate_golden_set.py

Expected output:

Golden set validation PASSED
Total cases: 25

8.2 Run the Evaluation

python evals\run_evals.py

Expected output:

Evaluation run completed.
Cases: 25

A new timestamped result file is created under:

results/eval_runs/

8.3 Verify the Latest Evaluation Artifact

python -c "import json; from pathlib import Path; p=Path('results/eval_runs/eval_20260917T082522Z.json'); d=json.loads(p.read_text(encoding='utf-8')); print('Run ID:', d['run_id']); print('Cases:', d['golden_set_cases']); print('Results:', len(d['results'])); print('Configuration:', d['configuration'])"

Verified output:

Run ID: 20260917T082522Z
Cases: 25
Results: 25
Configuration: {'top_k': 3, 'min_score': None, 'model_version': 'openrouter/free', 'prompt_version': 'v1'}

8.4 Run the Full Test Suite

pytest -q

Latest verified result:

28 passed in 271.80s (0:04:31)

8.5 Complete Day 13 Verification Sequence

For a complete Day 13 verification, run:

python scripts\validate_golden_set.py
python evals\run_evals.py
pytest -q

This sequence:

Validates the golden dataset.

Executes all evaluation cases.

Generates a timestamped machine-readable result.

Runs the complete project test suite.

The evaluation runner creates a new timestamped result artifact for each run, so previous evaluation results are preserved.

9. 📦 Day 13 Deliverables

Deliverable

Location

Status

Golden evaluation dataset

datasets/golden_set.jsonl

✅ Complete

Evaluation runner

evals/run_evals.py

✅ Complete

Golden-set validator

scripts/validate_golden_set.py

✅ Complete

Review documentation

docs/day13_golden_set_review.md

✅ Complete

Machine-readable evaluation results

results/eval_runs/

✅ Complete

10. ✅ Day 13 Completion Checklist

Dataset

Evaluation case format defined

25 golden-set cases created

Answerable cases included

Unanswerable cases included

Ambiguous cases included

Multi-document cases included

Adversarial cases included

Approved Day 5 corpus used

Every answerable case has an expected source

Review

Golden set manually self-reviewed

Review documentation completed

No incorrect source mappings identified

No cases required correction

Evaluation Runner

Evaluation runner implemented

All 25 cases executed

No manual intervention required

Answers recorded

Citations recorded

Retrieval results recorded

Status recorded

Latency recorded

Model version recorded

Prompt version recorded

Configuration recorded

Errors recorded

Results & Verification

Golden-set validation passed

Timestamped machine-readable result generated

Previous evaluation artifacts preserved

Full project test suite passed

11. 📋 Final Verification Summary

Metric

Result

Golden-set cases

25

Answerable

10

Multi-document

5

Ambiguous

4

Unanswerable

3

Adversarial

3

Cases executed

25/25

Golden-set validation

PASSED

Full test suite

28/28 PASSED

Latest evaluation run

eval_20260917T082522Z.json

Model version

openrouter/free

Prompt version

v1

Top-K

3

🎯 Day 13 Status: ✅ COMPLETE

Golden set created • Reviewed • Validated • Evaluate
