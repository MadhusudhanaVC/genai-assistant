
### DOC028_database_views.md

```markdown
---
document_id: DOC028
title: Database Views
category: Database
updated_at: 2026-08-10
---

# Database Views

A database view is a saved query that can be accessed like a table.

## Creating a View

A view can combine information from one or more tables.

```sql
CREATE VIEW active_employees AS
SELECT employee_id, name
FROM employees
WHERE status = 'active';