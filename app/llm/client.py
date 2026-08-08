import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

MODEL_NAME = os.getenv("OPENROUTER_MODEL")


def generate_response(prompt: str) -> dict:
    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    latency = round(time.perf_counter() - start_time, 2)

    return {
        "model": MODEL_NAME,
        "latency_seconds": latency,
        "text": response.choices[0].message.content,
    }