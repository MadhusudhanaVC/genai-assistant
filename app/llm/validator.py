"""
Validates LLM JSON responses using Pydantic models.
"""

# ==================================================
# Imports
# ==================================================

import json

from pydantic import ValidationError

from app.models.prompt_outputs import (
    SummaryOutput,
    ExtractionOutput,
    ClassificationOutput,
)

# ==================================================
# Clean LLM Output
# ==================================================

def clean_response(response_text: str) -> str:
    """
    Remove markdown code fences and extra text
    before parsing JSON.
    """

    response_text = response_text.strip()

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "", 1)

    if response_text.startswith("```"):
        response_text = response_text.replace("```", "", 1)

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Find first JSON object
    start = response_text.find("{")
    end = response_text.rfind("}")

    if start != -1 and end != -1:
        response_text = response_text[start:end + 1]

    return response_text


# ==================================================
# Validation Function
# ==================================================

def validate_response(task: str, response_text: str):
    """
    Validate an LLM response.
    """

    # --------------------------
    # Clean Response
    # --------------------------

    response_text = clean_response(response_text)

    # --------------------------
    # Parse JSON
    # --------------------------

    try:
        data = json.loads(response_text)

    except json.JSONDecodeError as error:

        return (
            False,
            str(error),
            "JSON_PARSE_ERROR",
        )

    # --------------------------
    # Select Model
    # --------------------------

    model_map = {
        "summarization": SummaryOutput,
        "extraction": ExtractionOutput,
        "classification": ClassificationOutput,
    }

    model = model_map.get(task)

    if model is None:

        return (
            False,
            "Unknown task",
            "CONFIG_ERROR",
        )

    # --------------------------
    # Validate Schema
    # --------------------------s

    try:

        validated = model(**data)

        return (
            True,
            validated,
            None,
        )

    except ValidationError as error:

        return (
            False,
            str(error),
            "VALIDATION_ERROR",
        )