from app.llm.validator import validate_response


response = """
{
    "answer": "A variable stores a value.",
    "status": "answered",
    "citations": [
        "[DOC001 | DOC001_CHUNK_001]"
    ]
}
"""


result = validate_response(
    "grounded_answer",
    response,
)

print(result)