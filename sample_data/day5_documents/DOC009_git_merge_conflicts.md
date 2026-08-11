# Git Merge Conflicts

A merge conflict occurs when Git cannot automatically combine changes from different branches.

## Why Conflicts Happen

Conflicts commonly occur when two branches modify the same part of a file in different ways.

## Conflict Markers

Git places special markers around sections that need manual attention.

A conflict shows the content from the current branch, separates it from the incoming content, and marks the end of the conflicting section.

For example:

```text
current branch content
----------------------
incoming branch content