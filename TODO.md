# TODO

Backlog for the `claude-playground` sandbox. Active in-flight work lives in session logs at `~/.claude/session-logs/<repo>/`; this file is the long-lived list.

## Skills / hooks
- [x] ~~Build a "Session Log" skill~~ — built on branch `new-skill-session-log`; shipped to `main` (#9, #10); lives at `skills/session-log/`, installed globally
- [x] ~~Build a "Breakdown to Decide" skill~~ — built on branch `new-skill-breakdown-to-decide` (spec `plans/2026-06-01-breakdown-to-decide-design.md`): skill + soft PreToolUse hook + 5 evals (iteration-2: 100% with-skill)
- [ ] Evals for `meetgeek-to-md` skill
- [ ] Build a cross-project memory-curation skill. Gap: auto-memory (`~/.claude/projects/<repo>/memory/`) is per-repo with no built-in promotion, and global `~/.claude/CLAUDE.md` is the only cross-project surface — so broadly-useful memories get stuck in one repo. Skill would scan `~/.claude/projects/*/memory/*.md`, flag global-promotion candidates (generic feedback, no project-specific nouns), and help move them (keep global <200 lines). Also leverage `.claude/rules/` symlinks to share rule-sets across repos without duplication. No existing tool does this (`claude-automation-recommender` / `claude-md-improver` only touch CLAUDE.md files).
- [ ] `breakdown-to-decide`: figure out the **plugin** packaging — bundle the skill **and** its PreToolUse hook as a Claude Code plugin (`.claude-plugin/plugin.json` + `skills/` + `hooks/hooks.json`, `${CLAUDE_PLUGIN_ROOT}`) so they install + activate together. Until then, install = copy the whole `skills/breakdown-to-decide` dir + register the hook manually (see the skill README "Shipping as a plugin"). (Already installed globally — `~/.claude/skills/breakdown-to-decide` + global hook.)

## Hooks

- [ ] Hook: when Claude triggers `gh pr merge`, inject the merge-initiator note + `Co-Authored-By` trailer automatically. GitHub attributes squash commits to the authenticated user regardless of who triggered the merge.
- [ ] Migrate `gitignore-init` → Claude Code session-start hook
- [ ] Migrate `gitignore-checker` → PostToolUse hook on `.gitignore` Write/Edit


## Housekeeping

- [x] ~~Delete merged local branches~~ — done 2026-06-01 (6 squash-merged branches removed via `gh pr`-verified status)
- [ ] Re-sync repo skill edits to the global copies — `skills/session-log` + `skills/breakdown-to-decide` README maturity (→ v1.0) and hardened hook-setup docs diverged from `~/.claude/skills/` during the top-level restructure (doc-only; SKILL.md + hooks unchanged, so runtime is unaffected). Re-copy after #11 merges.
