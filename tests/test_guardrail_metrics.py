
def calculate_guardrail_metrics(cases: list[dict]) -> dict:
    """Count false accepts and false rejects across evaluation cases."""

    false_accepts = 0
    false_rejects = 0
    total = len(cases)

    for case in cases:
        expected = case["expected"]
        actual = case["actual"]

        # An unanswerable question was incorrectly answered.
        if expected == "unanswerable" and actual == "answered":
            false_accepts += 1

        # An answerable question was incorrectly blocked.
        elif (
            expected == "answerable"
            and actual == "insufficient_evidence"
        ):
            false_rejects += 1

    return {
        "total_cases": total,
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
    }


def test_guardrail_metrics_count_false_accepts_and_rejects():
    cases = [
        {"expected": "answerable", "actual": "answered"},
        {"expected": "answerable", "actual": "insufficient_evidence"},
        {"expected": "unanswerable", "actual": "insufficient_evidence"},
        {"expected": "unanswerable", "actual": "answered"},
    ]

    metrics = calculate_guardrail_metrics(cases)

    assert metrics["total_cases"] == 4
    assert metrics["false_accepts"] == 1
    assert metrics["false_rejects"] == 1


def test_guardrail_metrics_are_zero_when_all_cases_are_correct():
    cases = [
        {"expected": "answerable", "actual": "answered"},
        {"expected": "unanswerable", "actual": "insufficient_evidence"},
    ]

    metrics = calculate_guardrail_metrics(cases)

    assert metrics["total_cases"] == 2
    assert metrics["false_accepts"] == 0
    assert metrics["false_rejects"] == 0