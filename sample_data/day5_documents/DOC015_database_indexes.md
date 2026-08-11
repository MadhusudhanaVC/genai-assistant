
---

### DOC015 — Database Indexes

**File:** `DOC015_database_indexes.md`

```markdown
---
document_id: DOC015
title: Database Indexes
category: Database
updated_at: 2026-08-10
---

# Database Indexes

An index helps a database find rows more efficiently. It is similar to an index in a book because it provides a faster way to locate specific information.

## Why Indexes Help

Without a suitable index, the database may need to examine many rows to find matching records.

An index can improve queries that frequently filter or sort using a particular column.

## Example

An index on an email column may help an application quickly find a customer by email address.

```sql
CREATE INDEX idx_customer_email
ON customers(email);