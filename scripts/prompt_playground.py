"""
Prompt Playground
-----------------

Purpose:
- Load prompt templates.
- Read input files.
- Replace placeholders.
- Send prompts to the LLM.
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


# ==================================================
# Read Text File
# ==================================================
def read_text_file(file_path: Path) -> str:
    """
    Read and return the contents of a text file.

    Parameters
    ----------
    file_path : Path
        Path of the text file.

    Returns
    -------
    str
        File contents.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ==================================================
# Save Output
# ==================================================
def save_output(output_path: Path, content: str):
    """
    Save generated response into a text file.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)


# ==================================================
# Build Final Prompt
# ==================================================
def build_prompt(prompt_template: str, input_text: str) -> str:
    """
    Replace the placeholder with actual input text.
    """

    return prompt_template.replace("{input_text}", input_text)


# ==================================================
# Main Function
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
    # Build file paths
    # --------------------------------------------------

    prompt_path = Path("prompts") / f"{args.task}.txt"
    input_path = Path(args.input_file)

    # --------------------------------------------------
    # Read files
    # --------------------------------------------------

    prompt_template = read_text_file(prompt_path)
    input_text = read_text_file(input_path)

    # --------------------------------------------------
    # Build final prompt
    # --------------------------------------------------

    final_prompt = build_prompt(
        prompt_template,
        input_text,
    )

    # ==================================================
    # DEBUG
    # ==================================================
    # Uncomment these lines whenever you want to inspect
    # the exact prompt sent to the model.

    # print("\n========== FINAL PROMPT ==========\n")
    # print(final_prompt)
    # print("\n==================================\n")

    # --------------------------------------------------
    # Generate response
    # --------------------------------------------------

    response = generate_response(final_prompt)

    # --------------------------------------------------
    # Save output
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
    print("Task    :", args.task)
    print("Model   :", response["model"])
    print("Latency :", response["latency_seconds"], "seconds")
    print("-----------------------------------")
    print(response["text"])
    print("-----------------------------------")
    print("Output saved to:")
    print(output_path)
    print("===================================")


# ==================================================
# Program Entry
# ==================================================
if __name__ == "__main__":
    main()