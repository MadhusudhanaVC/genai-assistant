import pytest

from app.llm.validator import clean_response, validate_response
from app.models.prompt_outputs import GroundedAnswerOutput


def test_clean_response_extracts_json_from_surrounding_text():
    response_text = (
        'Here is the result: '
        '{"summary": "Payment is due in 30 days."}'
        ' End of response.'
    )

    cleaned = clean_response(response_text)

    assert cleaned == '{"summary": "Payment is due in 30 days."}'


def test_valid_grounded_answer_is_accepted():
    response_text = """
    {
        "answer": "The document states that the payment is due in 30 days.",
        "status": "answered",
        "citations": ["[DOC001 | CHUNK001]"]
    }
    """

    is_valid, validated, error = validate_response(
        "grounded_answer",
        response_text,
    )

    assert is_valid is True
    assert isinstance(validated, GroundedAnswerOutput)
    assert validated.status == "answered"
    assert validated.citations == ["[DOC001 | CHUNK001]"]
    assert error is None


def test_malformed_json_is_rejected():
    response_text = '{"answer": "Incomplete JSON", "status":'

    is_valid, error_message, error_code = validate_response(
        "grounded_answer",
        response_text,
    )

    assert is_valid is False
    assert error_code == "JSON_PARSE_ERROR"
    assert isinstance(error_message, str)


def test_missing_required_field_is_rejected():
    response_text = """
    {
        "answer": "The document contains the information.",
        "citations": []
    }
    """

    is_valid, error_message, error_code = validate_response(
        "grounded_answer",
        response_text,
    )

    assert is_valid is False
    assert error_code == "VALIDATION_ERROR"
    assert isinstance(error_message, str)


def test_invalid_status_is_rejected():
    response_text = """
    {
        "answer": "The document contains the information.",
        "status": "maybe",
        "citations": []
    }
    """

    is_valid, error_message, error_code = validate_response(
        "grounded_answer",
        response_text,
    )

    assert is_valid is False
    assert error_code == "VALIDATION_ERROR"
    assert isinstance(error_message, str)


def test_empty_answer_is_rejected():
    response_text = """
    {
        "answer": "",
        "status": "answered",
        "citations": []
    }
    """

    is_valid, error_message, error_code = validate_response(
        "grounded_answer",
        response_text,
    )

    assert is_valid is False
    assert error_code == "VALIDATION_ERROR"
    assert isinstance(error_message, str)


def test_unknown_task_is_rejected():
    is_valid, error_message, error_code = validate_response(
        "unknown_task",
        '{"answer": "Example"}',
    )

    assert is_valid is False
    assert error_message == "Unknown task"
    assert error_code == "CONFIG_ERROR"


def test_json_inside_markdown_code_fence_is_accepted():
    response_text = """```json
    {
        "answer": "The document states that payment is due in 30 days.",
        "status": "answered",
        "citations": []
    }
    ```"""

    is_valid, validated, error = validate_response(
        "grounded_answer",
        response_text,
    )

    assert is_valid is True
    assert validated.answer.startswith("The document states")
    assert error is None


def test_clean_response_removes_surrounding_whitespace():
    response_text = '  {"summary": "Test summary"}  '

    cleaned = clean_response(response_text)

    assert cleaned == '{"summary": "Test summary"}'


def test_valid_summary_is_accepted():
    response_text = '{"summary": "This is a valid summary."}'

    is_valid, validated, error = validate_response(
        "summarization",
        response_text,
    )

    assert is_valid is True
    assert validated.summary == "This is a valid summary."
    assert error is None
