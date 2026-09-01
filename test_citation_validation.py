from app.rag.generate import validate_citations


results = [
    {
        "document_id": "DOC001",
        "chunk_id": "DOC001_CHUNK_001",
    },
    {
        "document_id": "DOC002",
        "chunk_id": "DOC002_CHUNK_001",
    },
]


citations = [
    "[DOC001 | DOC001_CHUNK_001]",
    "[DOC999 | DOC999_CHUNK_001]",
]


validated = validate_citations(
    citations=citations,
    results=results,
)

print("Validated citations:")
print(validated)