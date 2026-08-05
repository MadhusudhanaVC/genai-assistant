"""
Main Entry Point
----------------
This is the starting point of our GenAI Assistant.

Later this file will:
- Start the FastAPI server
- Load application settings
- Connect to the database
- Register API routes
"""

from app.core.config import settings


def main():
    """
    Simple smoke test for Day 1.

    If this function runs successfully, our project
    structure and configuration are working.
    """
    print("=" * 50)
    print(f"🚀 Welcome to {settings.APP_NAME}")
    print(f"Environment : {settings.APP_ENV}")
    print("Project setup completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()