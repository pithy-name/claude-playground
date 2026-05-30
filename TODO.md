# TODO

Backlog for the `claude-playground` sandbox. Active in-flight work lives in session logs at `.claude/session-logs/`; this file is the long-lived list.

## Skills / hooks

- [ ] Migrate `gitignore-init` → Claude Code session-start hook
- [ ] Migrate `gitignore-checker` → PostToolUse hook on `.gitignore` Write/Edit
- [ ] Build a "Session Log" skill (formalize the workflow currently in `.claude/session-logs/`)
- [ ] Evals for `meetgeek-to-md` skill

## Claude Code integration

- [ ] Hook: when Claude triggers `gh pr merge`, inject the merge-initiator note + `Co-Authored-By` trailer automatically. GitHub attributes squash commits to the authenticated user regardless of who triggered the merge.

## Housekeeping

- [ ] Delete merged local branches: `publish-meetgeek-to-md-skill`, `custom_session_report`, `v0.1-docs-pass`, `new_skill-session_journal`, `publish-tools`
