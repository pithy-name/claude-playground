# Session Log — Format Spec (full depth)

Full per-section guidance, the reference example, and the close checklist. SKILL.md has the operational summary; read this for depth or a worked example.

> **Path policy in examples:** placeholders only (`~` = home; `<project-slug>` = the project's dir under `~/.claude/projects/`). No absolute paths, no usernames — this ships in a public repo.

## Table of contents

- [Philosophy](#philosophy)
- [Required structure, in order](#required-structure)
- [Section guidance](#section-guidance)
- [Chronological-append discipline](#chronological-append-discipline)
- [Memory writes](#memory-writes)
- [decisions.md promotion](#decisionsmd-promotion)
- [Session-close checklist](#session-close-checklist)
- [Reference example](#reference-example)

## Philosophy

- **Posterity record with an executive top.** Substitutes for reading the whole transcript. The top (Started/Goal + What happened) is the quick read; the sections below are supporting depth. Length scales with the session — not capped. Also used for post-mortems.
- **Captures both directions.** A retro learns from what went *right* (repeat it) as much as what went *wrong* (stop it). That's why Learnings groups Mistakes, What-worked, and User-preferences together.
- **Final state up top, evolution in the timeline.** Thematic sections reflect the end state; the chronological Update blocks capture how it got there.

## Required structure

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

These headings are a **fixed, exact enum**. The parser (`scripts/parse_session_log.py`) depends on each being present and spelled exactly — don't rename, reorder, or substitute free-form text. Keep the blank line after `## Learnings`.

## Section guidance

### Header (title + metadata)
- `# Session Log — [Topic]` — the topic only; **no date in the H1** (the date lives in `**Started:**` and the filename).
- `**Started:**` — session start date + time + timezone, e.g. `2026-06-06 15:42 PT`.
- `**Session ID:**` — the session's stable identity (the `SessionStart` hook fills this from stdin). Lets a log be traced back to its transcript.
- `**Goal:**` — one line of session intent. *Why:* anchors the executive top so a reader grasps the *why* first.

### What happened
Bulleted executive overview of work completed. *Why:* lets a reader grasp the arc in ~30s. Add in-place as you go; don't batch at close. At close, refresh into named arcs (primary + secondary threads) ending with a **Final state** line (done / deferred / open).

### Decisions & trade-offs
One entry per decision, each a **bold heading** then bullets. *Why:* "we chose X" loses the context of what was considered; named alternatives make the reasoning auditable and reversible.

```
**<Decision name>**
- Options considered: <alternative A> vs <alternative B>
- Chosen: <the choice>
- Why: <rationale tied to the goal>
- Implication: <downstream consequence>   (optional — include when not obvious)
```

### Learnings
An H2 umbrella over the three kinds of learning. *Why:* when the user says "capture learnings," they mean **all three** — Mistakes, What-worked, and User-preferences — not just the user one. Grouping them removes that ambiguity. The `## Learnings` line itself carries no body; its content is the three H3 subsections.

#### ### Mistakes & corrections
Process failures as a triplet. *Why:* "I did X wrong" doesn't help future sessions; root cause + correct approach does.

```
**Symptom:** what happened (verbatim user quote / error message when available)
**Root cause:** the underlying mechanism, not the surface failure
**Correct approach:** forward-looking guidance
```
Capture meta-failures (failures about the process itself). Bold labels are mandatory — the visual weight makes the section scannable.

#### ### What worked & what to repeat
The positive counterpart to Mistakes. *Why:* a log that only records failures teaches what to stop, never what to keep doing.

```
**<the win>**
Why it worked: <the mechanism, on its own line>
Repeat: <whether/when to do it again>
```
Quantify the payoff when estimable (time saved, rework avoided). Capture process wins, not just task wins.

#### ### User preferences & conventions
Preferences, patterns, and working style observed this session. *Why:* generic notes ("values existing work") are too vague; specific signals + behavioral implications are usable by a future session.

- Each entry includes the **observable signal** that revealed it; written as actionable guidance.
- Tag session-scoped ones `*(session-log-only, not promoted to memory)*`.
- Example: `Wants verification before "done" — asked "did you actually run it?" Run it, then report.`

### Update blocks (timestamped activity log)
Chronological append-only snapshots of work between updates. Sits immediately above To-do. Format: `## Update YYYY-MM-DDTHH:MM TZ` (24h, local TZ, with the `T`, colon, and TZ label). Accurate, never guessed. Use for files written, memory saved, findings, decisions made/changed (with time), research/prep that led to a milestone. Don't restate thematic content.

### To-do
Open + recently-completed items. *Why:* the next-action prompt. Always the last section.
- `- [ ]` open; `- [x] ~~struck text~~ done` for completed — keep the checkbox **and** strike the text, never delete.

## Chronological-append discipline

Append new entries at the **END** of every section (oldest→newest) — not only Update blocks. Never anchor an Edit *above* an older entry because that string is convenient; it silently reorders the section and misrepresents how the thinking evolved. (The one exception is the close-time refresh of "What happened," which deliberately reorganizes into arcs.)

## Memory writes

```
- Written to persistent memory:
  - ~/.claude/projects/<project-slug>/memory/<filename>.md — one-line description
```

## decisions.md promotion

Only where the project has a `decisions.md` (many won't — skip if absent): review Decisions, promote any with lasting cross-session impact, note "promoted to decisions.md" on the entry. Don't duplicate.

## Session-close checklist

- [ ] "What happened" refreshed into arcs + a "Final state" line
- [ ] Every decision has Options considered / Chosen / Why
- [ ] Every mistake has root cause + "Correct approach:"; meta-failures captured
- [ ] Every win has "Why it worked:" on its own line
- [ ] Every user-preference has an observable signal and is actionable
- [ ] **Learnings populated** — none of the three subsections left empty if the session produced any
- [ ] All memory writes logged with paths
- [ ] Todos current — done items as `- [x] ~~…~~`
- [ ] Final timestamped `## Update` block; no duplicate timestamps; updates chronological
- [ ] decisions.md promotion reviewed (only if the project has one)
- [ ] **Stale-claim audit** — re-verify carry-forward claims with a quick `ls`/`cat`

## Reference example

A minimal conforming Session Log (path-agnostic, no PII). This is the fixture the parser test runs against — keep it conforming.

```markdown
# Session Log — script-folders

**Started:** 2026-05-18 14:02 PT
**Session ID:** sess-2f9c1a4b
**Goal:** Reorganize tool scripts into self-contained per-tool folders.

## What happened
- Reorganized tool scripts into per-tool folders; added READMEs.

## Decisions & trade-offs
**Folder granularity**
- Options considered: one folder per tool vs one shared utils/.
- Chosen: per-tool.
- Why: keeps each tool self-contained and independently runnable.
- Implication: shared helpers are promoted deliberately, not duplicated by accident.

## Learnings

### Mistakes & corrections
**Symptom:** Moved a script before updating its relative import.
**Root cause:** Edited the path in one place, not the caller.
**Correct approach:** grep for references before moving a file.

### What worked & what to repeat
**Grep-before-move, once adopted**
Why it worked: surfaced callers the editor didn't show, catching two more stale imports.
Repeat: for every file move.

### User preferences & conventions
- Wants verification before "done" — asked "did you actually run it?" Run it, then report.

## Update 2026-05-18T14:02 PT
- Set up the find-files tool; completed "split utils" (struck in To-do).

## Update 2026-05-18T14:42 PT
- Added a second tool folder; refreshed its README.

## To-do
- [x] ~~Split shared utils into per-tool folders~~ done
- [ ] Add tests for find_files.py
```
