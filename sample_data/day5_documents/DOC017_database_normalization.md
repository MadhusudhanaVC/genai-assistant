---
document_id: DOC017
title: Database Normalization
category: Database
updated_at: 2026-08-10
---

# Database Normalization

Normalization is a database design approach that reduces unnecessary duplication and improves data consistency.

## Repeated Data

Suppose a customer address is stored in every order record. Updating the customer's address would require changing many rows.

Separating customer information into its own table can reduce this duplication.

## First Normal Form

First normal form generally requires values to be stored in a structured form rather than keeping multiple unrelated values inside one field.

## Second Normal Form

Second normal form addresses dependencies on part of a composite key.

## Third Normal Form

Third normal form removes certain dependencies between non-key attributes.

## Practical Balance

Highly normalized designs are not always necessary for every system. Developers should consider the application's query patterns, performance needs, and data relationships.

## Summary

Normalization helps create consistent relational data structures and reduces problems caused by duplicated information.