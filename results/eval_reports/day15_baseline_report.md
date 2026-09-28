# Day 15 Adversarial Baseline Report

## 1. Baseline Identification

* **Baseline commit:** `ae6b417`
* **Purpose:** Document the application's existing defenses before Day 15 adversarial controls.
* **Evidence basis:** Source-code inspection and baseline test results recorded below.
* **Baseline workspace:** `genai-assistant-day15-baseline`
* **Report updated:** 2026-09-28

This report describes the pre-Day 15 implementation. It distinguishes source-code observations from executed test results. It does not claim that all adversarial cases were executed against the baseline.

## 2. Existing Controls Identified in Source Code

The baseline API request model (`app/models/api.py`) provides:

* A required `question` field with string type validation.
* A minimum question length of one character.
* `top_k` defaults to `3` and must be at least `1`.
* Optional `min_score` constrained to the range `0–1`.
* FastAPI/Pydantic request validation.

The baseline RAG and prompt implementation also contains grounded-answer instructions, citation requirements, and instructions to abstain when evidence is insufficient.

These are source-code observations. They do not independently prove that every unsafe request is handled correctly at runtime.

## 3. Missing Dedicated Day 15 Controls

Source-code inspection identified the following gaps in the baseline implementation:

* No dedicated prompt-injection evaluation before the RAG pipeline.
* No explicit 2,000-character question limit in the baseline request model.
* No dedicated guardrail decision function.
* No dedicated guardrail-blocked response for detected prompt injection.
* No explicit instruction-hierarchy defense against malicious instructions in retrieved documents.
* No dedicated guardrail decision logging.

These findings describe the inspected pre-Day 15 implementation. They should not be interpreted as proof that every attack would succeed.

## 4. Baseline Risk Assessment

| Category                       | Finding from source-code inspection                                                                                                           |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Direct prompt injection        | No dedicated input guardrail identified in the `/ask` route. Actual attack behavior was not established.                                      |
| Instructions in retrieved text | No explicit retrieved-context instruction-hierarchy defense identified in the inspected implementation. Runtime behavior was not established. |
| Restricted-data requests       | No dedicated prompt-injection guardrail identified; actual behavior was not established.                                                      |
| Irrelevant context             | Grounded-answer instructions provide an abstention mechanism; runtime behavior requires testing.                                              |
| Conflicting sources            | No dedicated conflict guardrail identified; runtime behavior requires testing.                                                                |
| Unsupported requests           | Existing retrieval and abstention instructions; runtime behavior requires testing.                                                            |
| Excessive input                | No explicit 2,000-character limit in the baseline request model.                                                                              |
| Malformed payloads             | Existing Pydantic validation; not every malformed payload has been tested.                                                                    |
| Guardrail logging              | No dedicated guardrail decision logging identified.                                                                                           |
| Benign questions               | The `/ask` route passes valid requests to `generate_grounded_answer()`. The API success test passed with a mocked answer generator.           |

## 5. Baseline Test Results

### 5.1 Full baseline test suite

The full baseline suite did not complete successfully during the earlier test run.

* Pytest reported 13 collected items and 3 collection errors.
* The collection errors involved tests importing the LLM client, which initializes the OpenAI client without an available `OPENAI_API_KEY`.
* No live LLM calls were made during that run.

This result represents a test-environment and collection limitation. It is not evidence that the baseline passed or failed adversarial attacks.

### 5.2 Independent baseline tests

**Command:**

`python -m pytest tests/test_document_validation.py tests/test_chunking.py tests/test_cli_loader.py tests/test_database.py -v`

**Result:**

* 12 passed.
* 1 failed: `tests/test_database.py::test_sql_event_insertion`.
* The failure reported `sqlite3.OperationalError: no such table: processing_events`.

These results describe the baseline test environment. They are not adversarial attack-test results.

### 5.3 Baseline API tests — verified 2026-09-28

**Command:**

`python -m pytest tests/test_api.py -v`

**Initial result:**

All 10 tests initially failed because the SQLite database did not contain the `api_requests` table. The request-logging middleware attempted to write to that table before the requests could complete.

**Database setup:**

The baseline database tables were subsequently initialized using SQLAlchemy:

`Base.metadata.create_all(bind=engine)`

This initialization created missing tables without deleting existing tables or rows. The command was run in the baseline workspace and may have modified its `genai.db` file.

**Result after initialization:**

* **10 passed.**
* **0 failed.**
* **Duration:** 100.95 seconds.

The passing tests were:

1. `test_health`
2. `test_ask_validation_empty_question`
3. `test_ask_validation_invalid_top_k`
4. `test_ask_validation_invalid_min_score`
5. `test_document_not_found`
6. `test_ask_success`
7. `test_ask_missing_evidence`
8. `test_ask_provider_failure`
9. `test_ingest_success`
10. `test_document_success`

The answer-generation functions in the relevant API tests were mocked. The successful test run did not require live LLM calls.

**Interpretation and limitations:**

The result confirms that the 10 tested API behaviors passed after the missing database tables were initialized. It does not establish that the baseline had the dedicated Day 15 security controls, nor does it establish an adversarial attack success or refusal rate.

The test setup also means the baseline database artifact was not left completely unchanged: its missing tables were initialized during the investigation. The baseline application source code was not changed as part of this database initialization.

### 5.4 Existing evaluation report

The existing report `results/eval_reports/report_20260922T114940Z.md` records 25 evaluation cases.

* All 25 cases are marked `FAIL`.
* The recorded failure category is `evaluation_error`.
* The actual answer status is recorded as `None`.
* Retrieval is marked `not graded`.

These results do not establish that the baseline assistant produced unsafe answers. Because the evaluations failed and the answers were not successfully graded, they cannot be used to calculate adversarial attack success or refusal rates.

### 5.5 Baseline evidence summary

| Evidence                                | Result               | What it establishes                                                   |
| --------------------------------------- | -------------------- | --------------------------------------------------------------------- |
| Full baseline suite                     | 3 collection errors  | The full suite did not complete in the earlier run.                   |
| Independent baseline tests              | 12 passed, 1 failed  | The selected tests ran, with a database-table failure.                |
| API tests after database initialization | 10 passed, 0 failed  | The tested API behaviors passed under the initialized database setup. |
| Existing 25-case evaluation report      | 25 evaluation errors | The recorded evaluation did not establish actual answer behavior.     |
| Dedicated baseline adversarial suite    | Not established      | No verified baseline attack success or refusal rate is available.     |

## 6. Conclusion

The pre-Day 15 application had basic request-schema validation and grounded-answer constraints. Source-code inspection identified no dedicated adversarial input-defense layer, explicit 2,000-character question limit, retrieved-context instruction-hierarchy defense, or dedicated guardrail decision logging.

The baseline API regression tests passed after the missing SQLite tables were initialized. However, the full baseline suite did not complete successfully in the earlier run, and the existing 25-case evaluation report contains evaluation errors rather than graded answer outcomes.

Day 15 introduces dedicated question validation, prompt-injection detection, retrieved-context instruction-hierarchy protection, and guardrail decision observability.

A complete baseline adversarial comparison has not been established. Claims about actual attack success, unsafe acceptance, incorrect refusal, malformed output, or refusal rates must be supported by executed tests that directly measure those outcomes. They must not be inferred from source-code inspection or failed evaluations.

The baseline API test result and the Day 15 adversarial test results should be reported separately because they measure different things.
