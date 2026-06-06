---
name: session-log
description: >-
  Create and maintain a Session Log — a per-session posterity record and executive
  TL;DR that substitutes for re-reading the whole transcript, used for retros and
  post-mortems. Use this skill whenever a session starts, at meaningful milestones
  (a decision is confirmed, a deliverable is written, a mistake is caught and
  corrected, a win is worth repeating, a memory file is saved, research yields a
  significant finding), and at session close. Trigger it whenever the user says
  "update the session log", "last call", "closing", "wrap up", or otherwise signals
  the session is ending, and whenever a Session Log file is mentioned. It keeps the
  required sections, append-only timestamped Update blocks, and a To-do list in a
  format that stays machine-parseable without an LLM.
---

# Session Log

A **Session Log** is a per-session posterity record with an executive top. It substitutes for reading the whole transcript: a future reader (or a future Claude) grasps what was accomplished, decided, and learned in ~30 seconds, then drills into the supporting depth only if needed. It is also the source material for **retros and post-mortems** — so it must capture both where things went *wrong* (to stop) and where they went *right* (to repeat).

> **Naming:** the **Session Log** is the artifact; **`session-log`** is this skill; **`.claude/session-logs/`** is the directory. This is distinct from Claude's *native scratchpad* (an internal Claude concept) — they are not the same thing.

## When this skill runs

Hybrid model — deterministic bits are owned by hooks, judgment bits by this skill:

- **Session start** — a `SessionStart` hook auto-creates the log file for the session, stamped with the session-start date. If no hook is active yet (a project not set up, or while building this skill), create the file yourself early; do not wait until close.
- **Throughout** — update the log at milestones (see *Incremental update triggers*). This is the skill's core job.
- **Session close** — run the close audit when the user signals the end.

**Why a skill and not just prose rules:** these conventions are easy to skip under context load. Loading the skill puts the procedure back in context at the moment it's needed, and forces the full-session scan instead of reconstruction from fading memory.

## File location & naming

`.claude/session-logs/YYYY-MM-DD-topic.md`

- Date = **session start date**, not the date you write the log (sessions can span midnight).
- Topic = short kebab-case descriptor of the session's main work.
- **Never overwrite an existing Session Log.** If a file for the session already exists, open and update it.

## The format at a glance

Required sections, in this exact order. The headings are a **fixed enum** — a deterministic parser depends on them being present and spelled exactly, so don't rename, reorder, or replace them with free-form text.

```markdown
# Session: [Topic] — YYYY-MM-DD

**Goal:** one line — what this session set out to do.

## What happened

## Decisions & trade-offs

## Mistakes & corrections

## What worked & what to repeat

## Learnings about the user

## Where to pick up

[...timestamped Update blocks go here, in chronological order...]

## To-do
```

Each section has depth rules and worked examples in **`references/format-spec.md`** — read it before writing a log for the first time, or whenever you're unsure how deep a section should go. The short version:

- **What happened** — bulleted executive overview of work completed; add in-place as you go, don't batch at close.
- **Decisions & trade-offs** — one **bold heading** per decision; list the alternatives *before* the choice; tie rationale to the user's goal; state the **implication**, not just the bare fact.
- **Mistakes & corrections** — the bold triplet `**Symptom:** / **Root cause:** / **Correct approach:**`; capture meta-failures (failures about the process itself).
- **What worked & what to repeat** — the positive counterpart to Mistakes: name the win + **why it worked** (the mechanism) + whether to repeat it; quantify the payoff when estimable (time saved, rework avoided), sized to the actual path taken.
- **Learnings about the user** — each tagged with the **observable signal** that revealed it; actionable and specific; mark session-scoped ones `*(session-log-only, not promoted to memory)*`.
- **Where to pick up** — short footer pointing future-self at canonical sources first.
- **To-do** — `[ ]` for open items; `~~strikethrough~~` (never delete) for completed ones; always the last section.

## Update blocks (the timeline)

Append-only, chronological snapshots of work *between* updates — an honest accounting of how the session actually progressed. They sit immediately above To-do.

```markdown
## Update YYYY-MM-DDTHH:MM TZ
```

- **One canonical timestamp format**, exactly: `YYYY-MM-DDTHH:MM TZ`, 24-hour clock, local timezone (e.g. `## Update 2026-06-04T15:32 PT`). The parser keys off this format — don't vary it.
- **Timestamps must be accurate, never guessed.** Get the real time from the `date`-backed hook (or run `date "+%Y-%m-%dT%H:%M %Z"`) at the moment you write the block.
- **Append in chronological order at the END of the run. Never insert a block above an existing one** — that creates a reverse-chronological mess a future reader has to re-sort. If you must backfill a missed block, write a single retroactive Update that says the exact time wasn't captured; don't fabricate a timestamp to hide the gap.
- **Use Update blocks for:** files written, memory saved, CLAUDE.md modified, todos crossed off, significant findings, decisions made/changed (with the time), **research/investigation conducted, and the prep or exploration that led to a milestone — the path to it, not only the milestone itself.** Capturing the effort *between* artifacts is what makes pacing analysis possible in a post-mortem.
- **Don't put thematic content here.** A decision belongs in *Decisions*; the Update block just notes that it happened and when.

## Incremental update triggers

Update immediately — don't batch — when any of these happen. In a long session you can't reliably scroll back; reconstruction at close drops things. Incremental capture is the only dependable mitigation.

- A decision is confirmed (an approach is approved, options resolved)
- A significant finding changes understanding (a scan result, web search, empirical test)
- A plan or spec file is created or modified
- A user correction, or a rejected tool call with the explanation
- A to-do item is completed or crossed off
- A deliverable is written
- A persistent memory file is written

**Logging memory writes** — when a persistent memory file is written, log it with its path:

```
- Written to persistent memory:
  - ~/.claude/projects/<project-slug>/memory/<filename>.md — one-line description
```

## On resume / after compaction

After a context compaction, API error, or session resume: **orient before executing.** Re-read the current Session Log end-to-end, verify the actual state (don't trust a summary's "next step"), and check in with the user before running anything — the summary describes intent, not verified state. Write only confirmed, directly-observed facts; never record assumptions, not even hedged. Use absolute dates (no "today"/"yesterday" — meaningless to a future reader).

## Session close

When the user signals close ("last call", "closing", "anything else?"), audit before confirming done. Full checklist in **`references/format-spec.md`**; the essentials:

- Every decision has alternatives + rationale tied to the user's goal; revised decisions show the final choice up top.
- Every mistake has a root cause + forward-looking "Correct approach:"; meta-failures captured.
- Every "What worked" entry names *why* it worked and whether to repeat (payoff quantified where estimable).
- Every learning has an observable signal and is actionable.
- Memory writes logged with paths; todos current (completed ones struck through, not deleted).
- A final `## Update` block for the last batch of actions; no duplicate timestamp blocks.
- "Where to pick up" footer written.
- **Stale-claim audit** — re-verify carry-forward claims that may have gone false during the session ("X file still on disk", "Y dir still empty"). A quick `ls`/`cat` beats a confidently wrong close.
- `decisions.md` promotion reviewed — *only if the project has a `decisions.md`*.

## Hard acceptance criterion — machine-readable without an LLM

A conforming Session Log must be parseable by a deterministic parser (regex / Markdown AST, no model call) that extracts the Goal, every required section's body, every Update block in chronological order, and the To-do items — with **zero manual fixup**. This is what the fixed heading enum and single timestamp format buy you. The bundled parser **`scripts/parse_session_log.py`** is the reference implementation and the test: run it against any log you produce to confirm the format holds.

```
python3 scripts/parse_session_log.py <path-to-session-log.md>
```

Exit code 0 + a full JSON extraction means the log conforms. A non-zero exit means a required field didn't parse — fix the log, don't ship it.

## Situational playbook

Beyond the always-on rules above, **`references/validated-patterns.md`** holds a library of situational patterns (arc-grouping multi-threaded sessions, parallel-session orchestration, cross-list renumbering, and more). These are *not* a checklist to force into every log — apply each only when its situation arises. Skim the list once so you recognize the situations; consult the detail when one shows up.

The unifying idea: a Session Log is a deliberate artifact whose structure can be *improved* within a session, not a fixed template to fill in. Favor pattern-finding over data entry.
