"""
Document Loader CLI
-------------------

Purpose:
- Accept a JSON file path.
- Read the JSON safely.
- Validate every document using the Pydantic model.
- Save valid documents into SQLite.
- Log processing events (STARTED, COMPLETED, FAILED).
"""

# ==========================================================
# Standard Library Imports
# ==========================================================
import sys
import os
import json

# ==========================================================
# Third Party Imports
# ==========================================================
from pydantic import ValidationError

# ==========================================================
# Local Imports
# ==========================================================
from app.models.document import Document
from app.db.database import SessionLocal
from app.db.crud import save_document, log_event


# ==========================================================
# Read JSON File
# ==========================================================
def load_json(file_path: str):
    """
    Read a JSON file safely.

    Parameters
    ----------
    file_path : str
        Path to the JSON file.

    Returns
    -------
    list | None
        Parsed JSON data or None if reading fails.
    """

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data

    except json.JSONDecodeError:
        print("❌ Invalid JSON format.")
        return None


# ==========================================================
# Validate Documents
# ==========================================================
def validate_documents(documents):
    """
    Validate every document using the Pydantic model.
    """

    validated_documents = []

    for index, document_data in enumerate(documents, start=1):

        try:
            document = Document(**document_data)
            validated_documents.append(document)

        except ValidationError as error:

            print(f"\n❌ Validation failed for document #{index}")
            print(error)

            return None

    return validated_documents


# ==========================================================
# Main Function
# ==========================================================
def main():
    """
    Entry point of the CLI.
    """

    # User must provide exactly one JSON file
    if len(sys.argv) != 2:
        print("Usage:")
        print("python -m scripts.load_documents <json_file>")
        return

    file_path = sys.argv[1]

    # ------------------------------------------------------
    # Read JSON
    # ------------------------------------------------------
    documents = load_json(file_path)

    if documents is None:
        return

    # ------------------------------------------------------
    # Validate Documents
    # ------------------------------------------------------
    validated_documents = validate_documents(documents)

    if validated_documents is None:
        return

    # ------------------------------------------------------
    # Create Database Session
    # ------------------------------------------------------
    db = SessionLocal()

    try:

        # Process every validated document
        for document in validated_documents:

            # ------------------------------------------
            # Log STARTED Event
            # ------------------------------------------
            log_event(
                db=db,
                document_id=document.document_id,
                event_type="STARTED",
                status="SUCCESS"
            )

            try:
                # --------------------------------------
                # Save Document
                # --------------------------------------
                save_document(db, document)

                # --------------------------------------
                # Log COMPLETED Event
                # --------------------------------------
                log_event(
                    db=db,
                    document_id=document.document_id,
                    event_type="COMPLETED",
                    status="SUCCESS"
                )

            except Exception as document_error:

                # --------------------------------------
                # Log FAILED Event
                # --------------------------------------
                log_event(
                    db=db,
                    document_id=document.document_id,
                    event_type="FAILED",
                    status="FAILED",
                    error_message=str(document_error)
                )

                print("\n--------------------------------------")
                print(f"❌ Failed to process: {document.document_id}")
                print(document_error)
                print("--------------------------------------")

        print("\n===================================")
        print("✅ Document processing finished.")
        print(f"📄 Total Documents : {len(validated_documents)}")
        print("💾 Database updated successfully.")
        print("===================================")

    except Exception as error:

        print("\n===================================")
        print("❌ Unexpected Error")
        print(error)
        print("===================================")

    finally:
        db.close()


# ==========================================================
# Program Entry
# ==========================================================
if __name__ == "__main__":
    main()