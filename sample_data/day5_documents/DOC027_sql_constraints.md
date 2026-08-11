
### DOC027_sql_constraints.md

```markdown
---
document_id: DOC027
title: SQL Constraints
category: SQL
updated_at: 2026-08-10
---

# SQL Constraints

SQL constraints are rules applied to table columns to protect data quality.

## Common Constraints

Common constraints include PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK, and DEFAULT.

```sql
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    age INTEGER CHECK (age >= 18)
);