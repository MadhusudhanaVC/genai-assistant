# SQLAlchemy engine is responsible for connecting to the database.
from sqlalchemy import create_engine

# Session is used to perform database operations.
from sqlalchemy.orm import sessionmaker

# Base is the parent class for all database models.
from sqlalchemy.orm import declarative_base



from app.core.config import settings


# SQLite database file.
# It will automatically be created in the project root.
DATABASE_URL = "sqlite:///genai.db"



engine = create_engine(
    DATABASE_URL,
    echo=False  # Set to True if you want SQL queries printed.
)



SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)



Base = declarative_base()



def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()