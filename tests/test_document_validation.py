"""
Tests for Document Validation
-----------------------------

These tests verify that our Pydantic Document model
validates input correctly.
"""

# Import pytest
import pytest

# Import Pydantic ValidationError
from pydantic import ValidationError

# Import our Document model
from app.models.document import Document


# ==========================================================
# Test 1 - Valid Document
# ==========================================================
def test_valid_document():
    """
    Test that a valid document is created successfully.
    """

    document = Document(
        document_id="DOC001",
        title="Python Basics",
        content="Python is an easy programming language.",
        source_path="docs/python.txt",
        updated_at="2026-08-06"
    )

    assert document.document_id == "DOC001"
    assert document.title == "Python Basics"

# ==========================================================
# Test 2 - Missing Required Field
# ==========================================================
def test_missing_required_field():
    """
    Test that validation fails when a required field is missing.
    """

    # updated_at is intentionally missing
    with pytest.raises(ValidationError):

        Document(
            document_id="DOC002",
            title="Machine Learning",
            content="Introduction to Machine Learning.",
            source_path="docs/ml.txt"
        )