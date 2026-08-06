"""
Create Database
---------------

Creates the SQLite database and all tables.
"""

from app.db.database import engine, Base

# Import models so SQLAlchemy knows about the tables
from app.db.models import Document, ProcessingEvent


def create_database():
    """
    Create all database tables.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database created successfully!")
    print("✅ Tables: documents, processing_events")


if __name__ == "__main__":
    create_database()