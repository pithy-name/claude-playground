---
name: session-log
description: >-
  Create and maintain a Session Log — a per-session posterity record and executive
  TL;DR that substitutes for re-reading the whole transcript, used for retros and
  post-mortems. Use this skill whenever a session starts, at meaningful milestones
  (a decision is confirmed, a deliverable is written, a mistake is caught and
  corrected, a win is worth repeating, a memory file is saved, research yields a
  significant finding), and at session close. Trigger it whenever the user says
  "update the session log", "capture our learnings", "capture that in the log",
  "last call", "wrap up", or otherwise signals the session is ending, and whenever a
  Session Log file is mentioned. It keeps the required sections, append-only
  timestamped Update blocks, and a To-do list in a format that stays
  machine-parseable without an LLM.
---

# Session Log

A **Session Log** is a per-session posterity record with an executive top. It substitutes for reading the whole transcript: a future reader (or a future Claude) grasps what was accomplished, decided, and learned in ~30 seconds, then drills into the supporting depth. It is also the source material for **retros and post-mortems** — so it must capture both where things went *wrong* (to stop) and where they went *right* (to repeat).

> **Naming:** the **Session Log** is the artifact; **`session-log`** is this skill; **`~/.claude/session-logs/<repo>/`** is the directory (central, outside any repo). Distinct from Claude's *native scratchpad* (an internal Claude concept).

## When this skill runs

Hybrid — deterministic bits owned by hooks, judgment bits by this skill:

- **Session start** — a `SessionStart` hook auto-creates the log file, stamped with the start date/time + session ID. If no hook is active yet, create it yourself early; don't wait for close. When you create or first touch the log, say so briefly ("Creating the session log now…") and note any section you're deliberately leaving empty ("leaving Decisions empty until we make one").
- **Throughout** — update at milestones (see *Incremental update triggers*). This is the core job.
- **Session close** — run the close audit when the user signals the end.

## File location & naming

`~/.claude/session-logs/<repo>/YYYY-MM-DDTHHMM-topic.md`

- **Location = central, outside any repo.** Logs live under `~/.claude/session-logs/`, in a per-repo subdir (`<repo>` = the repo's dir name, shared across its worktrees). This keeps logs off public repos entirely — no per-project `.gitignore`, no leak risk. The `SessionStart` hook resolves the path.
- Prefix = **session start date + time**, 24h local, `T`-separated, no colon, no timezone — e.g. `2026-06-06T1542-`. (The colon/TZ live *inside* the doc, not the filename.) The time prefix keeps same-repo sessions from colliding.
- Topic = short kebab-case descriptor of the session's main work. The `SessionStart` hook creates a `-session` placeholder; rename to the real topic once it's clear.
- **Never overwrite an existing Session Log.** The hook keys idempotency on the session ID, so a resume reuses the same file.

## The format

Required structure, in this exact order. Headings are a **fixed enum** — a deterministic parser depends on them being present and spelled exactly. Note the blank line after `## Learnings`.

```markdown
# Session Log — [Topic]

**Started:** YYYY-MM-DD HH:MM TZ
**Session ID:** <id>
**Goal:** one line — what this session set out to do.

## What happened

## Decisions & trade-offs

## Learnings

### Mistakes & corrections

### What worked & what to repeat

### User preferences & conventions

[...timestamped Update blocks go here, in chronological order...]

## To-do
```

Depth rules + worked examples live in **`references/format-spec.md`** — read it before writing a log for the first time. The short version:

- **Header** — `# Session Log — [Topic]` (no date in the H1). Then `**Started:**` (date + time + TZ), `**Session ID:**`, `**Goal:**` (one line).
- **What happened** — bulleted executive overview; add in-place as you go, don't batch at close. Refresh into arcs + a "Final state" line at close.
- **Decisions & trade-offs** — one **bold-heading** entry per decision, each with bullets: `Options considered:` (list alternatives), `Chosen:`, `Why:` (tie to the goal), and `Implication:` *(optional — include when the downstream consequence isn't obvious)*.
- **Learnings** (H2) — groups the three kinds of learning below. When the user says "capture learnings," that means **all three** subsections, not just the user one.
  - **### Mistakes & corrections** — the bold triplet `**Symptom:** / **Root cause:** / **Correct approach:**`; capture meta-failures.
  - **### What worked & what to repeat** — `**<win>**`, then `Why it worked:` **on its own line**, then `Repeat:`; quantify the payoff when estimable.
  - **### User preferences & conventions** — each tagged with the **observable signal** that revealed it; actionable + specific; mark session-scoped ones `*(session-log-only, not promoted to memory)*`.
- **To-do** — `- [ ]` for open; `- [x] ~~strikethrough~~ done` for completed (keep the checkbox **and** strike the text; never delete). Always the last section.

## Update discipline — the rule that's easiest to skip

When you update the log, **walk every section top-to-bottom and add wherever the new info is relevant — do not stop after What happened + Decisions.** The most-skipped section is **Learnings** (all three subsections). Before you call an update done, ask explicitly: *did this milestone produce a mistake, a win, or a user-preference signal?* If yes, it goes in the matching Learnings subsection. A milestone usually touches several sections at once.

**Append in chronological order at the END of every section** (oldest→newest) — not just Update blocks. Never anchor a new entry *above* an older one just because that string is convenient to edit; that silently reorders the section and misrepresents how the thinking evolved.

## Update blocks (the timeline)

Append-only, chronological snapshots of work *between* updates. They sit immediately above To-do.

```markdown
## Update YYYY-MM-DDTHH:MM TZ
```

- **One canonical timestamp format**, exactly: `YYYY-MM-DDTHH:MM TZ`, 24-hour, local timezone, with the `T` and the colon and the TZ label (e.g. `## Update 2026-06-06T15:32 PT`). The parser keys off this — don't vary it. (This is the *in-doc* format; the filename is the colon-less variant.)
- **Accurate, never guessed** — take the time from the `date`-backed hook (or run `date "+%Y-%m-%dT%H:%M %Z"`).
- **Append at the END in chronological order. Never insert above an existing block.** If you must backfill, write a single retroactive Update saying the exact time wasn't captured; don't fabricate a timestamp.
- **Use for:** files written, memory saved, CLAUDE.md modified, todos crossed off, significant findings, decisions made/changed (with the time), **research/investigation conducted, and the prep or exploration that led to a milestone — the path to it, not only the milestone**. The effort *between* artifacts is what makes pacing analysis possible.
- **Don't restate thematic content here** — a decision belongs in Decisions; the Update just notes it happened and when.

## Incremental update triggers

Update immediately — don't batch — when any of these happen. In a long session you can't reliably scroll back; reconstruction at close drops things.

- A decision is confirmed; a significant finding changes understanding; a plan/spec file is created or modified; a user correction or rejected tool call; a to-do completed; a deliverable written; a persistent memory file written.

**Logging memory writes** — when a persistent memory file is written, log it with its path:

```
- Written to persistent memory:
  - ~/.claude/projects/<project-slug>/memory/<filename>.md — one-line description
```

## On resume / after compaction

Orient before executing: re-read the current log end-to-end, verify actual state (don't trust a summary's "next step"), check in with the user before running anything. Write only confirmed, directly-observed facts — never assumptions, not even hedged. Absolute dates only.

## Session close

When the user signals close ("last call", "wrap up", "anything else?"), audit before confirming done. Full checklist in **`references/format-spec.md`**; essentials:

- "What happened" refreshed into arcs + a "Final state" line.
- Every decision has Options/Chosen/Why; every mistake has root cause + "Correct approach:"; every win has "Why it worked:"; every user-preference has its observable signal.
- **Learnings actually populated** — don't leave the three subsections empty if the session produced any.
- Memory writes logged; todos current (`- [x] ~~…~~` for done); a final `## Update` block; no duplicate timestamps.
- **Stale-claim audit** — re-verify carry-forward claims ("X still on disk") with a quick `ls`/`cat`.
- `decisions.md` promotion reviewed — *only if the project has one*.

## Hard acceptance criterion — machine-readable without an LLM

A conforming log must be parseable deterministically (no model call): topic, Started, Session ID, Goal, every required H2, the three H3 subsections under Learnings, every Update block in chronological order, and the To-do items — with zero manual fixup. The bundled parser **`scripts/parse_session_log.py`** is the reference implementation and the test:

```
python3 scripts/parse_session_log.py <path-to-session-log.md>
```

Exit 0 = conforms. Non-zero = a required field didn't parse — fix the log, don't ship it.

## Situational playbook

**`references/validated-patterns.md`** holds situational patterns (arc-grouping, parallel-session orchestration, cross-list renumbering, etc.) — apply each only when its situation arises. The unifying idea: a Session Log is a deliberate artifact whose structure can be *improved* within a session, not a fixed template to fill in.
