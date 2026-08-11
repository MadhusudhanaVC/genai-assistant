from app.rag.chunking import clean_text, split_sections, chunk_text


def test_clean_text_normalizes_line_endings():
    text = "Hello\r\n\r\nWorld\r\n"
    result = clean_text(text)

    assert result == "Hello\n\nWorld"


def test_clean_text_removes_excess_blank_lines():
    text = "Hello\n\n\n\nWorld"
    result = clean_text(text)

    assert result == "Hello\n\nWorld"


def test_split_sections_uses_markdown_headings():
    text = """# Introduction

This is the introduction.

## Variables

Variables store values.

## Functions

Functions organize reusable logic.
"""

    sections = split_sections(text)

    assert len(sections) == 3
    assert sections[0].startswith("# Introduction")
    assert sections[1].startswith("## Variables")
    assert sections[2].startswith("## Functions")


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("") == []


def test_chunk_text_keeps_small_document_as_one_chunk():
    text = """# Python Basics

Python is a programming language.

## Variables

Variables store values.
"""

    chunks = chunk_text(
        text,
        chunk_size=500,
        overlap=80,
    )

    assert len(chunks) == 1
    assert "# Python Basics" in chunks[0]
    assert "## Variables" in chunks[0]


def test_chunk_text_splits_large_content():
    text = "# Large Document\n\n" + ("Python programming content. " * 50)

    chunks = chunk_text(
        text,
        chunk_size=200,
        overlap=40,
    )

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_chunk_text_rejects_invalid_chunk_size():
    try:
        chunk_text("test", chunk_size=0, overlap=0)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "chunk_size" in str(error)


def test_chunk_text_rejects_invalid_overlap():
    try:
        chunk_text("test", chunk_size=100, overlap=100)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "overlap" in str(error)