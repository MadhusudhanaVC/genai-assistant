"""
Simple test for the Document model.
"""

from app.models.document import Document

sample_document = {
    "document_id": "DOC001",
    "title": "Python Basics",
    "content": "Python is an easy programming language.",
    "source_path": "docs/python.txt",
    "updated_at": "2026-08-06"
}

document = Document(**sample_document)

print("✅ Document validation successful!")
print(document)