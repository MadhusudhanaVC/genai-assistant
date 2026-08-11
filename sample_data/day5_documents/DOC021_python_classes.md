---
document_id: DOC021
title: Python Classes
category: Python
updated_at: 2026-08-10
---

# Python Classes

Classes provide a way to group related data and behavior into reusable objects.

## Creating a Class

A class is defined with the `class` keyword.

```python
class Student:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"My name is {self.name}"