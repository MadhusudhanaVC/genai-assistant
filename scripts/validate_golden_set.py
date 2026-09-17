import json
from pathlib import Path


GOLDEN_SET_PATH = Path("datasets/golden_set.jsonl")

REQUIRED_FIELDS = {
    "case_id",
    "question",
    "category",
    "expected_source_ids",
    "answerability",
}

VALID_CATEGORIES = {
    "answerable",
    "unanswerable",
    "ambiguous",
    "multi-document",
    "adversarial",
}


def main():
    if not GOLDEN_SET_PATH.exists():
        raise FileNotFoundError(
            f"Golden set not found: {GOLDEN_SET_PATH}"
        )

    cases = []

    with GOLDEN_SET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                case = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                ) from error

            cases.append(case)

    if len(cases) != 25:
        raise ValueError(
            f"Expected 25 cases, found {len(cases)}"
        )

    case_ids = set()

    for index, case in enumerate(cases, start=1):
        missing_fields = REQUIRED_FIELDS - set(case)

        if missing_fields:
            raise ValueError(
                f"Case {index} is missing fields: "
                f"{sorted(missing_fields)}"
            )

        case_id = case["case_id"]

        if case_id in case_ids:
            raise ValueError(
                f"Duplicate case_id found: {case_id}"
            )

        case_ids.add(case_id)

        category = case["category"]

        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"{case_id}: invalid category '{category}'"
            )

        expected_source_ids = case["expected_source_ids"]

        if not isinstance(expected_source_ids, list):
            raise ValueError(
                f"{case_id}: expected_source_ids must be a list"
            )

        if category == "answerable" and not expected_source_ids:
            raise ValueError(
                f"{case_id}: answerable case must have "
                "at least one expected source"
            )

        if category == "unanswerable" and expected_source_ids:
            raise ValueError(
                f"{case_id}: unanswerable case should not "
                "have expected sources"
            )

    categories = {
        case["category"]
        for case in cases
    }

    missing_categories = VALID_CATEGORIES - categories

    if missing_categories:
        raise ValueError(
            "Missing required categories: "
            f"{sorted(missing_categories)}"
        )

    print("Golden set validation PASSED")
    print(f"Total cases: {len(cases)}")

    for category in sorted(categories):
        count = sum(
            1
            for case in cases
            if case["category"] == category
        )
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()