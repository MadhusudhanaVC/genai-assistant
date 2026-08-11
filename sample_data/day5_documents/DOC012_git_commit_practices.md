
---

### DOC012 — Git Commit Practices

**File:** `DOC012_git_commit_practices.md`

```markdown
---
document_id: DOC012
title: Git Commit Practices
category: Git
updated_at: 2026-08-10
---

# Git Commit Practices

A commit represents a small, meaningful point in the history of a project.

## Keep Commits Focused

A commit should normally contain changes related to one task. Mixing unrelated changes makes the history harder to understand.

## Write Clear Messages

A commit message should explain what was changed.

For example:

```text
git commit -m "Add document preprocessing"