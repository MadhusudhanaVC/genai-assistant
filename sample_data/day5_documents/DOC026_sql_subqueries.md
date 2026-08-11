
### DOC026_sql_subqueries.md

```markdown
---
document_id: DOC026
title: SQL Subqueries
category: SQL
updated_at: 2026-08-10
---

# SQL Subqueries

A subquery is a query placed inside another SQL query.

## Example

A subquery can be used to find employees whose salary is higher than the average salary.

```sql
SELECT name, salary
FROM employees
WHERE salary > (
    SELECT AVG(salary)
    FROM employees
);