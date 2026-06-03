# breakdown-to-decide — Design Spec

**Date:** 2026-06-01
**Status:** Reviewed and revised — ready to build the MVP
**Type:** Claude Code skill (user-invocable) + PreToolUse hook

**Deliverables when built:**
- Skill — `.claude/skills/breakdown-to-decide/SKILL.md`
- Hook script (parser + `MODE`-gated decision layer)
- Hook registration in `.claude/settings.json` (via the `update-config` skill; path via `$CLAUDE_PROJECT_DIR`)
- `README.md` — human-facing: what it does, the contract, how to enable/disable the hook, the `MODE` flag

---

## Purpose

Walk a user through their set of choices to resolve a problem/question/finding/issue, one at a time. For each question, present a structured writeup (issue, why it matters, options, implications, trade-offs, recommendation), then capture the user's decision via the `AskUserQuestion` tool.

IMPORTANT: Each question must describe the issue & why it matters

IMPORTANT: For each decision, the recommended path is marked (with why) — exactly one option for single-select, or a recommended set for multi-select. Every option must state:
- **Implication** — what choosing *this* option causes (its direct consequence)
- **Trade-offs** — what you gain vs. give up *relative to the other options*

Replaces the ad-hoc pattern of dumping a wall of findings and asking the user to respond to all at once.

---

## Altitude of this spec

This spec is the **contract** — what the result must do and why — not the implementation. The decision contract below and the enforcement mechanism are binding. The peripheral mechanics (durable persistence, deferral routing, acting on decisions) are **out of MVP scope** — don't build them yet. A *simple in-chat recap* is the one exception: it **is** in the MVP (see Mechanism 1).

---

## Build for expansion (NON-NEGOTIABLE)

This is the load-bearing architectural requirement — **do not lose it in the build.** The MVP is deliberately small, but it must be structured so we can become stricter/more opinionated later **without a rewrite.** Concretely, the builder MUST:

1. **Separate the hook's parser from its decision layer**, selected by a `MODE` flag. MVP ships `MODE=soft`; `MODE=strict` is a known future requirement — do not hard-wire soft-only behavior.
2. **Keep peripheral concerns modular**, so each deferred capability can be added/changed in isolation later.
3. **Single source of truth for the contract** (see below) so the two enforcement layers never drift.

---

## The decision contract (binding)

This is the heart of the spec. A **decision** here means a *user-facing choice among options to resolve a problem / finding / issue / question*. Pure clarifiers — questions with no meaningful options or trade-offs (e.g. "which file did you mean?") — are **not** decisions in this sense; that distinction is why the soft MVP is lenient and the future strict mode needs a bypass for trivial questions.

Every decision the skill or hook governs must be presented this way:

- **Question** states the issue **and why it matters** (carried in the prose writeup that precedes the widget).
- **Options** — 2–4. **Single-select by default; use `multiSelect` when the decision genuinely allows multiple compatible picks** (e.g. "apply the fix AND add a test").
  - **Every** option's `description` carries an **Implication** segment and a **Trade-offs** segment — in *both* modes.
  - **Single-select:** the recommended option is **first**, its label suffixed with `(Recommended)`, and its description carries a **Why** segment.
  - **Multi-select:** "recommended-first" is relaxed; mark each recommended option `(Recommended)` (a recommended *set*), each carrying its own **Why**.

The contract is written as a **parseable shape** on purpose: labeled segments (`Implication:`, `Trade-offs:`, `Why:`) are what make it machine-checkable by the hook. Content quality is the model's job; segment presence is the hook's job.

Rec model chosen: **a recommended option (or set, for multi-select); all options carry Implication + Trade-offs** (the "why" lives on the recommended option(s)). Alternatives considered and rejected: every option self-verdicts (too verbose); recommendation at question level only (not bound to a button).

**Single source of truth (two enforcement layers, not duplication).** The contract is enforced in two places — the **SKILL.md instructions** (tell the model how to present) and the **hook** (machine-validate the segments). This is defense-in-depth, not a DRY violation, *provided* there is one canonical definition both layers point to. Keep it DRY by: defining the contract once (this section / the README) as the authority; SKILL.md restates the behavioral instruction but cites this as the source; the hook encodes only the segment **keys** as a small list (`["Implication", "Trade-offs", "Why"]`) with a comment pointing back here. Changing the contract = edit the canonical definition + the one key list. Do **not** copy the contract prose into multiple files.

Why both layers: inside the skill, the SKILL.md instructions carry the contract, so compliance holds even under the soft-MVP hook (the hook is backup there). The hook's **added value over the skill** is enforcing the contract on `AskUserQuestion` calls that happen *outside* a skill walk — i.e. when Claude asks a question during ordinary conversation.

---

## Mechanism 1 — Skill (user-invocable)

The skill orchestrates the **walk** over a set of decisions.

- **Invocation:** `/breakdown-to-decide`; also auto-triggers when the user signals decision overwhelm or wants options laid out. Seed the `description` with phrasings like: "walk through these one by one", "go through these issues / decide on each", "break it down for me", "help me understand my options", "I don't know where to start", "how to choose" / "how do I choose". (Tune to balance recall vs. over-firing on generic phrasing.)
- **Input gathering** (intent): prefer the decision set already present in the conversation; else ask. (How the user supplies it — paste, file, PR, etc. — is the builder's call.) **Never fabricate decisions.**
- **The walk:** for each item, one at a time, present the contract-shaped writeup (issue + why in prose) then the `AskUserQuestion` decision. Move to the next only after the current is answered.
- **Contract authority:** SKILL.md must embed the decision contract as behavioral instruction (citing the canonical definition) — this is what makes compliance reliable under the soft-MVP hook.

**MVP scope for the skill:** the walk + contract-shaped questions + a **simple end-of-walk recap** (print the decisions). Nothing more. Persistence files, deferral routing, and any "act on the decisions" step are **out of MVP** (deferred).

---

## Mechanism 2 — Hook (PreToolUse → `AskUserQuestion`)

A deterministic gate that applies the contract to **every** `AskUserQuestion` call, not just inside the skill. The trigger is clean: the event is "the model is about to ask a question" = `PreToolUse` with matcher `AskUserQuestion`.

**Hard constraint:** the hook receives only `tool_input` (the questions + options). It is **blind to the surrounding chat**. Therefore the contract elements it checks must live **inside the payload** (question text + option descriptions).

**Architecture (built for expansion):** separate the **parser** from the **decision layer**, selected by a `MODE` flag.

- **Parser** (python3 — robust JSON + regex; confirmed present): iterate `questions[].options[]`; flag any option whose `description` lacks an `Implication:` or `Trade-offs:` segment. Single-select: flag if `options[0].label` lacks `(Recommended)` or its description lacks `Why:`. Multi-select (`multiSelect: true`): relax recommended-first — instead require **at least one** option marked `(Recommended)` with a `Why:`.

- **Decision layer — MVP (`MODE=soft`), build this now:** always `allow`; when the parser finds gaps, emit `additionalContext` reminding the model of the contract so it self-applies. Zero friction, no lockout risk. **Known limit:** `additionalContext` on `allow` reaches the model *after* the current question is shown, so in a one-by-one walk it sharpens the *next* question, not the current one. The MVP's job is to prove the trigger + parser and start shaping behavior.

- **Decision layer — Expansion (`MODE=strict`), later:** `permissionDecision: "deny"` + `permissionDecisionReason` containing the **exact required template** so the model fixes it in one retry. Plus three safeguards:
  - **Loop-breaker:** per-`session_id` denial counter in `$TMPDIR`; auto-`allow` after 3 consecutive denials (hooks are stateless between runs, hence the file). Reset on any pass.
  - **Bypass sentinel:** a marker (e.g. `header` starting with `quick:`) skips enforcement for genuinely trivial questions — keeps "always-on" with a deliberate escape hatch.
  - Optional `updatedInput` for mechanical-only fixes (e.g. reorder so the recommended option is first).

**Honest boundary:** the hook enforces **shape, not substance** — it guarantees a `Trade-offs:` segment exists, not that the reasoning is good. It cannot verify the prose writeup was shown. Whether PreToolUse fires inside subagent tool calls is **unverified** — confirm before relying on it.

**Registration:** in checked-in `.claude/settings.json` (so it travels with the repo), command referenced via `$CLAUDE_PROJECT_DIR` — **no absolute paths** (public-repo rule). Use the `update-config` skill to wire it.

---

## Non-goals (YAGNI)

- No automatic fixing without confirmation.
