import argparse
import json
from pathlib import Path

from app.llm.client import generate_response
from app.llm.validator import validate_response


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "datasets" / "prompt_test_cases.json"
PROMPTS_FOLDER = PROJECT_ROOT / "prompts"
RESULTS_FOLDER = PROJECT_ROOT / "results"


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def read_text_file(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found:\n{file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_prompt(task: str, prompt_version: str):
    if task == "summarization":
        prompt_file = (
            PROMPTS_FOLDER
            / f"summarization_{prompt_version}.txt"
        )
    else:
        prompt_file = PROMPTS_FOLDER / f"{task}.txt"

    return read_text_file(prompt_file)


def build_prompt(prompt_template: str, input_text: str):
    if "{input_text}" not in prompt_template:
        raise ValueError(
            "Prompt template does not contain {input_text}."
        )

    return prompt_template.replace(
        "{input_text}",
        input_text,
    )


def parse_generated_response(response_text: str):
    cleaned_response = response_text.strip()

    if cleaned_response.startswith("```"):
        lines = cleaned_response.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned_response = "\n".join(lines).strip()

    if cleaned_response.lower().startswith("json"):
        cleaned_response = cleaned_response[4:].strip()

    return json.loads(cleaned_response)


def execute_case(
    case,
    prompt_version="v1",
):
    task = case["task"]

    input_path = PROJECT_ROOT / case["input_file"]

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{input_path}"
        )

    prompt_template = load_prompt(
        task=task,
        prompt_version=prompt_version,
    )

    input_text = read_text_file(input_path)

    final_prompt = build_prompt(
        prompt_template,
        input_text,
    )

    response = generate_response(final_prompt)

    print()
    print("========== RAW MODEL RESPONSE ==========")
    print(response["text"])
    print("========================================")
    print()

    success, validated, failure = validate_response(
        task,
        response["text"],
    )

    try:
        generated_response = parse_generated_response(
            response["text"]
        )
    except json.JSONDecodeError:
        generated_response = response["text"]

    return {
        "case_id": case["case_id"],
        "task": task,
        "prompt_version": prompt_version,
        "model": response["model"],
        "latency_seconds": response["latency_seconds"],
        "generated_response": generated_response,
        "validation_passed": success,
        "failure_category": failure,
        "failure_reason": (
            None if success else str(validated)
        ),
    }
def save_results(results, prompt_version):
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
            ensure_ascii=False,
        )

    return output_file


def run_all_tests(prompt_version="v1"):
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
                    f"FAILED "
                    f"({result['failure_category']})"
                )

        except Exception as error:
            failed += 1

            print("ERROR")
            print(f"      {error}")

            result = {
                "case_id": case["case_id"],
                "task": case["task"],
                "prompt_version": prompt_version,
                "model": None,
                "latency_seconds": None,
                "generated_response": None,
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
        prompt_version=args.prompt_version
    )


if __name__ == "__main__":
    main()