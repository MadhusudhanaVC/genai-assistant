"""
OpenRouter API Connection Test
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

try:
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL"),
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: API is working"
            }
        ],
    )

    print("\n===================================")
    print("✅ OpenRouter Connection Successful!")
    print("-----------------------------------")
    print(response.choices[0].message.content)
    print("===================================")

except Exception as error:
    print("\n===================================")
    print("❌ Connection Failed")
    print("-----------------------------------")
    print(error)
    print("===================================")