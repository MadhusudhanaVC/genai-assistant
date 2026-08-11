# Prompt Version Comparison

## Objective

Compare two versions of the summarization prompt using the same prompt test dataset.

---

## Version 1

- Summary under 100 words
- Return valid JSON

---

## Version 2

- Summary under 80 words
- Exactly 2–3 concise sentences
- Return valid JSON

---

## Test Results

| Metric | Version 1 | Version 2 |
|---------|-----------|-----------|
| Total Cases | 10 | 10 |
| Passed | 10 | 10 |
| Failed | 0 | 0 |

---

## Observation

Both prompt versions successfully passed schema validation for all ten test cases.

Version 2 produced shorter and more consistent summaries while preserving the important information from the source text.

---

## Preferred Version

**Version 2**

Reason:
- More concise summaries
- Better readability
- Consistent structure
- 100% validation success