"""
Database Configuration
----------------------

Purpose:
- Create a SQLite database connection.
- Manage database sessions.
- Create tables when the application starts.
"""

# SQLAlchemy engine is responsible for connecting to the database.
from sqlalchemy import create_engine

# Session is used to perform database operations.
from sqlalchemy.orm import sessionmaker

# Base is the parent class for all database models.
from sqlalchemy.orm import declarative_base


# ----------------------------------------------------
# Database Configuration
# ----------------------------------------------------

# SQLite database file.
# It will automatically be created in the project root.
DATABASE_URL = "sqlite:///genai.db"


# ----------------------------------------------------
# Create Database Engine
# ----------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False  # Set to True if you want SQL queries printed.
)


# ----------------------------------------------------
# Create Database Session
# ----------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ----------------------------------------------------
# Base Class
# ----------------------------------------------------

Base = declarative_base()


# ----------------------------------------------------
# Helper Function
# ----------------------------------------------------

def get_db():
    """
    Creates a new database session.

    Returns:
        SQLAlchemy Session
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()