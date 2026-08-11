
### DOC023_python_logging.md

```markdown
---
document_id: DOC023
title: Python Logging
category: Python
updated_at: 2026-08-10
---

# Python Logging

Logging helps developers record useful information about what an application is doing.

## Basic Logging

Python includes the `logging` module for creating application logs.

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Application started")
logging.warning("Configuration is missing")