"""
Prompt Output Models
--------------------

Pydantic models used to validate LLM responses
for the Prompt Playground tasks.

Tasks:
- Summarization
- Information Extraction
- Classification
"""

# ==================================================
# Imports
# ==================================================

from typing import Optional, Literal

from pydantic import BaseModel, Field


# ==================================================
# Summarization Output
# ==================================================

class SummaryOutput(BaseModel):
    """
    Expected output for summarization.
    """

    summary: str = Field(
        ...,
        min_length=1,
        description="Generated summary"
    )


# ==================================================
# Extraction Output
# ==================================================

class ExtractionOutput(BaseModel):
    """
    Expected output for information extraction.
    """

    document_id: Optional[str] = None

    customer_name: Optional[str] = None

    invoice_number: Optional[str] = None

    invoice_date: Optional[str] = None

    amount: Optional[str] = None


# ==================================================
# Classification Output
# ==================================================

class ClassificationOutput(BaseModel):
    """
    Expected output for classification.
    """

    label: Literal[
        "Complaint",
        "Inquiry",
        "Feedback",
        "Request",
    ]

    reason: str = Field(
        ...,
        min_length=1,
        description="Short explanation"
    )