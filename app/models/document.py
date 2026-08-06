"""
Document Model
--------------
This module defines the structure of a document.

Purpose:
- Validate JSON input.
- Ensure required fields are present.
- Prevent invalid data from entering the database.
"""

from pydantic import BaseModel, Field, field_validator


class Document(BaseModel):
    """
    Represents one document loaded from a JSON file.
    """

    # Unique ID of the document
    document_id: str = Field(
        ...,
        min_length=1,
        description="Unique document identifier"
    )

    # Title of the document
    title: str = Field(
        ...,
        min_length=1,
        description="Document title"
    )

    # Main document content
    content: str = Field(
        ...,
        min_length=1,
        description="Document content"
    )

    # Original file location
    source_path: str = Field(
        ...,
        min_length=1,
        description="Path of the source file"
    )

    # Last updated date
    updated_at: str = Field(
        ...,
        min_length=1,
        description="Last updated date"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        """
        Ensure the content is not empty or just spaces.
        """
        if not value.strip():
            raise ValueError("Content cannot be empty.")
        return value