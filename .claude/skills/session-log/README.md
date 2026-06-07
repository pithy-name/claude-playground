# session-log

**Maturity:** Experimental | **Type:** Hybrid (auto-create at session start + manual updates)

Creates and maintains a **Session Log** — a per-session posterity record and executive TL;DR that substitutes for re-reading the whole transcript, and the source material for retros and post-mortems.

## What it produces

One Session Log markdown file per session, stored **centrally** at `~/.claude/session-logs/<repo>/YYYY-MM-DDTHHMM-topic.md` — outside any repo, so no per-project `.gitignore` and no public-repo leak risk (date+time prefix, `T`-separated, no colon/TZ; by session start). The body uses a `# Session Log — <topic>` header with `Started` / `Session ID` / `Goal` metadata, a `## Learnings` group (Mistakes & corrections / What worked & what to repeat / User preferences & conventions), append-only timestamped Update blocks, and a To-do list — all parseable without an LLM.

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

Distinct from Claude's *native scratchpad* concept (an internal Claude thing). The format is tuned for retros and post-mortems — it captures both what went wrong (to stop) and what went right (to repeat).

## Authority

This skill is the single source of truth for Session Log conventions. If you also keep session/scratchpad rules in a `CLAUDE.md`, let this skill supersede them — one authority means no competing copy and no drift.

## Usage

Largely automatic: the `SessionStart` hook creates the file; the skill triggers at milestones and at close. Invoke explicitly with "update the session log", "last call", or by naming the Session Log.
