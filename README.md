# GenAI Assistant: Day 13 - Golden Set & Evaluation Runner

> Building a representative golden evaluation dataset and a repeatable evaluation runner to measure end-to-end RAG pipeline quality.

## Overview

Day 13 establishes the foundation for continuous evaluation of the RAG (Retrieval-Augmented Generation) pipeline. This includes a curated dataset of 25 evaluation cases covering diverse scenarios (answerable, unanswerable, ambiguous, multi-document, and adversarial) and an automated evaluation runner that captures comprehensive metrics for each execution.

---

## 🎯 Objectives

- ✅ Create a reviewed golden evaluation dataset with **25 comprehensive cases**
- ✅ Cover diverse question types and edge cases
- ✅ Define expected source mappings and answerability for each case
- ✅ Build a repeatable evaluation runner with full observability
- ✅ Capture answers, citations, retrieval results, status, latency, versions, and configuration
- ✅ Generate timestamped, machine-readable result artifacts
- ✅ Prevent overwriting of previous evaluation runs

---

## 📁 Project Structure

```
genai-assistant/
│
├── app/
│   └── ...                              # Existing RAG application
│
├── datasets/
│   ├── day6_retrieval_test_cases.json
│   ├── prompt_test_cases.json
│   └── golden_set.jsonl                 # 25 evaluation cases
│
├── docs/
│   └── day13_golden_set_review.md       # Review documentation
│
├── evals/
│   └── run_evals.py                     # Evaluation runner
│
├── prompts/
│   └── grounded_answer.txt
│
├── results/
│   └── eval_runs/                       # Timestamped evaluation artifacts
│       ├── eval_20260916T101937Z.json
│       ├── eval_20260916T140012Z.json
│       └── eval_20260917T082522Z.json
│
├── sample_data/
│   └── day5_documents/                  # Approved corpus (DOC001–DOC030)
│
├── sample_inputs/
├── sample_outputs/
│
├── scripts/
│   └── validate_golden_set.py           # Dataset validator
│
├── tests/
│   └── ...                              # Project tests
│
├── .env
├── .env.example
├── .gitignore
├── genai.db                             # Local runtime database
├── pytest.ini
├── pyproject.toml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Dependencies installed (`pyproject.toml`)
- Environment variables configured (`.env`)

### Run Complete Day 13 Verification

Execute the full verification sequence from the repository root:

```bash
python scripts/validate_golden_set.py
python evals/run_evals.py
pytest -q
```

This will:
1. Validate the golden dataset structure
2. Execute all 25 evaluation cases
3. Generate a timestamped machine-readable result
4. Run the complete project test suite

---

## 📊 Golden Evaluation Dataset

### Location
```
datasets/golden_set.jsonl
```

### Coverage

| Category | Cases | Coverage |
|----------|-------|----------|
| Answerable | 10 | 40% |
| Multi-document | 5 | 20% |
| Ambiguous | 4 | 16% |
| Unanswerable | 3 | 12% |
| Adversarial | 3 | 12% |
| **Total** | **25** | **100%** |

### Evaluation Case Format

Each case contains:

| Field | Description |
|-------|-------------|
| `case_id` | Unique evaluation case ID |
| `question` | Question being evaluated |
| `category` | Evaluation category (from coverage table above) |
| `expected_source_ids` | Expected supporting source document IDs |
| `answerability` | Expected answerability classification |
| `notes` | Optional additional evaluation guidance |

**Requirement:** Every answerable case has at least one expected source ID.

---

## ✅ Golden Set Validation

### Run the Validator

```bash
python scripts/validate_golden_set.py
```

### Expected Output

```
Golden set validation PASSED
Total cases: 25
```

### Validation Checks

- ✅ Golden-set structure compliance
- ✅ Required field presence
- ✅ Category coverage requirements
- ✅ Expected source mapping validity

---

## 📝 Manual Review

The golden set was manually self-reviewed against the approved Day 5 corpus.

| Review Item | Result |
|-------------|--------|
| Cases reviewed | 25 |
| Incorrect source mappings | 0 |
| Cases requiring correction | 0 |
| Review type | Manual self-review |

**Documentation:** See `docs/day13_golden_set_review.md`

---

## ▶️ Evaluation Runner

### Location
```
evals/run_evals.py
```

### Execute All Cases

```bash
python evals/run_evals.py
```

### Output

```
Evaluation run completed.
Cases: 25
```

A new timestamped result file is created under `results/eval_runs/`

### Captured Information

For every evaluation case, the runner records:

| Field | Description |
|-------|-------------|
| Case ID | Unique evaluation case identifier |
| Question | Question being evaluated |
| Category | Golden-set category |
| Expected source IDs | Expected supporting sources |
| Expected answerability | Expected answerability label |
| Actual answer | Generated answer from RAG pipeline |
| Actual status | Result status code |
| Actual citations | Generated citations |
| Retrieval results | Retrieved source information |
| Latency | Case execution time (ms) |
| Model version | LLM model version used |
| Prompt version | Prompt template version |
| Configuration | Evaluation configuration (top_k, min_score, etc.) |
| Errors | Error information, if any |

---

## ⚙️ Reproducible Evaluation Configuration

### Latest Verified Run

```json
{
  "top_k": 3,
  "min_score": null,
  "model_version": "openrouter/free",
  "prompt_version": "v1"
}
```

Configuration and version information are stored in the machine-readable evaluation result under the `configuration` field.

---

## 📊 Evaluation Results

### Location
```
results/eval_runs/
```

### Available Runs

- `eval_20260916T101937Z.json`
- `eval_20260916T140012Z.json`
- `eval_20260917T082522Z.json` (Latest)

### Result Structure

Each evaluation run contains:

- 25 evaluation results
- Generated answers and citations
- Retrieval results with scores
- Status and latency metrics
- Model, prompt, and configuration versions
- Error logs for failed cases

**Note:** Timestamped filenames preserve previous runs and prevent data loss.

---

## 🔄 Evaluation Flow

```
┌──────────────────────────────────┐
│ datasets/golden_set.jsonl        │ Load 25 evaluation cases
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Run Existing RAG Pipeline        │ Execute pipeline for each case
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Capture Answer & Citations       │ Extract generated results
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Capture Retrieval Results        │ Log retrieved sources
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Capture Status & Latency         │ Record execution metrics
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Record Model / Prompt / Config   │ Preserve version info
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Save Timestamped JSON Result     │ Store results/eval_runs/
└──────────────────────────────────┘
```

---

## 🧪 Verification Commands

### 1. Validate the Golden Set

```bash
python scripts/validate_golden_set.py
```

**Expected output:**
```
Golden set validation PASSED
Total cases: 25
```

---

### 2. Run the Evaluation

```bash
python evals/run_evals.py
```

**Expected output:**
```
Evaluation run completed.
Cases: 25
```

A new timestamped result file is created under `results/eval_runs/`

---

### 3. Verify the Latest Evaluation Artifact

```bash
python -c "import json; from pathlib import Path; p=Path('results/eval_runs/eval_20260917T082522Z.json'); d=json.loads(p.read_text(encoding='utf-8')); print('Run ID:', d['run_id']); print('Cases:', d['golden_set_cases']); print('Results:', len(d['results'])); print('Configuration:', d['configuration'])"
```

**Expected output:**
```
Run ID: 20260917T082522Z
Cases: 25
Results: 25
Configuration: {'top_k': 3, 'min_score': None, 'model_version': 'openrouter/free', 'prompt_version': 'v1'}
```

---

### 4. Run the Full Test Suite

```bash
pytest -q
```

**Expected output:**
```
28 passed in 271.80s (0:04:31)
```

---

### 5. Complete Day 13 Verification Sequence

For comprehensive Day 13 verification:

```bash
python scripts/validate_golden_set.py
python evals/run_evals.py
pytest -q
```

This sequence:
- ✅ Validates the golden dataset
- ✅ Executes all evaluation cases
- ✅ Generates a timestamped machine-readable result
- ✅ Runs the complete project test suite

---

## 📦 Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| Golden evaluation dataset | `datasets/golden_set.jsonl` | ✅ Complete |
| Evaluation runner | `evals/run_evals.py` | ✅ Complete |
| Golden-set validator | `scripts/validate_golden_set.py` | ✅ Complete |
| Review documentation | `docs/day13_golden_set_review.md` | ✅ Complete |
| Machine-readable evaluation results | `results/eval_runs/` | ✅ Complete |

---

## ✅ Completion Checklist

### Dataset
- ✅ Evaluation case format defined
- ✅ 25 golden-set cases created
- ✅ Answerable cases included
- ✅ Unanswerable cases included
- ✅ Ambiguous cases included
- ✅ Multi-document cases included
- ✅ Adversarial cases included
- ✅ Approved Day 5 corpus used
- ✅ Every answerable case has expected source(s)

### Review
- ✅ Golden set manually self-reviewed
- ✅ Review documentation completed
- ✅ No incorrect source mappings identified
- ✅ No cases required correction

### Evaluation Runner
- ✅ Evaluation runner implemented
- ✅ All 25 cases executed
- ✅ No manual intervention required
- ✅ Answers recorded
- ✅ Citations recorded
- ✅ Retrieval results recorded
- ✅ Status recorded
- ✅ Latency recorded
- ✅ Model version recorded
- ✅ Prompt version recorded
- ✅ Configuration recorded
- ✅ Errors recorded

### Results & Verification
- ✅ Golden-set validation passed
- ✅ Timestamped machine-readable result generated
- ✅ Previous evaluation artifacts preserved
- ✅ Full project test suite passed

---

## 📈 Final Verification Summary

| Metric | Result |
|--------|--------|
| Golden-set cases | 25 |
| Answerable | 10 |
| Multi-document | 5 |
| Ambiguous | 4 |
| Unanswerable | 3 |
| Adversarial | 3 |
| Cases executed | 25/25 |
| Golden-set validation | ✅ PASSED |
| Full test suite | ✅ 28/28 PASSED |
| Latest evaluation run | `eval_20260917T082522Z.json` |
| Model version | `openrouter/free` |
| Prompt version | `v1` |
| Top-K retrieval | 3 |

---

## 🎯 Status: ✅ COMPLETE

✅ Golden set created
✅ Reviewed and validated
✅ Evaluation runner implemented
✅ All cases executed
✅ Results generated and preserved
✅ Full test suite passing

---

## 📚 Additional Resources

- **Review Documentation:** `docs/day13_golden_set_review.md`
- **Latest Results:** `results/eval_runs/eval_20260917T082522Z.json`
- **Source Corpus:** `sample_data/day5_documents/`
- **Test Suite:** `pytest.ini` and `tests/`

---

## 📞 Support

For questions or issues:
1. Review the verification commands above
2. Check the review documentation in `docs/day13_golden_set_review.md`
3. Inspect the latest evaluation artifact in `results/eval_runs/`
4. Run the validator: `python scripts/validate_golden_set.py`

---

**Last Updated:** September 17, 2026
**Project:** GenAI Engineering Roadmap
**Day:** 13
