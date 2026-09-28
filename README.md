# Day 15: Adversarial Testing & Prompt Injection Protection

## Overview

Day 15 strengthens the GenAI assistant against adversarial and malformed inputs while preserving the expected behavior of the retrieval-augmented generation (RAG) pipeline. The implementation introduces a 10-case adversarial test suite, explicit input validation, instruction-hierarchy protections, and structured guardrail decision logging.

The objective is to prevent hostile instructions from overriding application rules, return controlled responses for malformed requests, and ensure benign questions can still reach the RAG pipeline. Automated tests verify these protections without making live LLM calls.

## Contents

- [Practical Goal](#practical-goal)
- [RAG Architecture Context](#rag-architecture-context)
- [Day 15 Objectives](#1-day-15-objectives)
- [Input Validation & Guardrails](#2-input-validation--guardrails)
- [Instruction Hierarchy Protection](#3-instruction-hierarchy-protection)
- [Adversarial Test Suite](#4-adversarial-test-suite)
- [Guardrail Decision Logging](#5-guardrail-decision-logging)
- [Baseline Results](#6-baseline-results)
- [Verification & Completion Evidence](#7-verification--completion-evidence)

---

## Practical Goal

Prevent malformed or hostile inputs from bypassing application rules while allowing benign questions to continue through the RAG pipeline.

## RAG Architecture Context

Day 15 builds on the existing Day 14 RAG pipeline. Day 14's evaluation work separates retrieval quality from answer quality and provides reports, scorecards, and regression checks to assess pipeline behavior. This is useful context for Day 15 because security controls must protect the assistant without breaking normal retrieval and grounded answering.

At a high level, the request flow is:

1. **API request validation** — validate the incoming question and request parameters.
2. **Day 15 guardrail evaluation** — check the question for invalid or adversarial input before generation.
3. **RAG retrieval and context preparation** — retrieve relevant evidence and prepare bounded context for the answer.
4. **Grounded generation** — keep application instructions separate from the user question and retrieved text.
5. **Response and decision logging** — return a controlled response and record the guardrail control, outcome, and reason code without storing the question in the guardrail-decision record.

Day 14's evaluation reports and regression checks provide quality evidence for the RAG pipeline; Day 15's adversarial tests and guardrails add security evidence. Both matter: a secure assistant should resist hostile input while still allowing benign questions to reach RAG.

## 1. Day 15 Objectives

The Day 15 implementation covers the following requirements:

- Create a 10-case adversarial test suite.
- Check direct prompt injection and attempts to extract restricted instructions.
- Treat instructions found in retrieved documents as untrusted content.
- Validate request fields and reject malformed question values.
- Enforce a maximum question length.
- Reject requests detected by the input guardrails before RAG generation.
- Keep trusted system instructions separate from user questions and retrieved context.
- Limit the size of retrieved context passed to generation.
- Record guardrail decisions using a control, outcome, reason code, request ID, and timestamp.
- Test that guardrail behavior does not prevent benign questions from reaching RAG.

## 2. 🛡️ Guardrail and Request-Validation Flow

The `/ask` endpoint evaluates the incoming question before starting RAG generation.

```text
Incoming request
      |
      v
API request validation
      |
      v
Input guardrail evaluation
      |
      +---- Blocked request ----> Controlled error response
      |
      v
Allowed question
      |
      v
RAG retrieval and context preparation
      |
      v
Grounded answer generation
      |
      v
Response returned
```

The guardrail implementation is located in:

`app/safety/guardrails.py`

The API integration is in:

`app/api/routes.py`

The implementation includes a maximum question length of 2,000 characters and checks for suspicious prompt-injection patterns. Requests rejected by the guardrail are blocked before answer generation.

## 3. 🔐 Instruction-Hierarchy Protection

The generation flow separates trusted system instructions from the user question and retrieved context.

Relevant implementation files:

- `prompts/grounded_answer.txt`
- `app/rag/generate.py`
- `app/llm/client.py`

The system instructions define how the assistant should behave. User input and retrieved document text are treated as untrusted data and must not override those instructions.

Retrieved documents can provide evidence for an answer, but instructions contained inside those documents are not application commands. The prompt explicitly directs the model to ignore instructions embedded in retrieved content.

The LLM client supports a separate `system_prompt` argument so the trusted system message is sent separately from the user/context message.

## 4. 📏 Context and Input Limits

The Day 15 implementation adds limits and checks intended to reduce malformed or excessive input reaching generation.

| Control | Purpose |
|---|---|
| Question type and field validation | Reject malformed request values |
| Maximum question length | Reject questions exceeding 2,000 characters |
| Injection-pattern detection | Block requests matching configured suspicious patterns |
| Retrieved-context limits | Cap context at 3 chunks and 6,000 characters |
| Context preparation validation | Validate positive limits and deduplicate context |

The guardrails are defensive controls, not a guarantee that every possible prompt injection will be detected. The adversarial tests document the specific behaviors covered by the current implementation.

## 5. 🧪 Adversarial Test Suite

The adversarial suite is implemented in:

`tests/test_adversarial.py`

It contains 10 cases:

| # | Test case | Expected behavior |
|---:|---|---|
| 1 | Direct prompt injection | Block the hostile request |
| 2 | Attempt to extract system instructions | Block the restricted request |
| 3 | Malicious instructions in retrieved text | Treat the text as data, not instructions |
| 4 | Restricted-data request | Block the request |
| 5 | Irrelevant context | Avoid an unsupported answer |
| 6 | Conflicting sources | Retain the sources as evidence rather than treating one as an instruction |
| 7 | Unsupported request | Abstain when evidence is insufficient |
| 8 | Excessive input | Reject input exceeding the configured limit |
| 9 | Malformed question type | Return controlled request validation |
| 10 | Benign question | Allow the question to reach RAG |

These tests use controlled test doubles where appropriate; the test suite does not require live LLM calls.

## 6. 🧾 Guardrail Decision Logging

Guardrail decisions are recorded through the database model and CRUD integration.

Relevant files:

- `app/db/models.py`
- `app/db/crud.py`
- `app/api/routes.py`

The decision record includes:

- `request_id`
- `control`
- `outcome`
- `reason_code`
- `timestamp`

The guardrail decision table does not include a field for storing the full question or prompt. This limits what is stored in this particular audit record; it does not by itself establish that no other application logs contain request content.

Logging tests are in:

`tests/test_guardrail_logging.py`

## 7. 📁 Day 15 Project Structure

```text
genai-assistant/
├── app/
│   ├── api/
│   │   ├── errors.py                 # Controlled API errors
│   │   └── routes.py                 # Guardrail integration in /ask
│   ├── db/
│   │   ├── crud.py                   # Guardrail decision logging
│   │   └── models.py                 # Guardrail decision model
│   ├── llm/
│   │   └── client.py                 # Separate system/user messages
│   ├── rag/
│   │   └── generate.py               # Grounded generation and context
│   └── safety/
│       └── guardrails.py             # Input validation and guardrails
├── prompts/
│   └── grounded_answer.txt           # Grounding and hierarchy instructions
├── results/
│   └── eval_reports/
│       └── day15_baseline_report.md  # Baseline findings and limitations
└── tests/
    ├── test_adversarial.py
    ├── test_guardrail_logging.py
    ├── test_guardrails.py
    ├── test_llm_instruction_hierarchy.py
    └── test_prompt_security.py
```

This is a focused overview of the Day 15 files, not an exhaustive listing of every file in the repository.

## 8. ✅ Automated Verification

The following tests were run in the Day 15 workspace.

| Test group | Verified result |
|---|---:|
| Full test suite: `python -m pytest tests/ -v` | **58 passed, 0 failed** |
| Adversarial suite: `tests/test_adversarial.py` | **10 passed** |
| Guardrail logging: `tests/test_guardrail_logging.py` | **3 passed** |
| Guardrails, prompt security, and instruction hierarchy | **16 passed** |
| Focused injection-blocking and benign-input evidence | **2 passed, 8 deselected** |
| `git diff --check` | No whitespace errors; Windows line-ending warnings only |

The adversarial and guardrail tests use mocks/test doubles as appropriate; no live LLM calls were used for these test runs.

### Key Evidence

- **Injection blocked:** The direct prompt-injection test passed.
- **Benign input allowed:** The benign-question test passed and verified that the question reaches RAG.
- **Malformed input controlled:** Validation and guardrail tests passed.
- **Decision logging covered:** Guardrail logging tests passed.

These results verify the behaviors covered by the tests; they do not prove that every possible adversarial input will be blocked.

## 9. 📋 Day 15 Baseline Report

The baseline report is stored at:

`results/eval_reports/day15_baseline_report.md`

The report records the Day 14 baseline commit and distinguishes source-code inspection from runtime test evidence.

The baseline full test suite could not be completed because test collection encountered OpenAI client initialization errors when `OPENAI_API_KEY` was not configured. Independent baseline tests also exposed a missing SQLite table, and the baseline API tests passed after the database tables were initialized.

The baseline workspace database was modified during this investigation to create missing tables. Therefore, it should not be described as an untouched baseline database.

A later evaluation report containing 25 `evaluation_error` results is not evidence that the baseline accepted adversarial requests. The report does not establish attack success or refusal behavior for those cases.

## 10. 📦 Day 15 Deliverables

| Deliverable | Location | Evidence |
|---|---|---|
| Adversarial test suite | `tests/test_adversarial.py` | 10 tests passed |
| Input guardrails | `app/safety/guardrails.py` | Guardrail tests passed |
| Controlled API errors | `app/api/errors.py`, `app/main.py` | API and validation tests passed |
| Instruction-hierarchy protection | `prompts/grounded_answer.txt`, `app/rag/generate.py`, `app/llm/client.py` | Prompt-security and hierarchy tests passed |
| Guardrail decision logging | `app/db/models.py`, `app/db/crud.py` | 3 logging tests passed |
| Baseline findings | `results/eval_reports/day15_baseline_report.md` | Limitations and evidence recorded |

## 11. 🧪 Day 15 Verification Commands

Run these commands from the project root with the project virtual environment activated.

### Run the full test suite

```bash
python -m pytest tests/ -v
```

Expected result from the verified Day 15 run:

```text
58 passed, 0 failed
```

### Run the adversarial suite

```bash
python -m pytest tests/test_adversarial.py -v
```

Expected result from the verified Day 15 run:

```text
10 passed
```

### Verify the two key evidence cases

```bash
python -m pytest tests/test_adversarial.py -k "direct_prompt_injection_is_blocked or benign_question_reaches_rag" -v
```

Verified result:

```text
2 passed, 8 deselected
```

## 12. 🏁 Day 15 Completion Gate

| Completion gate | Evidence | Status |
|---|---|---|
| Malformed inputs receive controlled responses | Request validation and guardrail tests | ✅ Verified |
| Retrieved instructions do not replace application instructions | Separate system/user messages and hierarchy tests | ✅ Verified by tests |
| Guardrail outcomes are covered by automated tests | Guardrail, adversarial, and logging tests | ✅ Verified |
| Benign questions still reach RAG | Benign-input adversarial test | ✅ Verified |

## 13. 🎯 Day 15 Final Evidence Summary

| Evidence | Verified result |
|---|---|
| Adversarial cases | 10 tests passed |
| Full test suite | 58 passed, 0 failed |
| Direct prompt injection | Blocked in the tested case |
| Benign question | Reached RAG in the tested case |
| Guardrail decision logging | 3 tests passed |
| Baseline report | Created with limitations documented |
| Live LLM calls in Day 15 tests | None |

---

## 🎯 Day 15 Status: ✅ VERIFIED BY AUTOMATED TESTS

Input validation • Prompt-injection defenses • Instruction-hierarchy protection • Guardrail decision logging • Adversarial test coverage

Day 15 verification is based on the implemented controls and the recorded automated test results. The tests cover the defined cases and should not be interpreted as proof against every possible attack.
