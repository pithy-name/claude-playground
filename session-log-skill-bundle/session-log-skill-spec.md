# Session Log Skill — Format Spec & Validated Patterns

> **Naming note:** the **Session Log** here is distinct from Claude's *native scratchpad* concept (a different, internal Claude thing). Where this doc refers to Claude's native scratchpad, it says so explicitly.
>
> **Terminology:** the **Session Log** is the artifact; **`session-log`** is the skill; **`.claude/session-logs/`** is the directory. Three different things, deliberately named alike.
>
> **Path policy in examples:** examples use placeholders (`~` = home; `<project-slug>` = the project's dir under `~/.claude/projects/`). No absolute paths, no usernames.

---

## Build constraints

- **Trigger model — hybrid:** auto-create the Session Log at session start (a `SessionStart` hook owns file creation + the session-start date), then manual/judgment updates thereafter. Do NOT auto-fire on every milestone.
- **Deterministic vs judgment:** timestamps come from a `date`-backed hook (`PreToolUse` on `Write|Edit`), not the model's memory. The skill owns judgment work (full-session scan, section depth, close audit); hooks own the mechanical bits.
- **Path-agnostic + PII-safe output:** the skill must emit no absolute paths (no `/Users/<name>/...`) and no PII (no real names). Use relative paths or placeholders.
- **Machine-readability is a hard v1 requirement (acceptance criterion — see "Acceptance criteria" below):** the format MUST be parseable without an LLM — stable, exact section headings (a fixed enum), YAML-style frontmatter–friendly structure, consistent Update-block and timestamp formats. Don't add a separate structured sidecar in v1; the Markdown itself MUST be deterministically parseable (for extraction of mistakes/learnings, pacing analysis, post-mortems). Exact schema TBD — but every format choice MUST preserve, not foreclose, machine-parseability.

---

## Acceptance criteria (hard requirements)

The skill is **not** done unless its output passes these. Each is testable.

1. **Machine-readable without an LLM.** A deterministic parser (regex / Markdown AST, no model call) must extract, from any conforming Session Log: the **Goal**, each required section's body, every `## Update YYYY-MM-DDTHH:MM TZ` block in chronological order, and the **To-do** items. This requires:
   - required-section headings drawn from a **fixed, exact enum** (no free-form text where a required heading is expected);
   - frontmatter-friendly, consistently-ordered structure;
   - one canonical timestamp format for every Update block.
   **Test:** run the parser over the Reference example and assert every field extracts with zero manual fixup. A log that fails this is not done.

(Further always-on rules are summarized in "Rules this skill enforces" at the end.)

---

## Purpose

Reliably enforce Session Log structure and update behavior. Prose instructions alone are too easily forgotten for complex procedural rules; a skill loads explicitly and stays in context.

### Philosophy (what a Session Log is for)

- **Posterity record with an executive top.** Substitutes for reading the whole transcript: what was accomplished and learned by session end (takeaways and FTRs). The **top** (Goal + What happened + Final state) is the quick executive read; the sections below are supporting depth. Length scales with the session — it is **not** capped to one page. Also used for **post-mortems**.
- **Top half = summary of the whole session:** the What-happened list, decisions + trade-offs, technical/misc learnings, mistakes + corrections (a mistake *is* a learning), learnings about the user.
- **Mistakes/corrections/learnings should be reusable to improve future processes.** Exact extraction mechanism is TBD.
- **Decision log shows the FINAL decision**, not a version later changed. The chronological Update blocks capture each decision at the time it was made (and when it changed) — top reflects the end state, timeline reflects the evolution.

## What the skill does

When invoked, guide Claude to correctly create or update a Session Log: (1) create the initial log, (2) update thematic sections in-place, (3) append timestamped Update blocks, (4) close out the session.

## Format spec

### Filename

`.claude/session-logs/YYYY-MM-DD-topic.md`

- Date = **session start date**, not the date the log is written (sessions can span midnight)
- Topic = short kebab-case descriptor of the session's main work
- Never overwrite an existing Session Log

### Required sections (in this order)

```markdown
# Session: [Topic] — YYYY-MM-DD

**Goal:** one line — what this session set out to do.

## What happened

## Decisions & trade-offs

## Mistakes & corrections

## Learnings about the user

## Files changed this session

## Where to pick up

[...timestamped Update blocks go here, in chronological order...]

## To-do
```

### Section guidance

Each section gets a short description + motivation, then the rules.

#### Goal (header line, under the title)
One-line statement of session intent — what we set out to do. *Why:* anchors the executive top so a future reader grasps the *why* before the details.

- One line. Plain prose, not a bullet list.

#### What happened
Big-picture executive overview of work completed this session. *Why:* lets a future reader grasp the session arc in ~30 seconds without reading the transcript. Updated in-place throughout the session — not batched at the end.

- Bulleted list of work completed — big-picture, executive takeaways
- Add in-place as work is done; do not batch for end of session
- Not every to-do needs to appear here (To-do completion is captured in Update blocks)

#### Decisions & trade-offs
Final decisions with alternatives + rationale + implication. *Why:* "we chose X" loses the context of what was considered; named alternatives make the reasoning auditable and reversible if context later changes. The top reflects the FINAL choice; the Update timeline captures any revisions.

- Each decision gets a **bold heading**
- List alternatives explicitly before stating the choice
- Include rationale tied to the user's goal
- State the **implication** of the choice, not just the bare fact
- Example:
  ```
  **"Empty folder" definition:** Two options: (1) no direct files only, or (2) no files anywhere in subtree. Chose recursive — stricter and more useful for cleanup purposes.
  ```
- If a decision is **revised mid-session**: strikethrough the old entry, add a new entry with inline timestamp `*(YYYY-MM-DDTHH:MM TZ)*`. No timestamp on entries never revised. (Top reflects the final choice; the timeline logs both original and change.)

#### Mistakes & corrections
Process failures named with Symptom / Root cause / Correct approach. A mistake is a learning — the aim is to improve future processes. *Why:* surface-level mistake logs ("I did X wrong") don't help future sessions avoid the same error; root cause + correct approach does.

- Use the explicit triplet, with **bold** labels: `**Symptom:**` / `**Root cause:**` / `**Correct approach:**`
- Symptom anchors in observable reality (verbatim user quote or error message when available); Root cause names the underlying mechanism, not the surface failure; Correct approach is forward-looking guidance
- Capture meta-failures — failures about the process itself, not just the task
- Example:
  ```
  **Symptom:** Rewrote entire README when asked to "add" a section.
  **Root cause:** Defaulted to Write tool without checking existing content.
  **Correct approach:** Use Edit, additive only; read before writing.
  ```

#### Learnings about the user
Preferences, patterns, and style observed during the session, each tagged with the observable signal that revealed it. *Why:* generic observations ("user values existing work") are too vague to act on; specific signals + behavioral implications are what future Claude sessions can actually use.

- Each learning includes the **observable signal** that revealed the preference
- Write as actionable guidance — specific and behavioral, not generic
- Tag session-scoped learnings (not yet memory-worthy) inline with `*(session-log-only, not promoted to memory)*`
- Example:
  ```
  Values existing work — "perfectly good and fine" signals satisfaction before a redirect; don't overwrite approved content
  ```

#### Files changed this session
A single consolidated list refreshed at close — at-a-glance summary of what was touched. *Why:* complements the per-Update memory-write logging (which is incremental); this is the scan-the-impact view, so a reader doesn't have to comb the Update blocks to know what moved.

- Relative paths; one brief note per file (created / revised / superseded).
- Refreshed at close so it reflects the final state.

#### Where to pick up
A footer pointing future-self at canonical sources first. *Why:* zero re-acquaint friction on return — the next session (or future Claude) shouldn't have to re-read the whole log to know where to start.

- Short and concrete; link to paths.
- Canonical sources first (backlog → pick item → reference logs only if needed → noting any archived plans).

#### Update blocks (timestamped activity log)
Chronological append-only snapshots of work between updates — an honest accounting of how the session progressed, evolved, or side-quested. *Why:* enables retrospective pacing analysis ("how long did step X take?") and captures the time-evolution of decisions and todos. Sits **immediately above To-do** so the most recent activity is the last thing before the next-action list.

Format:
```markdown
## Update YYYY-MM-DDTHH:MM TZ
```

- 24-hour clock, local timezone; timestamps **accurate, not guessed**
- Append in chronological order
- Use for: files written, memory saved, CLAUDE.md modified, todos crossed off, significant findings, decisions made/changed (with the time)
- Do NOT duplicate thematic content here — decisions go in Decisions, not in an Update block
- Capture To-do completion here

#### To-do
Open items + recently-completed items (struck through, not deleted). *Why:* this is the next-action prompt — what's still owed at session close. Lives at the very bottom because it's what the next session picks up.

- `[ ]` checkboxes for uncompleted items
- When completed later in session: strikethrough the whole line with `~~...~~`, do not delete
- Always stays at the **bottom** of the file

### Memory writes

When a persistent memory file is written during a session, log it with its path:

```
- Written to persistent memory:
  - ~/.claude/projects/<project-slug>/memory/<filename>.md — one-line description
```

### decisions.md promotion (at session close)

Only where the project has a `decisions.md` (many won't — if absent, skip this step):
- Review the Decisions & trade-offs section
- Promote any decision with lasting cross-session impact to `decisions.md`
- Note "promoted to decisions.md" on the Session Log entry
- Don't duplicate — Session Log = session staging, decisions.md = persistent record

## Trigger conditions

Trigger when:
- Starting a new session (create the log — note: the `SessionStart` hook auto-creates the file)
- User says "update the session log" / "last call" / signals session close
- Any explicit mention of the Session Log

## Incremental update triggers

Update immediately — do not batch — when any of these occur:
- A decision is confirmed (user approves an approach, options resolved)
- A significant finding changes understanding (scan result, web search, empirical test)
- A plan file is created or modified
- A user correction or rejected tool call with explanation
- A to-do item is completed or crossed off
- A deliverable file is written
- A persistent memory file is written

**Why this matters:** In long sessions, Claude cannot mechanically scroll back through history. Reconstruction at session end from in-context memory is unreliable — gaps are likely. Incremental updates are the only reliable mitigation.

**Manual fallback (no hook/skill active yet):** when building this skill, or in a project not yet set up, the file won't auto-exist and honoring incremental updates depends entirely on manual discipline. Reconstructing the whole log at close is exactly the failure mode this skill prevents — expect gaps (e.g., uncaptured timestamps). Mitigation: create the log early and update as you go.

## Session resume / post-compaction

After a context compaction, API error, or session resume: **orient before executing.** Re-read the current Session Log end-to-end, verify actual state (don't trust the summary's "next step"), and check in with the user before running anything. The summary describes intent, not verified state — the user may have changed direction.

Write only confirmed, directly observed facts. Never record assumptions or unverified state, not even hedged. Use absolute dates (no "yesterday"/"today" — meaningless to a future reader).

## Session-close checklist

When the user signals close ("last call", "closing", "anything else?"), audit before confirming done:

- [ ] Every decision has alternatives listed and rationale tied to the user's goal
- [ ] Every mistake has root cause + forward-looking "Correct approach:" statement
- [ ] Meta-failures captured (failures about the process itself)
- [ ] Every learning has an observable signal and is actionable
- [ ] All memory writes logged with paths
- [ ] Todos current — completed ones crossed out with `~~strikethrough~~`
- [ ] Final timestamped `## Update` block written for this session's last batch of actions
- [ ] decisions.md promotion reviewed (only if the project has one)
- [ ] No duplicate timestamp blocks
- [ ] "Files changed this session" list consolidated
- [ ] "Where to pick up" footer written
- [ ] **Stale-claim audit** — re-verify carry-forward claims that may have become false during the session (e.g., "X file still on disk", "Y dir still empty"). Quick `ls`/`cat` to confirm reality before close. Carry-forward assumptions are a known source of session-close drift.

## Reference example (inline)

A minimal Session Log showing the shape (path-agnostic, no PII):

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

## Learnings about the user
Wants verification before "done" — asked "did you actually run it?" after a claim. Run it, then report.

## Files changed this session
- `tools/find-files/find_files.py` — moved in
- `tools/find-files/README.md` — created

## Where to pick up
Next: add tests for `find_files.py`. Reference: `tools/find-files/README.md`.

## Update 2026-05-18T14:02 PT
- Set up the find-files tool; completed "split utils" (struck in To-do below).

## To-do
- ~~Split shared utils into per-tool folders~~ done
- [ ] Add tests for find_files.py
```

## Validated patterns (situational playbook)

These were validated by the user mid-session and extend the format above. **Most are a situational playbook — apply each WHEN its situation arises, not as a 14-item checklist forced into every log.** A few are tagged **[always-on]**: these are mandatory rules that also live in the Format spec / "Rules this skill enforces" summary, repeated here for completeness. The rest are situational.

1. **Arc-grouping in "What happened."** When a session has multiple parallel threads (primary + a secondary thread that grew), split the section into named arcs with a closing "Final state" paragraph naming what's done/deferred/open. Flat summaries flatten genuinely multi-threaded sessions. (Reflected in the close-refresh of "What happened".)

2. **Equal narrative weight for secondary threads.** Don't treat session-log/memory grooming as overhead noise around the primary task — give it equal weight if it produces durable artifacts (memory files, plan revisions). Sessions can morph from primary-task to secondary-curation focus; the log should reflect the actual shape, not the initial intent.

3. **Bold-label triplet for Mistakes entries.** **[always-on]** Use `**Symptom:** / **Root cause:** / **Correct approach:**` for every Mistake entry. Bold labels (not plain) — visual weight makes the section scannable + signals the validated pattern. Symptom anchors in observable reality; Root cause forces underlying-mechanism analysis; Correct approach makes the lesson actionable.

4. **Inline italic scope markers on Learnings.** When a Learning is session-scoped (not yet memory-worthy), tag it inline with `*(session-log-only, not promoted to memory)*` after the heading. Preserves the log-vs-memory boundary visibly so future sessions don't auto-promote everything.

5. **Decisions for meta-choices about persistence scope.** When the user explicitly chooses "session-log-only, not memory" or similar (a meta-choice about *where* to record something), capture it as a Decision entry with alternatives listed — not executed silently. The meta-choice has auditable rationale future sessions should see.

6. **First-class meta-failure entries.** When a process failure repeats (e.g., needing the user to prompt twice to capture both halves of one event), capture it as its own Mistake entry with the meta-failure named explicitly — don't bury it in a parenthetical. Meta-failures about the log/memory process deserve the full triplet.

7. **Honest scope-flagging of out-of-scope edits.** When an edit exceeds the literal request scope: state explicitly that the extra change is out-of-scope, give the rationale (consistency, alignment with validated style), let the user accept/reject/extend. Never silently bundle.

8. **Apply pinned disciplines to Claude's own next action.** When a discipline is freshly memorialized (e.g., "narrow instructions execute narrowly", "query `date` immediately before write"), the very next action that could violate it is the first test. Don't memorialize-then-violate. Self-audit against just-pinned rules before the next non-trivial action.

9. **Dual-log / parallel-session orchestration.** When two Claude sessions work in parallel on the same project (build vs execution, primary vs commentary), explicitly define which log is canonical (full execution log) and which is commentary. Cross-session info flow is "read on demand" — when relevant, the commentary log reads canonical and writes a 2–3 sentence synthesis back into its own log. Don't write into the other session's log. Capture the split as a Decision with named alternatives (single shared log / bidirectional sync / unidirectional read-on-demand). Default: do NOT notify the canonical session the split exists — it's already behaving as canonical; telling adds context load with zero behavior delta.

10. **Cross-list collision resolution = normalize, not preserve dual sequences.** When two independently-numbered lists (e.g., a log-local backlog and a canonical durable backlog) merge into one canonical source, normalize the non-canonical sequence's letters/numbers to match the canonical authority. Don't keep two parallel sequences with a mapping table — the cognitive cost outlives the historical-preservation argument. Capture the renumber in a Mistakes entry; add an inline italic note on each renumbered item flagging its original identifier so the audit trail is visible at the point of change. (Applies to cross-list MERGE collisions — not within-list reordering, which keeps original order.)

11. **Per-item consistency on series annotations.** When applying a marker/annotation/correction across multiple items in a series (e.g., "(originally L)" notes during a renumber, or normalizing bullet labels), apply it to EVERY item — not just the first. The first item's annotation does not "cover" the rest. Same for backwards-compat notes, version-suffix tags, comment-style normalization.

12. **Living-section + Update-block dual-discipline at step completion.** When a step/task/deliverable completes, edit BOTH the living section (where status lives — e.g., a step-results table) AND append a dated Update block — same edit pass, before moving on. The table answers "where are we?"; the Update log answers "when did each thing land?" Skipping the Update block collapses the timeline (and blocks retrospective pacing analysis). Generalizes to: memory writes, MEMORY.md index updates, plan-file edits, runbook edits, backlog mods — every committed artifact gets a dated Update block in the log that observed it.

13. **Update-block chronological order is append-only.** **[always-on]** New Update blocks always go at the END of the Update-block run (which sits immediately above To-do), in chronological order. Never insert above existing blocks — that creates a reverse-chronological mess future readers must re-sort. If a missed block needs backfilling, write a single retroactive Update with explicit "exact times not captured at the moment" framing and cross-ref a source with canonical timestamps if one exists. Don't fabricate prior timestamps to hide the gap.

14. **"Where to pick up" footer.** Write a "Where to pick up" footer pointing future-self at canonical sources first (backlog file → pick item → reference logs only if needed → noting any archived plans). Placed **above** the Update blocks — Updates sit immediately above the trailing To-do, so the footer goes one level up. Goal: zero re-acquaint friction on return. Keep it short, concrete, link-to-paths.

**Unifying principle:** the Session Log is a deliberate artifact whose structure can be improved within a session, not a fixed template to fill in. Encourage pattern-finding over data entry — leave room for in-session structural innovation, validated by the user, that improves on the template.

## Future considerations (out of scope for v1)

Parked ideas — do NOT build in v1, but don't foreclose them either. Recorded so the direction survives.

- **Incorporate Claude's native scratchpad / reasoning narrative.** Aspiration to fold Claude's actual in-session thinking (the native scratchpad — distinct from this Session Log, see the naming note at top) into the log, rather than only the post-hoc executive summary. Unresolved: capture mechanism, and how to keep it PII-safe and non-bloating. Verbatim per-milestone capture of prompts/Q&A/feedback is the closest existing model for this — but that's a different artifact shape than this spec's executive-summary-first log, so reconcile the two before building.

## Rules this skill enforces (always-on summary)

- Filename dated by session start; never overwrite
- Required sections in order (Goal header → What happened → Decisions → Mistakes → Learnings → Files changed this session → Where to pick up → Update blocks → To-do), with depth guidance (Decisions: named headings + alternatives + implication; Mistakes: bold Symptom/Root cause/Correct approach triplet + meta-failures; Learnings: observable signal + actionable + specific)
- Thematic sections are living reference sections — edit in-place; refresh "What happened" at close for the full arc
- Timestamped Update blocks are an append-only, chronological activity log — not for thematic content; accurate timestamps, never guessed; sit immediately above To-do
- Decision revision: top reflects final choice; strikethrough old entry + add new with inline timestamp; timeline logs both
- Strikethrough for completed todos (never delete)
- decisions.md promotion at close (only if the project has one)
- Memory writes logged with path
- Update incrementally — don't reconstruct at close
- On resume/post-compaction: re-read the log, verify state, check in before executing
- Only confirmed, observed facts — no assumptions; absolute dates only
- Output is machine-parseable without an LLM (**hard acceptance criterion**) — fixed required-heading enum + one canonical Update-block timestamp format; never break deterministic parseability
