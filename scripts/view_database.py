"""
View SQLite Database
--------------------

Displays all rows from:
1. documents
2. processing_events
"""

from sqlalchemy import text

from app.db.database import SessionLocal


def main():

    db = SessionLocal()

    print("\n========== DOCUMENTS ==========\n")

    documents = db.execute(
        text("SELECT * FROM documents")
    ).fetchall()

    if not documents:
        print("No documents found.")

    else:
        for row in documents:
            print(row)

    print("\n======= PROCESSING EVENTS =======\n")

    events = db.execute(
        text("SELECT * FROM processing_events")
    ).fetchall()

    if not events:
        print("No events found.")

    else:
        for row in events:
            print(row)

    db.close()


if __name__ == "__main__":
    main()