"""
LLM Client Wrapper
------------------

Purpose:
- Connect to OpenRouter.
- Send prompts to the model.
- Return generated text.
- Measure response latency.

This module keeps all provider-specific code
(OpenRouter/OpenAI SDK) in one place.
"""

# ==================================================
# Standard Library Imports
# ==================================================
import os
import time
from pathlib import Path

# ==================================================
# Third-Party Imports
# ==================================================
from dotenv import load_dotenv
from openai import OpenAI

# ==================================================
# Load Environment Variables
# ==================================================

# Load .env from the project root
load_dotenv(
    dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env"
)

# ==================================================
# Create OpenRouter Client
# ==================================================

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

MODEL_NAME = os.getenv("OPENROUTER_MODEL")


# ==================================================
# Generate Response
# ==================================================
def generate_response(prompt: str) -> dict:
    """
    Send a prompt to the LLM.

    Parameters
    ----------
    prompt : str
        Input prompt.

    Returns
    -------
    dict
        Generated response with metadata.
    """

    # Record start time
    start_time = time.perf_counter()

    # Send request
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    # Record end time
    end_time = time.perf_counter()

    # Calculate latency
    latency = round(end_time - start_time, 2)

    return {
        "model": MODEL_NAME,
        "latency_seconds": latency,
        "text": response.choices[0].message.content,
    }