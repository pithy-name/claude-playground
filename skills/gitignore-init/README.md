# gitignore-init

**Maturity:** v0.1 | **Type:** Automatic

Creates a `.gitignore` at the repo root if one doesn't exist. Triggers on first repo exploration — no user action required.

If a `.gitignore` already exists, does nothing (delegates validation to `gitignore-checker`).

## Next Steps

This should be a Claude Code hook (session-start), not a skill — deterministic file operations are more reliable and cheaper as hooks. Skill implementation works for now.
