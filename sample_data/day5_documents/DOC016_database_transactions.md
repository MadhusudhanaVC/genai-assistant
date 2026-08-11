---
document_id: DOC016
title: Database Transactions
category: Database
updated_at: 2026-08-10
---

# Database Transactions

A database transaction groups related operations so that they can be treated as one unit of work.

## Commit

A transaction is committed when its changes should become permanent.

## Rollback

A rollback cancels changes made during the current transaction.

For example, if an application updates two related records and the second update fails, the first update may need to be rolled back.

## Atomic Operations

Transactions help maintain consistency when multiple database operations depend on each other.

## Error Handling

Applications should handle database errors carefully. After a failed transaction, the database session may need to be rolled back before another operation can continue.

## Practical Example

A money transfer is a common transaction example. Removing money from one account and adding it to another should succeed together or fail together.

## Summary

Transactions protect data consistency when an operation contains several related database changes.