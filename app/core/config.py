"""
Configuration Module
--------------------
This module loads environment variables from the .env file.

Purpose:
- Central place for application configuration.
- Prevent hardcoding secrets.
- Validate required settings during startup.
"""

from dotenv import load_dotenv
import os

# Load variables from the .env file (if present)
load_dotenv()


class Settings:
    """
    Stores application settings.

    All configuration values should be accessed through this class.
    """

    # Application Settings
    APP_NAME = os.getenv("APP_NAME", "GenAI Assistant")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True")

    # OpenAI API Key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///genai.db")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """
        Validate required environment variables.

        Raises:
            ValueError: If any required setting is missing.
        """

        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is missing. "
                "Create a .env file from .env.example and add your API key."
            )


# Create a global settings object
settings = Settings()