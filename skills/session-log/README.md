# session-log

> A Claude Code skill that keeps a clean, machine-readable **Session Log** for every coding session — so you can run a retro or post-mortem without re-reading the whole transcript.

**Maturity:** v1.0 · **Type:** Hybrid (auto-creates at session start via a hook + updates by the skill)

---

## What it is

A skill + two hooks that create and maintain one markdown **Session Log** per session — an executive record of what happened, what you decided, what went wrong, what went right, and what you learned. It's a substitute for scrolling back through a long transcript, and the raw material for retros.

## The problem it solves

By the end of a long session, can you still say which decisions you made when, or where the dead-ends were? Notes-as-you-go would fix that — but the discipline (consistent structure, real timestamps, append-don't-reorder, *actually capturing the learnings*) is tedious and the first thing to slip. This skill makes it automatic and enforces a structure a script can parse.

## Components

| Piece | What it does |
|------|--------------|
| `SKILL.md` | The operational core — when it runs, the format, the rules. |
| `references/format-spec.md` | Full per-section depth, the close checklist, a worked example. |
| `references/validated-patterns.md` | Situational playbook — apply a pattern when its situation arises. |
| `scripts/parse_session_log.py` | Deterministic parser — both the reference implementation and the format's test. |
| `scripts/session_start.sh` | `SessionStart` hook — auto-creates the log (idempotent; resume-safe). |
| `scripts/inject_timestamp.sh` | `PreToolUse` hook — surfaces the real clock time so timestamps are never guessed. |
| `governance/` | Optional, opt-in health-check (launchd-scheduled) that audits the logs and verdicts **GREEN/RED** on whether the skill has been dogfooded enough to drop the old backup guidance — experimental. See `governance/README.md`. |

Logs are written **centrally** to `~/.claude/session-logs/<repo>/` — outside any repo, so there's no per-project `.gitignore` and no risk of committing private notes to a public repo.

## Install

**1. Copy the skill.**

- *One project:* put this folder at `<repo>/.claude/skills/session-log/`.
- *All projects (globalize):* put it at `~/.claude/skills/session-log/`.

**2. Register the two hooks (required — the skill is inert without them).** Add them to your `settings.json`'s `hooks` block, pointing at wherever you copied the skill. **Merge** — don't overwrite the file:
- For one project: add to `.claude/settings.json`, with `${CLAUDE_PROJECT_DIR}` in the command paths
- For all projects: add to `~/.claude/settings.json`, with `$HOME` instead (as shown below)

```jsonc
{
  "hooks": {
    "SessionStart": [
      { "matcher": "startup", "hooks": [{ "type": "command", "command": "bash \"$HOME/.claude/skills/session-log/scripts/session_start.sh\"" }] },
      { "matcher": "resume",  "hooks": [{ "type": "command", "command": "bash \"$HOME/.claude/skills/session-log/scripts/session_start.sh\"" }] }
    ],
    "PreToolUse": [
      { "matcher": "Write|Edit", "hooks": [{ "type": "command", "command": "bash \"$HOME/.claude/skills/session-log/scripts/inject_timestamp.sh\"" }] }
    ]
  }
}
```

Then run `/hooks` (or restart Claude Code) so it loads them. Requires `python3` and `bash` (both standard on macOS/Linux). **Verify:** start a new session — it should create a log at `~/.claude/session-logs/<repo>/<timestamp>-session.md`.

## How to use

Mostly it just runs. The `SessionStart` hook creates the log; the skill updates it at milestones and at close. To nudge it explicitly, say things like **"update the session log"**, **"capture our learnings"**, **"last call"**, or **"wrap up"**. Each log looks like:

```markdown
# Session Log — <topic>

**Started:** 2026-05-18 14:02 PT
**Session ID:** <id>
**Goal:** one line.

## What happened
## Decisions & trade-offs
## Learnings
### Mistakes & corrections
### What worked & what to repeat
### User preferences & conventions
## Update 2026-05-18T14:02 PT   ← timestamped, append-only
## To-do
```

---

## How it works

Work is split by reliability: **deterministic bits → hooks, judgment bits → the skill.**

- **[`SessionStart` hook](https://code.claude.com/docs/en/agent-sdk/hooks)** creates the log at session start, keyed on session ID so a resume reuses the same file (one log dir per repo, shared across worktrees).
- **`PreToolUse` hook** injects the real clock time into context before each `Write`/`Edit`, so Update-block timestamps come from the clock, not a guess. (There's deliberately **no** ordering-lint hook — chronological order is emergent from real timestamps + the append-at-end rule.)
- **The skill** owns the judgment: the full-session scan, section depth, the close audit, and the *update-discipline* (walk every section, don't skip Learnings).
- **Machine-readable acceptance criterion:** the format is parseable without an LLM. `scripts/parse_session_log.py <file>` exits 0 on a conforming log and non-zero (with the reason) otherwise — it's both the spec and the test.

## How it was built

Designed as a PRD + format spec (two red-team passes each), then built and validated with the `skill-creator` eval loop (with-skill vs. baseline subagents across create / update / close / accumulate cases). The parser ships with a self-test + a negative-case battery. Known eval limitation (the harness can't reproduce the real-world "Learnings-skip") is documented in `evals/README.md`.

## Future Improvements

### Shipping it as a plugin

To distribute beyond a single machine, package it as a Claude Code plugin: place the skill under a plugin's `skills/` directory (with the hook registration in the plugin's settings) and share via a plugin marketplace or git repo — or produce a portable `.skill` bundle with skill-creator's `package_skill.py`. End users then get the skill + hooks without manual copying.
