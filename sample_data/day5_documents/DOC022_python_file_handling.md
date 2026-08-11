
### DOC022_python_file_handling.md

```markdown
---
document_id: DOC022
title: Python File Handling
category: Python
updated_at: 2026-08-10
---

# Python File Handling

Python provides built-in functions for reading and writing files.

## Opening a File

The `open` function can be used to access a file.

```python
with open("notes.txt", "r", encoding="utf-8") as file:
    content = file.read()