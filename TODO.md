# TODO

Backlog for the `claude-playground` sandbox. Active in-flight work lives in session logs at `.claude/session-logs/`; this file is the long-lived list.

## Skills / hooks
- [ ] Build a "Session Log" skill (formalize the workflow currently in `.claude/session-logs/`) - on branch `new-skill-session-log`
- [x] ~~Build a "Breakdown to Decide" skill~~ — built on branch `new-skill-breakdown-to-decide` (spec `plans/2026-06-01-breakdown-to-decide-design.md`): skill + soft PreToolUse hook + 5 evals (iteration-2: 100% with-skill)
- [ ] Evals for `meetgeek-to-md` skill

## Hooks

- [ ] Hook: when Claude triggers `gh pr merge`, inject the merge-initiator note + `Co-Authored-By` trailer automatically. GitHub attributes squash commits to the authenticated user regardless of who triggered the merge.
- [ ] Migrate `gitignore-init` → Claude Code session-start hook
- [ ] Migrate `gitignore-checker` → PostToolUse hook on `.gitignore` Write/Edit


## Housekeeping

- [x] ~~Delete merged local branches~~ — done 2026-06-01 (6 squash-merged branches removed via `gh pr`-verified status)
