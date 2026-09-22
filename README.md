# Day 14 — Graders, Scorecard & Regression Checks

GenAI Engineering Roadmap · Day 14 Documentation

Day 14 focuses on separating retrieval quality from answer quality and building an automated quality gate for the RAG pipeline.

The implementation adds retrieval graders, answer graders, a review-friendly evaluation report, an automated scorecard, regression thresholds, and a one-command regression check.

## 📌 Practical Goal

Separate retrieval quality from answer quality and produce a scorecard that guides the next improvement.

## 1. 🎯 Day 14 Objectives

The Day 14 implementation covers the following roadmap requirements:

- Implement retrieval graders.
- Measure expected-source retrieval using Hit Rate, Recall@K, and MRR.
- Implement answer-quality checks.
- Check answerability status.
- Check citation presence and citation validity.
- Check required facts where available.
- Check correct abstention for unsupported questions.
- Generate review-friendly per-case evaluation output.
- Generate an automated quality scorecard.
- Identify common failure categories.
- Track latency and a cost proxy.
- Define regression thresholds.
- Return a failing process status when a critical threshold is broken.

## 2. 📁 Day 14 Project Structure

```
genai-assistant/
│
├── app/
│   └── ...                         # Existing RAG application
│
├── datasets/
│   └── golden_set.jsonl            # 25-case Day 13 evaluation dataset
│
├── docs/
│   └── day13_golden_set_review.md  # Day 13 review documentation
│
├── evals/
│   ├── answer_grader.py            # Day 14 answer-quality graders
│   ├── check_regression.py         # Day 14 regression quality gate
│   ├── generate_eval_report.py     # Day 14 per-case report generator
│   ├── generate_scorecard.py       # Day 14 automated scorecard generator
│   ├── regression_thresholds.json  # Day 14 minimum quality thresholds
│   ├── retrieval_grader.py         # Day 14 retrieval graders
│   └── run_evals.py                # Evaluation runner
│
├── results/
│   ├── eval_runs/                  # Timestamped evaluation results
│   ├── eval_reports/               # Day 14 per-case evaluation reports
│   └── scorecards/                 # Day 14 scorecard artifacts
│
├── prompts/
│   └── grounded_answer.txt
│
├── tests/
│   └── ...
│
├── scripts/
│   └── ...
│
├── .env.example
├── genai.db
├── pyproject.toml
└── README.md
```

check_regression_backup.py is a local backup of the regression checker and is not a required Day 14 deliverable.

## 3. 🧩 Day 14 Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Retrieval Grader | evals/retrieval_grader.py | Measures expected-source retrieval quality |
| Answer Grader | evals/answer_grader.py | Measures answerability, citations, facts, and abstention |
| Evaluation Runner | evals/run_evals.py | Executes the golden-set evaluation |
| Evaluation Report Generator | evals/generate_eval_report.py | Creates per-case review output |
| Scorecard Generator | evals/generate_scorecard.py | Creates the automated quality scorecard |
| Regression Thresholds | evals/regression_thresholds.json | Defines minimum acceptable quality |
| Regression Checker | evals/check_regression.py | Enforces quality thresholds with PASS/FAIL status |
| Evaluation Runs | results/eval_runs/ | Stores timestamped evaluation results |
| Evaluation Reports | results/eval_reports/ | Stores review-friendly reports |
| Scorecards | results/scorecards/ | Stores timestamped scorecards |

## 4. 🔎 Retrieval Graders

The retrieval grader is implemented in:

`evals/retrieval_grader.py`

It evaluates whether expected source documents appear in the retrieved top-k results.

### Retrieval Metrics

#### Hit Rate

Checks whether at least one expected source appears in the retrieved results.

```
Hit Rate = 1 when at least one expected source is retrieved
           0 otherwise
```

#### Recall@K

Measures how many of the expected source documents were retrieved within the evaluated top-k results.

```
Recall@K = retrieved expected sources / total expected sources
```

#### Mean Reciprocal Rank (MRR)

Measures the reciprocal rank of the first retrieved expected source.

```
MRR = 1 / rank of the first relevant result
```

If no expected source is retrieved, the MRR is 0.0.

### Retrieval Grader Output

Each graded case includes:

- hit_rate
- recall_at_k
- mrr
- passed

A retrieval case passes when at least one expected source is retrieved.

## 5. 📝 Answer Graders

The answer grader is implemented in:

`evals/answer_grader.py`

It separates answer quality from retrieval quality.

### 5.1 Answerability Check

Expected and actual answerability are compared using the evaluation case definition.

Supported statuses include:

- answered
- insufficient_evidence

For ambiguous cases, both an answered response and an insufficient-evidence response can be accepted according to the evaluation logic.

### 5.2 Citation Presence

The grader checks whether citations are present when an answer is returned.

For an answered response:

- At least one citation is required.

For an insufficient_evidence response:

- No citations are expected.

### 5.3 Citation Validity

Citation references are checked against the retrieved source information and expected citation structure.

The baseline evaluation recorded:

- Checked citations : 27
- Valid citations   : 27
- Correctness       : 1.0

### 5.4 Required Facts

Where expected facts are available, the grader checks whether the required fact text is present in the generated answer.

Cases without expected facts are not forced through a required-facts check.

The required-facts logic was also tested against a negative example to prevent unrelated text from being treated as a valid required fact.

### 5.5 Unsupported-Question Abstention

Unsupported questions must correctly use the insufficient-evidence path rather than producing an unsupported answer.

The baseline achieved:

- Correct abstentions : 3 / 3
- Abstention accuracy : 1.0

## 6. 📊 Review-Friendly Evaluation Report

The per-case report generator is:

`evals/generate_eval_report.py`

It produces a review-friendly report containing:

| Field | Description |
|-------|-------------|
| Case | Evaluation case ID |
| Retrieval | Retrieval pass/fail result |
| Answer | Answer-quality pass/fail result |
| Latency | Case execution latency |
| Failure Category | Primary failure category |
| Details | Additional per-case grading information |

### Final Baseline Report

The report was generated from the valid baseline evaluation run:

`results/eval_runs/eval_20260922T065158Z.json`

Generated report:

`results/eval_reports/report_20260922T114940Z.md`

The report contains results for all:

- 25 cases

## 7. 📈 Automated Scorecard

The scorecard generator is:

`evals/generate_scorecard.py`

It summarizes the evaluation run into a machine-readable quality scorecard.

### Scorecard Metrics

The scorecard contains:

- Total cases
- Answer grading pass rate
- Retrieval pass rate
- Hit Rate
- Recall@K
- MRR
- Citation correctness
- Answerability accuracy
- Abstention accuracy
- Average latency
- Maximum latency
- Failure categories
- Top three failure categories
- Component-level quality metrics
- Weakest component
- LLM-call cost proxy

## 8. 🏁 Baseline Evaluation Scorecard

The valid Day 14 baseline scorecard is:

`results/scorecards/scorecard_20260922T065158Z.json`

### Baseline Summary

| Metric | Baseline Result |
|--------|-----------------|
| Total cases | 25 |
| Answer pass rate | 0.8000 (80.00%) |
| Retrieval pass rate | 0.8750 (87.50%) |
| Retrieval Hit Rate | 0.8750 (87.50%) |
| Recall@K | 0.8611 (86.11%) |
| MRR | 0.8542 (85.42%) |
| Citation correctness | 1.0000 (100%) |
| Answerability accuracy | 0.8000 (80.00%) |
| Abstention accuracy | 1.0000 (100%) |
| Average latency | 12.9992 seconds |
| Maximum latency | 100.167 seconds |
| LLM-call cost proxy | 25 calls |

## 9. 🚨 Failure Analysis

The baseline scorecard identified the following failure categories:

| Failure Category | Count |
|------------------|-------|
| Answerability mismatch | 4 |
| Retrieval failure | 3 |
| Evaluation error | 1 |

### Top Three Failure Categories

1. Answerability mismatch — 4 cases
2. Retrieval failure — 3 cases
3. Evaluation error — 1 case

These categories are generated from the evaluation results rather than manually assigned.

## 10. 🧭 Component Quality Analysis

The scorecard calculates separate component metrics so retrieval and answer quality can be analyzed independently.

| Component | Metric |
|-----------|--------|
| Answer quality | 0.8000 |
| Retrieval quality | 0.8750 |
| Citation quality | 1.0000 |
| Abstention quality | 1.0000 |

### Weakest Component

- Component : Answer quality
- Metric    : 0.8000

Therefore, the Day 14 baseline evidence identifies answer quality as the weakest measured component.

## 11. ⚙️ Regression Thresholds

Regression thresholds are defined in:

`evals/regression_thresholds.json`

Current thresholds:

```json
{
  "answer_pass_rate": 0.75,
  "retrieval_hit_rate": 0.8,
  "recall_at_k": 0.8,
  "mrr": 0.8,
  "citation_correctness": 0.95,
  "answerability_accuracy": 0.75,
  "abstention_accuracy": 0.75,
  "max_average_latency_seconds": 20.0
}
```

For quality metrics, the actual value must be greater than or equal to the configured minimum.

For average latency, the actual value must be less than or equal to the configured maximum.

## 12. 🛡️ One-Command Regression Quality Check

The regression checker is:

`evals/check_regression.py`

Run it with:

```bash
python evals\check_regression.py
```

The checker:

- Finds available scorecards.
- Skips provider/evaluation-error-only scorecards.
- Loads the latest valid scorecard.
- Loads the configured regression thresholds.
- Checks every critical metric.
- Prints PASS/FAIL for each threshold.
- Returns a successful process status only when all checks pass.

## 13. ✅ Verified Regression Check

The valid baseline was checked against the Day 14 thresholds.

```
Answer pass rate: 0.8 (minimum 0.75) -> PASS
Retrieval hit rate: 0.875 (minimum 0.8) -> PASS
Recall@K: 0.8611 (minimum 0.8) -> PASS
MRR: 0.8542 (minimum 0.8) -> PASS
Citation correctness: 1.0 (minimum 0.95) -> PASS
Answerability accuracy: 0.8 (minimum 0.75) -> PASS
Abstention accuracy: 1.0 (minimum 0.75) -> PASS
Average latency: 12.9992 (maximum 20.0) -> PASS
REGRESSION CHECK PASSED
```

The quality gate therefore passed for the valid baseline scorecard.

## 14. 🧪 Regression Failure Test

A deliberately weakened configuration was previously used to verify that the regression checker can detect a quality regression.

The test demonstrated the required behavior:

```
Threshold broken
       ↓
Metric marked FAIL
       ↓
Overall regression check marked FAILED
       ↓
Non-zero failure status returned
```

After restoring the valid baseline scorecard and thresholds, the regression check returned:

```
REGRESSION CHECK PASSED
```

This satisfies the Day 14 requirement that a deliberately weakened configuration can trigger a regression failure.

## 15. 🔄 Day 14 Evaluation Flow

```
┌─────────────────────────────────────┐
│ datasets/golden_set.jsonl           │
│ 25 evaluation cases                 │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ evals/run_evals.py                  │
│ Execute RAG evaluation              │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ Retrieval Results + Generated Answer│
│ Citations + Status + Latency        │
└──────────────────┬──────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
┌──────────────────┐ ┌────────────────────┐
│ Retrieval Grader │ │ Answer Grader      │
│ Hit Rate         │ │ Answerability      │
│ Recall@K         │ │ Citation Presence │
│ MRR              │ │ Citation Validity │
└────────┬─────────┘ │ Required Facts    │
         │           │ Abstention        │
         │           └─────────┬──────────┘
         └─────────────┬───────┘
                       ▼
┌─────────────────────────────────────┐
│ generate_eval_report.py             │
│ Per-case pass/fail + failure data   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ generate_scorecard.py               │
│ Aggregate quality metrics           │
│ Failure categories + weakest area   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ check_regression.py                 │
│ Compare against thresholds          │
└──────────────────┬──────────────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ PASS / FAIL     │
          │ Quality Gate    │
          └─────────────────┘
```

## 16. 🧪 Day 14 Verification Commands

### 16.1 Compile Grader and Evaluation Modules

```bash
python -m py_compile evals\retrieval_grader.py
python -m py_compile evals\answer_grader.py
python -m py_compile evals\generate_eval_report.py
python -m py_compile evals\generate_scorecard.py
python -m py_compile evals\check_regression.py
```

All required modules compiled successfully during Day 14 verification.

### 16.2 Generate the Baseline Evaluation Report

```bash
python evals\generate_eval_report.py --input results\eval_runs\eval_20260922T065158Z.json
```

Verified output:

```
Evaluation report generated.
Cases: 25
Report: ...\results\eval_reports\report_20260922T114940Z.md
```

### 16.3 Run the Regression Quality Check

```bash
python evals\check_regression.py
```

Verified result:

```
REGRESSION CHECK PASSED
```

## 17. ⚠️ Evaluation Provider Note

During Day 14, the configured OpenRouter free-model provider reached its daily free-model quota.

The direct provider test returned a rate-limit error indicating that the free-model daily request allowance had been exhausted.

Several later evaluation runs therefore contained provider/evaluation errors. These runs were not used as the Day 14 quality baseline.

The valid baseline used for Day 14 reporting and regression verification is:

- Evaluation run: `results/eval_runs/eval_20260922T065158Z.json`
- Scorecard: `results/scorecards/scorecard_20260922T065158Z.json`
- Report: `results/eval_reports/report_20260922T114940Z.md`

The regression checker was updated so provider/evaluation-error-only scorecards are not selected as the quality baseline.

## 18. 📦 Day 14 Required Deliverables

| Required Deliverable | Location | Status |
|----------------------|----------|--------|
| Retrieval grader module | evals/retrieval_grader.py | ✅ Complete |
| Answer grader module | evals/answer_grader.py | ✅ Complete |
| Baseline evaluation scorecard | results/scorecards/scorecard_20260922T065158Z.json | ✅ Complete |
| Per-case failure report | results/eval_reports/report_20260922T114940Z.md | ✅ Complete |
| Regression thresholds | evals/regression_thresholds.json | ✅ Complete |
| One-command quality check | evals/check_regression.py | ✅ Complete |

## 19. ✅ Day 14 Completion Gate

The roadmap defines four completion-gate requirements.

| Completion Gate | Evidence | Status |
|-----------------|----------|--------|
| Retrieval and answer failures are reported separately | Separate retrieval and answer grader results in the scorecard/report | ✅ |
| Scorecard is generated automatically from run results | generate_scorecard.py and baseline scorecard artifact | ✅ |
| At least the top three failure categories are identified | 3 categories identified in baseline | ✅ |
| Deliberately weakened configuration triggers regression failure | Regression failure behavior was tested | ✅ |

## 20. 📋 Day 14 Final Verification Checklist

### Retrieval Quality

- Retrieval grader implemented.
- Expected source matching implemented.
- Hit Rate implemented.
- Recall@K implemented.
- MRR implemented.
- Retrieval pass/fail recorded separately from answer quality.

### Answer Quality

- Answerability grading implemented.
- Citation presence check implemented.
- Citation validity check implemented.
- Required-facts check implemented where facts are available.
- Unsupported-question abstention check implemented.
- Answer pass/fail recorded separately from retrieval quality.

### Reporting

- Per-case report generated.
- Retrieval result included.
- Answer result included.
- Latency included.
- Failure category included.
- 25 cases included in the baseline report.

### Scorecard

- Answer pass rate included.
- Retrieval metrics included.
- Citation correctness included.
- Answerability accuracy included.
- Abstention accuracy included.
- Failure categories included.
- Top three failure categories identified.
- Latency included.
- Cost proxy included.
- Weakest component identified from measured evidence.

### Regression

- Minimum quality thresholds defined.
- Average latency threshold defined.
- One-command regression check implemented.
- PASS/FAIL status implemented.
- Deliberately weakened configuration tested.
- Valid baseline passes all configured thresholds.

## 21. 🏆 Day 14 Final Evidence Summary

| Evidence | Verified Result |
|----------|-----------------|
| Evaluation cases | 25 |
| Answer pass rate | 80.00% |
| Retrieval Hit Rate | 87.50% |
| Recall@K | 86.11% |
| MRR | 85.42% |
| Citation correctness | 100% |
| Answerability accuracy | 80.00% |
| Abstention accuracy | 100% |
| Average latency | 12.9992 seconds |
| Top failure categories | 3 identified |
| Weakest component | Answer quality — 0.80 |
| Regression quality gate | PASSED |
| Baseline scorecard | Generated |
| Per-case failure report | Generated |

---

## 🎯 Day 14 Status: ✅ COMPLETE

Retrieval graded • Answers graded • Scorecard generated • Failures analyzed • Regression thresholds enforced • Quality gate passed

Day 14 is complete based on the implemented graders, verified baseline scorecard, generated per-case report, regression thresholds, and successful one-command quality check.