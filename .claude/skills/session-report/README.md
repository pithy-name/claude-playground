# session-report skill override

This file shadows the plugin at:
`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/session-report/skills/session-report/SKILL.md`

This override is project-scoped (lives in `.claude/skills/` within the `claude-playground` repo), so it only applies when the skill is run from within this project. Other projects use the global plugin version.

## Why absolute paths

The original skill uses `<skill-dir>` as a placeholder that Claude resolves to the directory containing the active SKILL.md. Since this override lives in the project's `.claude/skills/session-report/`, `<skill-dir>` would point here — but `analyze-sessions.mjs` and `template.html` are still in the plugin directory. Absolute paths to those files are used in SKILL.md to keep them working correctly.

## Why this override exists

Configured to save reports to `~/dev/pithy-name` instead of the current working directory.

## Trade-offs

- **Plugin updates won't propagate.** If the upstream plugin's SKILL.md is updated, this override silently ignores those changes. Check and merge manually if things seem stale.
- **Absolute paths are fragile.** If the plugin is reinstalled or the marketplace directory structure changes, the hardcoded paths to `analyze-sessions.mjs` and `template.html` will break. Not obvious to diagnose, but straightforward to fix.
