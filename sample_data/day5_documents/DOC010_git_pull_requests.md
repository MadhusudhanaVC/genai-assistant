
---

### DOC010 — Git Pull Requests

File:

```text
---
document_id: DOC010
title: Git Pull Requests
category: Git
updated_at: 2026-08-10
---

# Git Pull Requests

A pull request is a way to propose changes from one branch for review before they are merged into another branch.

## Purpose

Pull requests allow team members to inspect code, discuss changes, and identify problems before the changes become part of the target branch.

## Creating a Pull Request

A developer normally pushes a feature branch to the remote repository and then creates a pull request through the repository platform.

## Code Review

Reviewers can examine the changed files and leave comments. The author can update the branch based on the review.

## Tests

Automated tests are often run when a pull request is opened. A pull request should normally be merged only when the required checks have passed.

## Good Pull Requests

A useful pull request has:

- a clear title
- a short description
- focused changes
- relevant tests
- no unrelated modifications

## Summary

Pull requests provide a structured way for teams to review and integrate changes safely.