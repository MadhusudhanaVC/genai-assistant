"""
Prompt Test Runner
------------------

Purpose:
- Load prompt test dataset.
- Load prompt templates.
- Read input files.
- Build prompts.
- Execute prompt test cases.
- Validate responses.
- Save machine-readable test results.

Day 4 Roadmap
-------------
Task 4 - Prompt Test Harness
"""

# ==================================================
# Standard Library Imports
# ==================================================

import argparse
import json
from pathlib import Path

# ==================================================
# Local Imports
# ==================================================

from app.llm.client import generate_response
from app.llm.validator import validate_response

# ==================================================
# Project Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "datasets" / "prompt_test_cases.json"

PROMPTS_FOLDER = PROJECT_ROOT / "prompts"

RESULTS_FOLDER = PROJECT_ROOT / "results"

# ==================================================
# Load Dataset
# ==================================================

def load_dataset():
    """
    Load prompt dataset.
    """

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ==================================================
# Read Text File
# ==================================================

def read_text_file(file_path: Path):
    """
    Read text file.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        return file.read()


# ==================================================
# Load Prompt
# ==================================================

def load_prompt(
    task: str,
    prompt_version: str,
):
    """
    Load prompt template.
    """

    if task == "summarization":

        prompt_file = (
            PROMPTS_FOLDER
            / f"summarization_{prompt_version}.txt"
        )

    else:

        prompt_file = (
            PROMPTS_FOLDER
            / f"{task}.txt"
        )

    if not prompt_file.exists():

        raise FileNotFoundError(
            f"Prompt file not found:\n{prompt_file}"
        )

    return read_text_file(
        prompt_file
    )


# ==================================================
# Build Prompt
# ==================================================

def build_prompt(
    prompt_template: str,
    input_text: str,
):
    """
    Replace placeholder.
    """

    return prompt_template.replace(
        "{input_text}",
        input_text,
    )

# ==================================================
# Execute One Test Case
# ==================================================

def execute_case(
    case,
    prompt_version="v1",
):
    """
    Execute a single prompt test case.
    """

    task = case["task"]

    # ----------------------------------------------
    # Load Input File
    # ----------------------------------------------

    input_path = (
        PROJECT_ROOT
        / case["input_file"]
    )

    if not input_path.exists():

        raise FileNotFoundError(
            f"Input file not found:\n{input_path}"
        )

    # ----------------------------------------------
    # Load Prompt
    # ----------------------------------------------

    prompt_template = load_prompt(
        task=task,
        prompt_version=prompt_version,
    )

    # ----------------------------------------------
    # Read Input
    # ----------------------------------------------

    input_text = read_text_file(
        input_path
    )

    # ----------------------------------------------
    # Build Final Prompt
    # ----------------------------------------------

    final_prompt = build_prompt(
        prompt_template,
        input_text,
    )

    # ----------------------------------------------
    # Generate Response
    # ----------------------------------------------

    response = generate_response(
        final_prompt
    )

    # ----------------------------------------------
    # Validate Response
    # ----------------------------------------------

    success, validated, failure = validate_response(
        task,
        response["text"],
    )

    # ----------------------------------------------
    # Return Result
    # ----------------------------------------------

    return {
        "case_id": case["case_id"],
        "task": task,
        "prompt_version": prompt_version,
        "model": response["model"],
        "latency_seconds": response["latency_seconds"],
        "validation_passed": success,
        "failure_category": failure,
        "failure_reason": (
            None
            if success
            else str(validated)
        ),
    }

# ==================================================
# Save Results
# ==================================================

def save_results(
    results,
    prompt_version,
):
    """
    Save prompt test results.
    """

    RESULTS_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        RESULTS_FOLDER
        / f"prompt_test_results_{prompt_version}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
        )

    return output_file


# ==================================================
# Run All Test Cases
# ==================================================

def run_all_tests(
    prompt_version="v1",
):
    """
    Execute all prompt test cases.
    """

    dataset = load_dataset()

    results = []

    passed = 0
    failed = 0

    print("\n==========================================")
    print("🚀 Running Prompt Test Suite")
    print("==========================================")
    print("Prompt Version :", prompt_version)
    print("------------------------------------------")

    for case in dataset:

        print(f"Running {case['case_id']}...")

        try:

            result = execute_case(
                case,
                prompt_version,
            )

            if result["validation_passed"]:

                passed += 1

                print("   ✅ PASSED")

            else:

                failed += 1

                print(
                    f"   ❌ FAILED ({result['failure_category']})"
                )

        except Exception as error:

            failed += 1

            print("   ❌ ERROR")
            print(f"      {error}")

            result = {
                "case_id": case["case_id"],
                "task": case["task"],
                "prompt_version": prompt_version,
                "model": None,
                "latency_seconds": None,
                "validation_passed": False,
                "failure_category": "MODEL_ERROR",
                "failure_reason": str(error),
            }

        results.append(result)

    output_file = save_results(
        results,
        prompt_version,
    )

    print("\n==========================================")
    print("📊 Prompt Test Summary")
    print("==========================================")
    print(f"Total Cases : {len(dataset)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print("------------------------------------------")
    print("Results saved to:")
    print(output_file)
    print("==========================================")

    return results


# ==================================================
# Main
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description="Prompt Test Runner"
    )

    parser.add_argument(
        "--prompt-version",
        choices=["v1", "v2"],
        default="v1",
        help="Summarization prompt version",
    )

    args = parser.parse_args()

    run_all_tests(
        prompt_version=args.prompt_version,
    )


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":
    main()