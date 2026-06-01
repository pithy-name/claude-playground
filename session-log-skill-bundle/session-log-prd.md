# PRD: Session Log Skill

**Date:** 2026-05-28
**Status:** Final draft — not done (spec still being refined; PRD content stable pending spec sync)
**Canonical spec:** `plans/session-log-skill-spec.md` — the standalone, self-contained build reference (format spec + validated patterns). `archive/scratchpad-management-skill.DEPRECATED.md` is the frozen historical source it was derived from. This PRD owns *strategy, naming, architecture, and scope* — not format detail. Do not duplicate the spec here.
**Related sources reconciled:** global `~/.claude/CLAUDE.md`, self-hosted `CLAUDE.md`, self-hosted project memories, `claude-playground/.claude/skills/session-journal/` (superseded predecessor), `claude-playground/CLAUDE.md`.

---

## 1. Problem

Session-summary docs (creation + updates) dominate top session goals. The same conventions get re-taught every session: chronological ordering, fresh timestamps, strikethrough-not-delete, full-session scan, session-start dating.

**Naive framing (insights report):** "Codify the rules in a skill so you stop re-teaching them."

**Why that's incomplete:** The conventions already live in `~/.claude/CLAUDE.md`, loaded every session. The rules are not missing — they get skipped under context load. A naive skill that merely restates CLAUDE.md would just be a second copy: duplication, drift, zero behavior change. A skill earns its place two ways: by doing **active work** passive text can't (forcing procedures, running checks, pulling live state), and by becoming the **single home** for these rules once CLAUDE.md's copy is removed (§4, §7.5) — not by sitting alongside a copy that still lives elsewhere.

**Second problem — naming collision:** The artifact has been called three things across the workspace: "scratchpad" (global CLAUDE.md, ~24 memory files, self-hosted CLAUDE.md), "journal" (the playground `session-journal` skill), and "Session Log" (the playground README, which marks `session-journal` as superseded by "a Session Log-based approach"). "Scratchpad" also collides with Claude's own native scratchpad concept, which is a distinct thing.

---

## 2. Decisions (confirmed 2026-05-28)

| # | Decision | Choice | Notes |
|---|----------|--------|-------|
| Name | What to call it everywhere | **Session Log** | Rename cascade required (§4) |
| Structure | Organizing model | **Thematic + timeline base** (current model), selectively borrowing from `session-journal`; no full hybrid | §5; unused journal ideas → §10 Deferred |
| Trigger | How the skill fires | **Hybrid** — auto-create the file at session start, manual/judgment updates thereafter | §6 |
| Location / path policy | Where it lives | **Per-project (self-hosted) for now**, authored in the *spirit of a global skill*: fully path-agnostic and PII-safe everywhere | §7.4 (global promotion → §10 Deferred) |
| Directory | Where logs are written | **`.claude/session-logs/`** — co-located with Claude config, hidden, tidy (NOT a gitignore play — `.claude/` is intentionally tracked for skills) | §4 |
| Hooks | What ships in v1 | **Two hooks:** `SessionStart` (auto-create file) + `PreToolUse` on `Write\|Edit` (inject fresh timestamp). **No ordering-lint** | §7.2 |
| Deliverables | What the build produces | **`SKILL.md` + `README.md`** (README holds provenance/maturity, keeps SKILL lean) | §7.1, spec "Deliverables" |
| Authority | Source of truth | **Standalone, self-contained spec** is the build input; CLAUDE.md Session Management section **removed once skill is live**; the skill becomes sole authority | §7.5, §4 |
| Spec fate | After the skill ships | **Archive/freeze the spec** (e.g., move to `archive/`) so it can't become a competing live copy; provenance moves into the skill README | §7.5 |

---

## 3. Goals / Non-goals

**Goals**
- Convert passively-ignored conventions into actively-enforced behavior.
- Eliminate recurring corrective prompts (ordering, timestamps, strikethrough, memory-from-reconstruction).
- Single source of truth for the format rules — no duplicated rule sets that drift.
- Build path-agnostic and PII-safe from day one so global promotion is friction-free.
- **Machine-readable without an LLM — hard v1 acceptance criterion.** The Markdown itself must be deterministically parseable (fixed required-heading enum, frontmatter-friendly structure, one canonical Update-block timestamp format); no separate structured sidecar in v1. Promoted from deferred per the 2026-05-30 session — full, testable criterion lives in the spec's "Acceptance criteria (hard requirements)".

**Non-goals**
- Rewriting the format spec (lives in `plans/session-log-skill-spec.md`).
- Full transcript-fidelity capture (verbatim prompts/Q&A) — see §10.

---

## 4. Naming: "Session Log" + rename cascade

Adopt **Session Log** as the canonical term. Cascade (mechanical, but touches many files — execute as a discrete, separately-approved step):

- Global `~/.claude/CLAUDE.md` — the "Session Management" section is **removed** once the skill is live (not renamed); the skill replaces it (§7.5).
- Self-hosted `CLAUDE.md` — update/remove references to `scratchpads/`.
- Project memory files — ~24 files; several have `scratchpad` in the filename slug (`feedback_scratchpad_depth.md`, `feedback_scratchpad_session_start_date.md`) + `MEMORY.md` index lines.
- Spec doc — ✅ done: renamed to `plans/session-log-skill-spec.md` (new file); original `archive/scratchpad-management-skill.DEPRECATED.md` kept frozen as historical source.
- Directory — rename `scratchpads/` → **`.claude/session-logs/`**.

**Risk:** broad find/replace could corrupt entries that legitimately reference Claude's *native* scratchpad. Rename must distinguish "our artifact" from "Claude's native scratchpad concept" — manual review, not blind sed.

---

## 5. Structure: thematic + timeline base, with selected `session-journal` ideas

**Base = current model** (full detail in `plans/session-log-skill-spec.md`): living thematic sections at top (What happened, Decisions & trade-offs, Mistakes & corrections, Learnings about the user) + chronological timestamped Update blocks + To-do at bottom. Purpose: an executive **TL;DR alternative to reading the whole transcript** — posterity + post-mortems.

**Folded in from `session-journal` (kept):**
1. **Goal line in the header.** Brief "what we set out to do this session" at the top. Cheap, improves the posterity TL;DR.
2. **Implication, not bare fact.** Decision/update entries must state the *implication* of a choice, not just the fact ("set `user-invocable: false` *so it fires automatically*"). Sharpens entries for future readers.
3. **Privacy framing for repo identity.** Reference the repo as `owner/repo` or relative path — never the full absolute path. (Also satisfies §7.4.)
4. **Consolidated "Files changed this session"** at close — a single list, complementing the per-Update memory-write logging.

---

## 6. Trigger model: hybrid

- **Auto-create at session start** (deterministic → hook): a `SessionStart` hook creates the Session Log file for the session if absent, stamped with the session-start date. Guarantees the file always exists; removes the "forgot to create it" failure.
- **Manual/judgment updates** (→ skill): the user (or judgment-driven moments) invoke the skill to write thematic sections, Update blocks, and the close-out. Content cadence stays under user control; avoids auto-fire noise.

Full automatic milestone-detection firing (the `session-journal` model) is **deferred** — see §10.

---

## 7. Architecture

### 7.1 Use `skill-creator` — do not hand-write `SKILL.md`
Build-vs-buy: `skill-creator` handles correct placement (don't guess the skills path), description tuning for trigger accuracy, and eval. Deliverables are `SKILL.md` **and** `README.md`; if `skill-creator` does not emit a README, author it separately as part of the build.

**README skeleton** (model the README on this — keeps `SKILL.md` lean, holds provenance/maturity):

````markdown
# session-log

**Maturity:** Experimental | **Type:** Hybrid (auto-create at session start + manual updates)

One-line description of what the skill does.

## What it produces
One Session Log markdown file per session in `.claude/session-logs/`.

## Provenance
Derived from the Session Log spec + PRD. Distinct from Claude's native scratchpad concept. Supersedes the `session-journal` experiment.

## Authority
Replaces the (now-removed) CLAUDE.md Session Management section — the single source of truth for Session Log conventions.

## Usage
How/when to invoke.
````

### 7.2 Split work by mechanism — hook for deterministic, skill for judgment

| Failure class | Example | Mechanism | Why |
|---|---|---|---|
| Deterministic | Stale/guessed timestamp; wrong filename date; file not created | **Hook** | LLM unreliable at "now" and at never-forgetting; `date` + `SessionStart` are guaranteed. Stale-timestamp friction is direct evidence. |
| Judgment | Full-session scan vs memory reconstruction; section depth; red-team pass | **Skill** | Requires reading, synthesis, structure decisions. |

```jsonc
// .claude/settings.json (illustrative; finalize during build)
{
  "hooks": {
    "SessionStart": [{ "command": "<create session-log file for today if absent>" }],
    "PreToolUse": [{ "matcher": "Write|Edit", "command": "date +'Current local time: %Y-%m-%dT%H:%M:%S %Z'" }]
  }
}
```

**v1 ships exactly these two hooks. No ordering-lint hook.** Chronological order is *emergent* — it falls out of real timestamps (the `date` hook) plus the append-at-end skill rule. A web scan found no off-the-shelf tool that enforces ascending-timestamp ordering for this pattern: changelog linters (markdownlint, Keep-a-Changelog) enforce *version-section* conventions (newest-first, ISO dates), which is the wrong semantics. Building a custom ordering linter isn't worth reinventing. Hard ordering-validation, if ever wanted → §10 Deferred.

### 7.3 Acceptance principle — active enforcement, single authority
Originally framed as a de-dup gate against CLAUDE.md ("if CLAUDE.md already does this passively, cut it"). **That gate is retired:** the CLAUDE.md Session Management section is removed once the skill is live (§4, §7.5), so there is no passive baseline to de-dup against — the skill becomes the sole authority and must encode the full spec.
The surviving principle: the skill should do **active work** — force a procedure (full-session scan, close audit), run a check, or pull live state (timestamps via hook) — rather than read as an inert rule list. Mechanical/deterministic steps go to hooks (§7.2), not skill prose.

### 7.4 Path-agnostic + PII-safe (global-spirit), even though per-project for now
The skill and the spec it draws from must contain **no hardcoded absolute paths** (no `/Users/<name>/...`) and **no PII** (no real names). Use relative paths or placeholders. Rationale: the playground is a public repo with a hard no-absolute-paths/no-PII rule, and global promotion is on the table.

> **Cleanup status (done):** the build reference `plans/session-log-skill-spec.md` was created PII-safe and path-agnostic. The original `archive/scratchpad-management-skill.DEPRECATED.md` (which embeds the username inside `/Users/...` absolute paths) is kept frozen as historical source and is NOT the build input.

### 7.5 Single source of truth
Once live, the **skill itself** is the single authority for Session Log conventions, and the CLAUDE.md Session Management section is removed (§4). `session-log-skill-spec.md` is the standalone, self-contained build input — the author builds from it alone and does not pull rules from CLAUDE.md or memory. After the skill ships, the spec is **archived/frozen** (e.g., moved to `archive/`) so it can't become a competing live copy; its provenance moves into the skill README. One authority = no competing copy = no drift.

---

## 8. Prior art & build-vs-buy (skills.sh scan, 2026-05-28)

Scanned the open skills registry (`skills.sh`) via WebFetch + `npx skills find` (the `vercel-labs/skills@find-skills` discovery skill). **Verdict: BUILD.** No battle-tested skill matches the Session Log concept.

**Closest trustworthy match — `softaworks/agent-toolkit@session-handoff`** (1.9K stars, 3.7K installs):
- Purpose is **handoff to a fresh agent** (context-exhaustion), not posterity / TL;DR / post-mortem.
- Captures: git history, modified files, project metadata, "Decisions Made" (Decision | Options Considered | Rationale table), Deferred Items, Assumptions, Gotchas, Blockers, Environment State, Next Steps.
- Does **not** capture: Mistakes triplet (Symptom/Root cause/Correct approach), Learnings-about-the-user, chronological timestamped Update blocks, the posterity framing.
- **Reusable assets** (see §10.8–10.10): `scripts/validate_handoff.py` (secret scan + section completeness + quality score), `scripts/check_staleness.py` (git commits since creation), file-reference existence check. Install to inspect: `npx skills add softaworks/agent-toolkit --skill session-handoff`.

**Session-log-named skills found — all below trust bar** (find-skills guidance: skeptical under 100 installs):
- `simhacker/moollm@session-log` (14) — human-readable narrative logs, but for **character/roleplay adventures**, not dev work. Shares the "living document, retroactively improve, not append-only" philosophy; domain mismatch.
- `adeonir/agent-skills@session-notes` (42), `willsigmon/sigstack@session-summary-generator` (17), `membranedev/application-skills@decision-journal` (82), `aaaaqwq/claude-code-skills@context-manager` (34), `zelinewang/claudemem@claudemem` (53) — low install counts, none verified against this model's requirements.

**Why build anyway:** the differentiator (Mistakes triplet, Learnings-about-the-user with observable signals, validated-pattern library, posterity TL;DR) is exactly what no existing skill captures. Adopt session-handoff's *validation scripts*, not its document model.

---

## 9. Execution plan

Runs **after** this PRD is complete (post-sign-off). These are build steps, not unfinished PRD content.

1. Confirm the §4 rename-cascade scope (dir name resolved: `.claude/session-logs/`).
2. ✅ Done — `plans/session-log-skill-spec.md` is the cleaned, PII-safe, standalone build input; original `archive/scratchpad-management-skill.DEPRECATED.md` kept frozen.
3. Author the skill (`SKILL.md` + `README.md`) via `skill-creator` (name `session-log`), building solely from `session-log-skill-spec.md`.
4. Add the `SessionStart` + `PreToolUse` hooks to `.claude/settings.json`.
5. Execute the rename cascade (§4) — separately approved.
6. Validate across 2–3 real sessions; confirm corrective prompts actually drop.
7. Remove the CLAUDE.md Session Management section (now superseded by the skill); archive/freeze the spec (§7.5); revisit deferred items (§10); consider global promotion.

---

## 10. Deferred items (not in v1)

The only home for future work. From `session-journal`, the prior-art scan, and raised ideas — intentionally excluded from the first build:

1. **Verbatim User Prompt capture** (per-milestone, exact prompt text). Pushes toward transcript-fidelity, which tensions against the executive-TL;DR purpose. Revisit if post-mortems need it.
2. **Q&A capture** (explicit Claude-asked / User-answered exchanges as a structured block).
3. **Verbatim User Feedback block** beyond the observable-signal quotes already captured in "Learnings about the user."
4. **Fully automatic milestone-detection firing** (`user-invocable: false`, auto-append at every milestone). v1 uses hybrid (§6) instead.
5. ~~**Machine-readable format** (structured/parseable Session Logs).~~ **Promoted to v1 (2026-05-30)** — now a hard acceptance criterion (§3 + spec "Acceptance criteria"). The "tension against rich prose" is resolved by requiring the *Markdown itself* be parseable (fixed heading enum + canonical timestamps), not a separate structured sidecar. Exact schema still TBD.
6. **Incorporating Claude's actual native-scratchpad / thinking narrative** into the Session Log.
7. **Process-improvement extraction pipeline** — mechanism to leverage Mistakes/Corrections/Learnings to improve future processes ("TBD how precisely to extract them"). Likely a separate skill/agent that reads Session Logs and proposes memory promotions.
8. **Automated secret + PII + absolute-path scan on write/close** — adapt `session-handoff`'s `validate_handoff.py` `SECRET_PATTERNS` (API keys, tokens, PEM keys, DB connection strings, `ghp_`/`sk-`/`xox` tokens). Extend with patterns for real names and `/Users/<name>/` absolute paths to enforce §7.4. Strong fit given global-promotion + public-repo exposure.
9. **Completeness / quality-score gate at close** — adapt `validate_handoff.py` required-section + 50-char-min-content + 0–100 scoring, mapped to Session Log's sections. Turns the close-out checklist into an enforced gate.
10. **Borrowable handoff-only sections** — `session-handoff`'s Assumptions Made, Potential Gotchas, Blockers/Open Questions, Environment State (active processes/env vars). Only relevant if a Session Log is ever reused for fresh-agent handoff; out of scope for the posterity purpose, but cheap to add behind a flag.
11. **Hard chronological-ordering validation** — a check that Update-block timestamps are strictly ascending. Not needed in v1 (ordering is emergent — §7.2); add only if real logs show out-of-order blocks slipping through.
12. **Global promotion** — promote the skill to `~/.claude/skills/` for cross-project use (v1 is per-project). Gated on path-agnostic/PII-safe holding up across 2–3 real sessions.
