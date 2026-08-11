---
document_id: DOC003
title: Python Exception Handling
category: Python
updated_at: 2026-08-10
---

# Python Exception Handling

Exceptions occur when a program encounters an unexpected situation while running. Python provides `try`, `except`, `else`, and `finally` blocks for handling these situations.

## Try and Except

Code that may raise an exception can be placed inside a `try` block.

```python
try:
    number = int(user_input)
except ValueError:
    print("Please enter a valid number.")