# gitignore-checker

**Maturity:** v0.1 | **Type:** Automatic

Silently ensures `.DS_Store` and `.env` are present in every `.gitignore`. Triggers whenever Claude reads, creates, or edits a `.gitignore` — no user action required.

If entries are missing, appends them. No duplicates added.

## Next Steps

This should be a Claude Code hook (PostToolUse on Write/Edit targeting `.gitignore`), not a skill — deterministic file operations are more reliable and cheaper as hooks. Skill implementation works for now.
