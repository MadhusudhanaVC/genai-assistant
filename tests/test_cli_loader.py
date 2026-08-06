"""
Tests for CLI Loader
--------------------

These tests verify that the CLI handles
missing files and malformed JSON correctly.
"""

import json
from pathlib import Path

from scripts.load_documents import load_json


# ==========================================================
# Test 3 - Malformed JSON
# ==========================================================
def test_malformed_json(tmp_path):
    """
    Test that load_json() returns None
    when the JSON file is malformed.
    """

    # Create an invalid JSON file
    invalid_file = tmp_path / "invalid.json"

    invalid_file.write_text(
        '{"document_id": "DOC001",}',
        encoding="utf-8"
    )

    result = load_json(str(invalid_file))

    assert result is None


# ==========================================================
# Test 4 - Missing File
# ==========================================================
def test_missing_file():
    """
    Test that load_json() returns None
    when the file does not exist.
    """

    result = load_json("file_that_does_not_exist.json")

    assert result is None