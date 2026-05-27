# session-report skill override

**Caveat emptor**
> **Status:** v0.1 — experimental
> **Requires:** the `session-report` plugin from the Claude plugins marketplace
> **Output path:** hardcoded to `<your-output-dir>` — edit SKILL.md before use

---

## What this demonstrates

How to create a **project-scoped skill override** that shadows a global Claude Code plugin. Place a `SKILL.md` in `.claude/skills/<skill-name>/` within a project and Claude will use it instead of the installed plugin — only for that project. Other projects continue using the global version.

This override saves session-report output to a fixed directory (`<your-output-dir>`) instead of the current working directory, and keeps the plugin's analyzer and template working via absolute paths.

## Why absolute paths

The original plugin uses `<skill-dir>` as a placeholder Claude resolves to the active SKILL.md's directory. Since this override lives in the project's `.claude/skills/session-report/`, `<skill-dir>` would point here — but `analyze-sessions.mjs` and `template.html` remain in the plugin directory. Absolute paths to those files keep them working correctly.

## Trade-offs

- **Plugin updates won't propagate.** If the upstream plugin's SKILL.md changes, this override silently ignores those changes. Check and merge manually if things seem stale.
- **Absolute paths are fragile.** If the plugin is reinstalled or the marketplace directory structure changes, the hardcoded paths to `analyze-sessions.mjs` and `template.html` will break. Not obvious to diagnose, but straightforward to fix.
