# session-log

**Maturity:** Experimental | **Type:** Hybrid (auto-create at session start + manual updates)

Creates and maintains a **Session Log** — a per-session posterity record and executive TL;DR that substitutes for re-reading the whole transcript, and the source material for retros and post-mortems.

## What it produces

One Session Log markdown file per session in `.claude/session-logs/`, named `YYYY-MM-DD-topic.md` (dated by session start). The format keeps required sections, append-only timestamped Update blocks, and a To-do list — all parseable without an LLM.

## Structure

```
session-log/
├── SKILL.md                          operational core: when it runs, the format, the rules
├── README.md                         this file
├── references/
│   ├── format-spec.md                full per-section depth, examples, close checklist, reference example
│   └── validated-patterns.md         situational playbook (apply when the situation arises)
└── scripts/
    └── parse_session_log.py          deterministic parser — the reference impl + the acceptance test
```

## Hooks (ship alongside the skill)

Two hooks split the deterministic work off from the judgment work:

- **`SessionStart`** — auto-create the session's log file if absent, stamped with the session-start date.
- **`PreToolUse` on `Write|Edit`** — surface a fresh `date`-backed timestamp so Update-block times are never guessed.

See the project's `.claude/settings.json`. There is deliberately **no ordering-lint hook** — chronological order is emergent from real timestamps + the append-at-end rule.

## Acceptance test

```
python3 scripts/parse_session_log.py <path-to-session-log.md>
```

Exit 0 + full JSON extraction = the log conforms to the machine-readable acceptance criterion. Non-zero = a required field didn't parse.

## Provenance

Derived from the Session Log format spec + PRD (two red-team passes each). Distinct from Claude's *native scratchpad* concept. Supersedes the `session-journal` experiment in this repo.

## Authority

Once live, this skill is the single source of truth for Session Log conventions, replacing the (to-be-removed) CLAUDE.md "Session Management" section. One authority = no competing copy = no drift.

## Usage

Largely automatic: the `SessionStart` hook creates the file; the skill triggers at milestones and at close. Invoke explicitly with "update the session log", "last call", or by naming the Session Log.
