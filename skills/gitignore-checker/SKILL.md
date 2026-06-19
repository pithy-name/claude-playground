---
name: gitignore-checker
description: Apply when reading, creating, or editing any .gitignore file. Ensures required entries are always present.
user-invocable: false
---

# .gitignore Checker

Whenever you read, create, or edit a `.gitignore` file, ensure the following entries are present:

```
.DS_Store
.env
```

## Steps

1. Read the current `.gitignore` contents (if it exists).
2. Check which of the required entries above are missing.
3. If any are missing, add them — append at the end of the file.
4. Do not add duplicates if an entry already exists (including commented-out variants).
5. Silently fix any missing entries without asking the user unless the file does not exist yet, in which case create it with all required entries.
