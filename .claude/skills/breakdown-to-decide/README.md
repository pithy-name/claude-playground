# breakdown-to-decide

Walk through a pile of decisions **one at a time** instead of all at once. For each decision, Claude presents a short structured choice and captures your pick with the `AskUserQuestion` widget. It replaces the ad-hoc pattern of dumping a wall of findings and asking you to react to everything at once — which is exactly when people freeze or rubber-stamp.

This directory is the **canonical home of the decision contract** below. The `SKILL.md` restates it as behavioral instruction and the hook encodes only its segment *keys*; if they ever disagree, this file (and the design spec) win.

## The decision contract

A **decision** is a user-facing choice among options to resolve a problem / finding / issue / question. (Pure clarifiers — "which file did you mean?" — are not decisions and don't get the treatment.)

Every decision is presented as:

- **Issue** — what was raised.
- **Why it matters** — the impact/risk if left unaddressed.
- **Options** (2–4), each carrying:
  - **Implication** — what choosing *this* option causes.
  - **Trade-offs** — what you gain vs. give up *relative to the other options*.
- A **recommendation** with a **Why**:
  - *Single-select:* the recommended option is first, labelled `(Recommended)`.
  - *Multi-select:* each recommended option is marked `(Recommended)` (a recommended set), each with its own Why.

Two non-obvious rules the skill follows: **decompose completely** (surface the foundational decision that constrains the rest first; don't stop short), and **keep it tight, keep your voice** (a sentence or two per segment; the structure is a skeleton, not a straitjacket).

## Using it

- Invoke explicitly: `/breakdown-to-decide`.
- It also auto-triggers when you're facing a pile of choices — e.g. after a review/audit produces findings, or when you say "walk me through these," "break it down for me," "help me understand my options," "I don't know where to start," "how do I choose."

Independent decisions are presented together in a **single `AskUserQuestion` card** (up to 4 at a time) that you navigate with prev/next and one summary Submit; a decision that depends on an earlier answer is asked on its own first. More than four decisions are chunked into successive cards.

MVP scope: the walk + a simple end-of-walk recap. It does **not** persist decisions to a file, route deferrals, or apply fixes — acting on a choice is a separate, explicitly-confirmed step.

## The hook

`hook/contract_hook.py` is a `PreToolUse` hook for `AskUserQuestion` that enforces the contract on **every** question, not just inside the skill. **As of 2026-06-06 it is registered** in the project `.claude/settings.json` in **soft mode**.

- **Architecture:** a shared *parser* (finds contract gaps) feeding a `MODE`-gated *decision layer*.
- **`MODE=soft`** (default): never blocks; when an option is missing an Implication/Trade-offs/Why, it returns `additionalContext` reminding the model — which sharpens the *next* question (it can't reform the one already shown).
- **`MODE=strict`** (future): denies with an exact-template reason so the model fixes and retries; includes a per-session loop-breaker (gives up after 3 denials) and a bypass — a question whose `header` starts with `quick:` skips enforcement.

Set the mode with the `BTD_HOOK_MODE` env var (default `soft`).

**Enable** (use the `update-config` skill so it lands in the right `settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/skills/breakdown-to-decide/hook/contract_hook.py" }
        ]
      }
    ]
  }
}
```

**Disable:** remove that block (or set it aside) via the same skill.

### Where it's registered — and the trade-off (note for future-you)

It currently lives in **`.claude/settings.json`** — the **project-shared, committed** scope. The design spec wanted it there so the hook "travels with the repo." The implication: once this branch merges, the hook is active for **anyone** who uses this repo, and it fires on **every** `AskUserQuestion` in the project (soft mode, so only harmless nudges — it never blocks).

If that ever feels too broad — e.g. you want the contract enforced **only for you**, or to stop imposing it on a public repo's other users — move the same `hooks` block to **`.claude/settings.local.json`** (personal, git-ignored). Same behavior, just not shared/committed. Decision as of 2026-06-06: **left in `settings.json`** (the spec's intent; this is a personal sandbox). No action needed unless that calculus changes.

> Loading note: if you register or move it mid-session, run `/hooks` (or restart) so Claude Code's watcher picks up the change.

> Caveat: it's unverified whether `PreToolUse` fires inside subagent tool calls — confirm before relying on the hook to cover subagents.

## Future / revisit once live

Deliberately out of the MVP; add modularly if real usage calls for it:

- **Strict hook** (`MODE=strict`) — the deny + loop-breaker + `quick:` bypass upgrade, for *guaranteed* enforcement on ambient questions (outside a skill walk).
- **Durable decision record** — persist decisions to a file (path resolution / portability); append per-pick for resumability and so the recap can't drift.
- **Deferral routing** — e.g. append punted items to `TODO.md`.
- **Acting on decisions** — apply fixes vs. record + suggested next action; how a decision maps to a concrete action for non-code findings.
- **>4 options** — ranking rule + overflow UX (the widget caps at 4).
- **Large-N UX** — an optional fast bulk-triage pass vs. a threshold warning.
- **Findings-set confirmation** — enumerate + confirm when prior-context findings are ambiguous.
- **Subagent scope** — verify whether `PreToolUse` fires inside subagent tool calls.

## Development

- `evals/evals.json` — eval prompts (5 cases across code findings, stack decomposition, multi-select, under-specified, and a design-spec review).
- `evals/grading_criteria.md` — the iteration-2 grading spec (objective checks + an LLM judge on completeness/content/sequencing).
- `evals/objective_checks.py` — deterministic O1/O2 checks.
- Eval run outputs live in a sibling `breakdown-to-decide-workspace/` (git-ignored scratch).
- Design spec: `plans/2026-06-01-breakdown-to-decide-design.md`.
