# Build prompt — `session-log` skill

> Drop this whole file into a fresh Claude Code session **in the `claude-playground` repo**. It is self-contained: everything you need to build the skill is either in this prompt or in the two files bundled alongside it (`session-log-skill-spec.md`, `session-log-prd.md`).

---

## Your task

Build a Claude Code skill named **`session-log`** that reliably enforces Session Log structure and update behavior. A "Session Log" is a per-session posterity record — an executive TL;DR alternative to reading the whole transcript, also used for post-mortems.

## Inputs (bundled with this prompt)

1. **`session-log-skill-spec.md` — the canonical build input.** This is the format spec + validated-pattern library. **Build the skill content solely from this file.** It is self-contained, PII-safe, and path-agnostic by design.
2. **`session-log-prd.md` — strategy / architecture / scope.** Owns the *why* and the *how to build* (naming, hooks, deliverables, build-vs-buy verdict, deferred items). Read it for architecture decisions; do **not** pull format rules from it — those live in the spec.

If anything in the PRD contradicts the spec on format detail, the **spec wins**.

## How to build it

1. **Use the `skill-creator` skill — do not hand-write `SKILL.md`.** It handles correct skills-path placement, description tuning for trigger accuracy, and eval. Skill name: `session-log`.
2. **Deliverables: `SKILL.md` + `README.md`.** If `skill-creator` does not emit a README, author one separately. Model it on the README skeleton in PRD §7.1 — it holds provenance/maturity and keeps `SKILL.md` lean.
3. **Two hooks ship in v1** (add to `.claude/settings.json`; see PRD §7.2):
   - `SessionStart` — auto-create the Session Log file for the session if absent, stamped with the session-start date.
   - `PreToolUse` on `Write|Edit` — inject a fresh `date`-backed timestamp so timestamps are never guessed.
   - **No ordering-lint hook.** Chronological order is emergent (real timestamps + append-at-end rule).
4. **Split work by mechanism:** deterministic bits (timestamps, file creation, filename date) → hooks; judgment bits (full-session scan, section depth, close audit) → skill prose.

## Hard requirements (acceptance criteria — the skill is not done without these)

- **Machine-readable without an LLM.** A deterministic parser (regex / Markdown AST, no model call) must extract the Goal, every required section's body, every `## Update YYYY-MM-DDTHH:MM TZ` block in chronological order, and the To-do items. Requires: required-section headings from a fixed exact enum, frontmatter-friendly consistent structure, one canonical Update-block timestamp format. **Test:** run a parser over the spec's Reference example and assert every field extracts with zero manual fixup. (Full criterion: spec "Acceptance criteria".)
- **Path-agnostic + PII-safe.** Emit no absolute paths (no `/Users/<name>/...`) and no real names. Use relative paths or placeholders. `claude-playground` is a public repo — this is non-negotiable.
- **Single source of truth.** The skill becomes the sole authority for Session Log conventions. (In the origin repo, the CLAUDE.md "Session Management" section is removed once the skill is live — that's an origin-repo cleanup step, tracked there, not part of this build.)

## Validate before calling it done

- Dry-run / dogfood across 2–3 real sessions; confirm the format holds and corrective prompts actually drop.
- Run the machine-readability parser test against the spec's Reference example.

## Out of scope for v1

See PRD §10 (Deferred). Notably: verbatim prompt/Q&A capture, fully-automatic milestone firing, secret/PII scan-on-write, quality-score gate, global promotion. Do not build these; do not foreclose them.

---

## Provenance

This skill supersedes the `session-journal` experiment already in `claude-playground`. It was designed in a separate workspace (PRD + spec, two red-team passes each) and moved here for the build. The frozen historical source (`scratchpad-management-skill.DEPRECATED.md`) stays in the origin repo and is **not** a build input (it carries absolute paths / PII).
