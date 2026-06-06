# Session Log — Validated Patterns (situational playbook)

These patterns were validated mid-session and extend the always-on format. **Most are situational — apply each WHEN its situation arises, not as a checklist forced into every log.** A few are tagged **[always-on]**: those are mandatory and also live in SKILL.md / the format spec, repeated here for completeness.

Skim the list once so you recognize the situations; consult the detail when one actually shows up.

1. **Arc-grouping in "What happened."** When a session has multiple parallel threads (a primary thread + a secondary one that grew), split the section into named arcs with a closing "Final state" paragraph naming what's done / deferred / open. Flat summaries flatten genuinely multi-threaded sessions.

2. **Equal narrative weight for secondary threads.** Don't treat session-log/memory grooming as overhead noise around the primary task — give it equal weight if it produced durable artifacts (memory files, plan revisions). Sessions can morph from primary-task to secondary-curation focus; the log should reflect the actual shape, not the initial intent.

3. **Bold-label triplet for Mistakes entries.** **[always-on]** Use `**Symptom:** / **Root cause:** / **Correct approach:**` for every Mistake entry. Bold labels (not plain) — the visual weight makes the section scannable and signals the validated pattern. Symptom anchors in observable reality; Root cause forces underlying-mechanism analysis; Correct approach makes the lesson actionable.

4. **Inline italic scope markers on Learnings.** When a Learning is session-scoped (not yet memory-worthy), tag it inline with `*(session-log-only, not promoted to memory)*` after the entry. Preserves the log-vs-memory boundary visibly so future sessions don't auto-promote everything.

5. **Decisions for meta-choices about persistence scope.** When the user explicitly chooses "session-log-only, not memory" or similar (a meta-choice about *where* to record something), capture it as a Decision entry with alternatives listed — not executed silently. The meta-choice has auditable rationale future sessions should see.

6. **First-class meta-failure entries.** When a process failure repeats (e.g. needing the user to prompt twice to capture both halves of one event), capture it as its own Mistake entry with the meta-failure named explicitly — don't bury it in a parenthetical. Meta-failures about the log/memory process deserve the full triplet.

7. **Honest scope-flagging of out-of-scope edits.** When an edit exceeds the literal request scope, state explicitly that the extra change is out-of-scope, give the rationale (consistency, alignment with validated style), and let the user accept / reject / extend. Never silently bundle.

8. **Apply pinned disciplines to Claude's own next action.** When a discipline is freshly memorialized (e.g. "narrow instructions execute narrowly", "query `date` immediately before write"), the very next action that could violate it is the first test. Don't memorialize-then-violate. Self-audit against just-pinned rules before the next non-trivial action.

9. **Dual-log / parallel-session orchestration.** When two Claude sessions work in parallel on the same project (build vs execution, primary vs commentary), explicitly define which log is canonical (the full execution log) and which is commentary. Cross-session info flow is "read on demand" — when relevant, the commentary log reads canonical and writes a 2–3 sentence synthesis back into its *own* log. Don't write into the other session's log. Capture the split as a Decision with named alternatives (single shared log / bidirectional sync / unidirectional read-on-demand). Default: do NOT notify the canonical session the split exists — it's already behaving as canonical; telling it adds context load with zero behavior change.

10. **Cross-list collision resolution = normalize, not preserve dual sequences.** When two independently-numbered lists (e.g. a log-local backlog and a canonical durable backlog) merge into one canonical source, normalize the non-canonical sequence's letters/numbers to match the canonical authority. Don't keep two parallel sequences with a mapping table — the cognitive cost outlives the historical-preservation argument. Capture the renumber in a Mistakes entry; add an inline italic note on each renumbered item flagging its original identifier so the audit trail is visible at the point of change. (Applies to cross-list MERGE collisions — not within-list reordering, which keeps original order.)

11. **Per-item consistency on series annotations.** When applying a marker/annotation/correction across multiple items in a series (e.g. "(originally L)" notes during a renumber, or normalizing bullet labels), apply it to EVERY item — not just the first. The first item's annotation does not "cover" the rest. Same for backwards-compat notes, version-suffix tags, comment-style normalization.

12. **Living-section + Update-block dual-discipline at step completion.** When a step/task/deliverable completes, edit BOTH the living section (where status lives — e.g. a step-results table) AND append a dated Update block — same edit pass, before moving on. The table answers "where are we?"; the Update log answers "when did each thing land?" Skipping the Update block collapses the timeline (and blocks retrospective pacing analysis). Generalizes to memory writes, MEMORY.md index updates, plan-file edits, backlog mods — every committed artifact gets a dated Update block in the log that observed it.

13. **Update-block chronological order is append-only.** **[always-on]** New Update blocks always go at the END of the Update-block run (which sits immediately above To-do), in chronological order. Never insert above existing blocks — that creates a reverse-chronological mess future readers must re-sort. If a missed block needs backfilling, write a single retroactive Update with explicit "exact times not captured at the moment" framing and cross-ref a source with canonical timestamps if one exists. Don't fabricate prior timestamps to hide the gap.

14. **"Where to pick up" footer.** Write a "Where to pick up" footer pointing future-self at canonical sources first (backlog file → pick item → reference logs only if needed → noting any archived plans). Placed **above** the Update blocks (Updates sit immediately above the trailing To-do, so the footer goes one level up). Goal: zero re-acquaint friction on return. Keep it short, concrete, link-to-paths.

**Unifying principle:** the Session Log is a deliberate artifact whose structure can be improved *within* a session, not a fixed template to fill in. Encourage pattern-finding over data entry — leave room for in-session structural innovation, validated by the user, that improves on the template.

## Future considerations (out of scope for v1)

Parked ideas — do NOT build in v1, but don't foreclose them either.

- **Incorporate Claude's native scratchpad / reasoning narrative.** Aspiration to fold Claude's actual in-session thinking (the native scratchpad — distinct from this Session Log) into the log, rather than only the post-hoc executive summary. Unresolved: capture mechanism, and how to keep it PII-safe and non-bloating. Verbatim per-milestone capture of prompts/Q&A/feedback is the closest existing model — but that's a different artifact shape than this executive-summary-first log, so reconcile the two before building.
