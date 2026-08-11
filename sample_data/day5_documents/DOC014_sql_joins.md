
---

### DOC014 — SQL Joins

**File:** `DOC014_sql_joins.md`

```markdown
---
document_id: DOC014
title: SQL Joins
category: Database
updated_at: 2026-08-10
---

# SQL Joins

SQL joins combine related information from multiple tables.

## Inner Join

An inner join returns rows where matching values exist in both tables.

```sql
SELECT customers.name, orders.order_id
FROM customers
INNER JOIN orders
    ON customers.id = orders.customer_id;