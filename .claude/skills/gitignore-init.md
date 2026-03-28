---
name: gitignore-init
description: Apply when first exploring or reading files in a repo. Checks if a .gitignore file exists and creates one with required entries if it does not.
user-invocable: false
---

# .gitignore Init

When first exploring or reading files in a repo, check if a `.gitignore` file exists at the repo root.

## Steps

1. Check if `.gitignore` exists at the repo root.
2. If it exists, do nothing — the `gitignore-checker` skill handles validation.
3. If it does not exist, create an empty `.gitignore` file at the repo root, then run the `gitignore-checker` skill to populate it with the required entries.
4. Inform the user that a `.gitignore` was created.
