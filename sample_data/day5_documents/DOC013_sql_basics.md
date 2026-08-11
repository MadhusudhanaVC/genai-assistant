
---

### DOC013 — SQL Basics

**File:** `DOC013_sql_basics.md`

```markdown
---
document_id: DOC013
title: SQL Basics
category: Database
updated_at: 2026-08-10
---

# SQL Basics

SQL is used to work with data stored in relational databases.

## Tables

A relational database stores information in tables. A table contains rows and columns.

For example, a `customers` table might contain customer IDs, names, and email addresses.

## Selecting Data

The `SELECT` statement retrieves data.

```sql
SELECT name, email
FROM customers;