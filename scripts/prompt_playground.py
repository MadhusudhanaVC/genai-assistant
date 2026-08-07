"""
Prompt Playground
-----------------

Purpose:
- Load prompt templates.
- Read input files.
- Replace placeholders.
- Send prompts to the LLM.
- Validate responses.
- Save generated outputs.

Supports:
- Summarization
- Extraction
- Classification
"""

# ==================================================
# Standard Library Imports
# ==================================================

import argparse
from pathlib import Path

# ==================================================
# Local Imports
# ==================================================

from app.llm.client import generate_response
from app.llm.validator import validate_response

# ==================================================
# Read Text File
# ==================================================


def read_text_file(file_path: Path) -> str:
    """
    Read and return the contents of a text file.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        return file.read()


# ==================================================
# Save Output
# ==================================================


def save_output(
    output_path: Path,
    content: str,
):
    """
    Save generated response to a file.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(content)


# ==================================================
# Build Prompt
# ==================================================


def build_prompt(
    prompt_template: str,
    input_text: str,
) -> str:
    """
    Replace placeholders with user input.
    """

    return prompt_template.replace(
        "{input_text}",
        input_text,
    )


# ==================================================
# Main
# ==================================================


def main():

    parser = argparse.ArgumentParser(
        description="GenAI Prompt Playground"
    )

    parser.add_argument(
        "task",
        choices=[
            "summarization",
            "extraction",
            "classification",
        ],
        help="Prompt task",
    )

    parser.add_argument(
        "input_file",
        help="Input text file",
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # Paths
    # --------------------------------------------------

    prompt_path = (
        Path("prompts")
        / f"{args.task}.txt"
    )

    input_path = Path(
        args.input_file
    )

    # --------------------------------------------------
    # Read Files
    # --------------------------------------------------

    prompt_template = read_text_file(
        prompt_path
    )

    input_text = read_text_file(
        input_path
    )

    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------

    final_prompt = build_prompt(
        prompt_template,
        input_text,
    )

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    # print("\n========== FINAL PROMPT ==========\n")
    # print(final_prompt)
    # print("\n==================================\n")

    # --------------------------------------------------
    # Generate Response
    # --------------------------------------------------

    try:

        response = generate_response(
            final_prompt
        )

    except Exception as error:

        print("\n===================================")
        print("❌ Model Request Failed")
        print("-----------------------------------")
        print(error)
        print("===================================")

        return

    # --------------------------------------------------
    # Validate Response
    # --------------------------------------------------

    success, validated_output, failure_category = (
        validate_response(
            args.task,
            response["text"],
        )
    )

    if not success:

        print("\n===================================")
        print("❌ Response Validation Failed")
        print("-----------------------------------")
        print("Failure Type :", failure_category)
        print("-----------------------------------")
        print(validated_output)
        print("===================================")

        return

    # --------------------------------------------------
    # Save Output
    # --------------------------------------------------

    output_path = (
        Path("sample_outputs")
        / args.task
        / "output.txt"
    )

    save_output(
        output_path,
        response["text"],
    )

    # --------------------------------------------------
    # Print Result
    # --------------------------------------------------

    print("\n===================================")
    print("✅ Prompt executed successfully!")
    print("-----------------------------------")
    print("Task     :", args.task)
    print("Model    :", response["model"])
    print(
        "Latency :",
        response["latency_seconds"],
        "seconds",
    )
    print("-----------------------------------")
    print("✅ Validation Passed")
    print("-----------------------------------")
    print(validated_output)
    print("-----------------------------------")
    print("Output saved to:")
    print(output_path)
    print("===================================")


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":
    main()