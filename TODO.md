# TODO

Backlog for the `claude-playground` sandbox. Active in-flight work lives in session logs at `.claude/session-logs/`; this file is the long-lived list.

## Skills / hooks
- [ ] Build a "Session Log" skill (formalize the workflow currently in `.claude/session-logs/`) - on branch `new-skill-session-log`
- [x] ~~Build a "Breakdown to Decide" skill~~ — built on branch `new-skill-breakdown-to-decide` (spec `plans/2026-06-01-breakdown-to-decide-design.md`): skill + soft PreToolUse hook + 5 evals (iteration-2: 100% with-skill)
- [ ] Evals for `meetgeek-to-md` skill
- [ ] `breakdown-to-decide`: figure out the **plugin** packaging — bundle the skill **and** its PreToolUse hook as a Claude Code plugin (`.claude-plugin/plugin.json` + `skills/` + `hooks/hooks.json`, `${CLAUDE_PLUGIN_ROOT}`) so they install + activate together. Until then, install = copy the whole `.claude/skills/breakdown-to-decide` dir + register the hook manually (see the skill README "Shipping as a plugin"). Promotion plan: after squash-merge + push, copy the skill + hook to the global location.

## Hooks

- [ ] Hook: when Claude triggers `gh pr merge`, inject the merge-initiator note + `Co-Authored-By` trailer automatically. GitHub attributes squash commits to the authenticated user regardless of who triggered the merge.
- [ ] Migrate `gitignore-init` → Claude Code session-start hook
- [ ] Migrate `gitignore-checker` → PostToolUse hook on `.gitignore` Write/Edit


## Housekeeping

- [x] ~~Delete merged local branches~~ — done 2026-06-01 (6 squash-merged branches removed via `gh pr`-verified status)
