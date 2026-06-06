# Session Log — Format Spec (full depth)

Full per-section guidance, the reference example, and the close checklist. SKILL.md has the operational summary; read this when you need the depth or a worked example.

> **Path policy in examples:** placeholders only (`~` = home; `<project-slug>` = the project's dir under `~/.claude/projects/`). No absolute paths, no usernames — this ships in a public repo.

## Table of contents

- [Philosophy — what a Session Log is for](#philosophy)
- [Required sections, in order](#required-sections)
- [Section guidance](#section-guidance)
- [Memory writes](#memory-writes)
- [decisions.md promotion](#decisionsmd-promotion)
- [Session-close checklist](#session-close-checklist)
- [Reference example](#reference-example)

## Philosophy

- **Posterity record with an executive top.** Substitutes for reading the whole transcript: what was accomplished and learned by session end. The top (Goal + What happened) is the quick executive read; the sections below are supporting depth. Length scales with the session — it is **not** capped to one page. Also used for post-mortems.
- **Top half = summary of the whole session:** the What-happened list, decisions + trade-offs, mistakes + corrections (a mistake *is* a learning), what worked + what to repeat (the positive counterpart — a retro learns from both), learnings about the user.
- **Mistakes / corrections / wins / learnings should be reusable to improve future processes.** The exact extraction mechanism is TBD, but write them as if a future session will mine them.
- **The decision log shows the FINAL decision**, not a version later changed. The chronological Update blocks capture each decision at the time it was made (and when it changed) — the top reflects the end state, the timeline reflects the evolution.

## Required sections

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

These headings are a **fixed, exact enum**. The deterministic parser (`scripts/parse_session_log.py`) depends on each being present and spelled exactly — don't rename, reorder, or substitute free-form text where a required heading is expected.

## Section guidance

### Goal (header line, under the title)
One-line statement of session intent — what we set out to do. *Why:* anchors the executive top so a future reader grasps the *why* before the details.

- One line. Plain prose, not a bullet list.

### What happened
Big-picture executive overview of work completed this session. *Why:* lets a future reader grasp the session arc in ~30 seconds without reading the transcript. Updated in-place throughout — not batched at the end.

- Bulleted list of work completed — big-picture, executive takeaways.
- Add in-place as work is done; do not batch for end of session.
- Not every to-do needs to appear here (to-do completion is captured in Update blocks).

### Decisions & trade-offs
Final decisions with alternatives + rationale + implication. *Why:* "we chose X" loses the context of what was considered; named alternatives make the reasoning auditable and reversible if context later changes. The top reflects the FINAL choice; the Update timeline captures any revisions.

- Each decision gets a **bold heading**.
- List alternatives explicitly *before* stating the choice.
- Include rationale tied to the user's goal.
- State the **implication** of the choice, not just the bare fact.
- Example:
  ```
  **"Empty folder" definition:** Two options: (1) no direct files only, or (2) no files anywhere in subtree. Chose recursive — stricter and more useful for cleanup purposes.
  ```
- If a decision is **revised mid-session**: strikethrough the old entry, add a new entry with an inline timestamp `*(YYYY-MM-DDTHH:MM TZ)*`. No timestamp on entries never revised. (Top reflects the final choice; the timeline logs both original and change.)

### Mistakes & corrections
Process failures named with Symptom / Root cause / Correct approach. A mistake is a learning — the aim is to improve future processes. *Why:* surface-level mistake logs ("I did X wrong") don't help future sessions avoid the error; root cause + correct approach does.

- Use the explicit triplet, with **bold** labels: `**Symptom:**` / `**Root cause:**` / `**Correct approach:**`.
- Symptom anchors in observable reality (a verbatim user quote or error message when available); Root cause names the underlying mechanism, not the surface failure; Correct approach is forward-looking guidance.
- Capture meta-failures — failures about the process itself, not just the task.
- Example:
  ```
  **Symptom:** Rewrote entire README when asked to "add" a section.
  **Root cause:** Defaulted to Write tool without checking existing content.
  **Correct approach:** Use Edit, additive only; read before writing.
  ```

### What worked & what to repeat
Wins, effective approaches, and good calls worth repeating — the positive counterpart to Mistakes. *Why:* a retro needs both sides. A log that only records failures teaches what to *stop*, never what to *keep doing*; capturing what worked (and the mechanism behind it) turns successful patterns into reusable practice instead of luck.

- Name the win + **why it worked** (the underlying mechanism, not just "it went well") + whether it's worth repeating or promoting to a durable practice.
- Anchor in observable reality where possible — what specifically succeeded and the signal it worked.
- Capture process wins, not just task wins — an effective workflow or sequence is itself reusable.
- Where a path was chosen over an alternative, **quantify the payoff when estimable** — time/effort saved, rework avoided — sized case-by-case to the context and the path actually taken, not a fixed figure.
- Examples:
  ```
  **Worktree before editing a cross-branch spec:** spun an isolated git worktree instead of switching branches in a shared working tree. Why it worked: zero collision with the parallel session sharing the tree. Repeat for any cross-branch edit while another session is live.
  ```
  ```
  **Build-vs-buy → reuse:** scouted for prior work before building and found the skill already designed — PRD, format spec, and a dedicated branch. Reused that instead of rebuilding from scratch. Why it worked: a short investigation pass surfaced finished prior work. Payoff: ~15h of redesign avoided. Repeat: always scout for existing work/tools before building.
  ```

### Learnings about the user
Preferences, patterns, and style observed during the session, each tagged with the observable signal that revealed it. *Why:* generic observations ("user values existing work") are too vague to act on; specific signals + behavioral implications are what future sessions can actually use.

- Each learning includes the **observable signal** that revealed the preference.
- Write as actionable guidance — specific and behavioral, not generic.
- Tag session-scoped learnings (not yet memory-worthy) inline with `*(session-log-only, not promoted to memory)*`.
- Example:
  ```
  Values existing work — "perfectly good and fine" signals satisfaction before a redirect; don't overwrite approved content.
  ```

### Where to pick up
A footer pointing future-self at canonical sources first. *Why:* zero re-acquaint friction on return — the next session shouldn't have to re-read the whole log to know where to start.

- Short and concrete; link to paths.
- Canonical sources first (backlog → pick item → reference logs only if needed → noting any archived plans).

### Update blocks (timestamped activity log)
Chronological append-only snapshots of work between updates — an honest accounting of how the session progressed, evolved, or side-quested. *Why:* enables retrospective pacing analysis ("how long did step X take?") and captures the time-evolution of decisions and todos. Sits **immediately above To-do**.

Format: `## Update YYYY-MM-DDTHH:MM TZ`

- 24-hour clock, local timezone; timestamps **accurate, not guessed**.
- Append in chronological order; never insert above an existing block.
- Use for: files written, memory saved, CLAUDE.md modified, todos crossed off, significant findings, decisions made/changed (with the time), research/investigation conducted, and the exploration or prep work that led to a milestone (the path to it, not only the milestone itself).
- Do NOT duplicate thematic content here — a decision goes in Decisions, not in an Update block.

### To-do
Open items + recently-completed items (struck through, not deleted). *Why:* this is the next-action prompt — what's still owed at close. Lives at the very bottom because it's what the next session picks up.

- `[ ]` checkboxes for uncompleted items.
- When completed later in session: strikethrough the whole line with `~~...~~`, do not delete.
- Always stays at the **bottom** of the file.

## Memory writes

When a persistent memory file is written during a session, log it with its path:

```
- Written to persistent memory:
  - ~/.claude/projects/<project-slug>/memory/<filename>.md — one-line description
```

## decisions.md promotion

Only where the project has a `decisions.md` (many won't — if absent, skip):

- Review the Decisions & trade-offs section.
- Promote any decision with lasting cross-session impact to `decisions.md`.
- Note "promoted to decisions.md" on the Session Log entry.
- Don't duplicate — Session Log = session staging, decisions.md = persistent record.

## Session-close checklist

When the user signals close, audit before confirming done:

- [ ] Every decision has alternatives listed and rationale tied to the user's goal
- [ ] Every mistake has root cause + forward-looking "Correct approach:" statement
- [ ] Meta-failures captured (failures about the process itself)
- [ ] Every "What worked" entry names why it worked + whether to repeat (payoff quantified where estimable)
- [ ] Every learning has an observable signal and is actionable
- [ ] All memory writes logged with paths
- [ ] Todos current — completed ones crossed out with `~~strikethrough~~`
- [ ] Final timestamped `## Update` block written for this session's last batch of actions
- [ ] decisions.md promotion reviewed (only if the project has one)
- [ ] No duplicate timestamp blocks
- [ ] "Where to pick up" footer written
- [ ] **Stale-claim audit** — re-verify carry-forward claims that may have become false during the session (e.g. "X file still on disk", "Y dir still empty"). Quick `ls`/`cat` to confirm reality before close.

## Reference example

A minimal Session Log showing the shape (path-agnostic, no PII). This is also the fixture the parser test runs against — keep it conforming.

```markdown
# Session: script-folders — 2026-05-18

**Goal:** Reorganize tool scripts into self-contained per-tool folders.

## What happened
- Reorganized tool scripts into per-tool folders; added READMEs.

## Decisions & trade-offs
**Folder granularity:** one folder per tool vs one shared utils/. Chose per-tool — keeps each tool self-contained and independently runnable.

## Mistakes & corrections
**Symptom:** Moved a script before updating its relative import.
**Root cause:** Edited path in one place, not the caller.
**Correct approach:** grep for references before moving a file.

## What worked & what to repeat
**Grep-before-move, once adopted:** after the first slip, grepping for references ahead of each move caught two more stale imports. Why it worked: surfaced callers the editor didn't show. Repeat for every file move.

## Learnings about the user
Wants verification before "done" — asked "did you actually run it?" after a claim. Run it, then report.

## Where to pick up
Next: add tests for `find_files.py`. Reference: `tools/find-files/README.md`.

## Update 2026-05-18T14:02 PT
- Set up the find-files tool; completed "split utils" (struck in To-do below).

## To-do
- ~~Split shared utils into per-tool folders~~ done
- [ ] Add tests for find_files.py
```
