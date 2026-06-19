# breakdown-to-decide

*A Claude Code skill that walks you through a pile of decisions one question at a time, with explicit choice implications and trade-offs.*

**Maturity:** v1.0 · **Type:** User-invocable (`/breakdown-to-decide`) + auto-trigger, with a soft PreToolUse hook

## What it is

When Claude comes at you with a dozen decisions to make, this skill makes Claude present them **one at a time** via the `AskUserQuestion` tool, structured to convey the issue, why it matters, your options (each with its implications and trade-offs), and a recommendation. You decide, then get a recap.

## The problem it solves

A wall of open-ended questions is overwhelming — where do you even start? Front-loading the reasoning (implications + trade-offs), providing a recommendation, and sequencing the choices keeps your nervous system calm and lets you make well-informed decisions.

## Components

- **`SKILL.md`** — the skill itself (the one-at-a-time walk + the decision contract Claude follows).
- **`hook/contract_hook.py`** — an *optional* `PreToolUse` hook that enforces the contract on every `AskUserQuestion`, not just inside the skill. **Soft by default:** it only nudges, never blocks.
- **`README.md`** — this file.
- **`evals/`** — test prompts + grading used to develop the skill (not needed to run it).

## Install

For now, copying the directory is the only way to get the skill + hook (bundled/pre-packaged plugin planned for future):

1. **Copy the whole `breakdown-to-decide/` directory** into your `.claude/skills/`:
   - For one project: `<your-project>/.claude/skills/breakdown-to-decide/`
   - For all projects: `~/.claude/skills/breakdown-to-decide/`

2. **(Recommended) Turn on the hook** so the contract is softly enforced on every `AskUserQuestion`. Add this to your `settings.json`'s `hooks` block, pointing at wherever you copied the skill:
   - For one project: add to `.claude/settings.json` + use `$CLAUDE_PROJECT_DIR` in the command path (as below)
   - For all projects: add to `~/.claude/settings.json` + use `$HOME` in the command path instead

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "AskUserQuestion",
           "hooks": [
             { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/skills/breakdown-to-decide/hook/contract_hook.py\"", "statusMessage": "Checking decision contract" }
           ]
         }
       ]
     }
   }
   ```

   Then run `/hooks` (or restart) so Claude Code loads it. **Verify:** `/hooks` should now list a `PreToolUse` → `AskUserQuestion` entry. Your next decision card will be contract-checked.

   **TIP (Optional, not recommended):**
      - Want the hook to *block* until each question meets the contract, not just nudge? Set `BTD_HOOK_MODE=strict` in your settings's `env`, sibling to `hooks`. Default is `soft`.
      - Not recommended because this level of detail can easily become overkill.

   ```json
   {
     "env": {
       "BTD_HOOK_MODE": "strict"
     },
     "hooks": {
       "PreToolUse": [ ... the breakdown hook ... ]
     }
   }
   ```

## How to use it

- The skill kicks in naturally after a review/audit produces several findings. It is also triggered when you signal indecision: *"walk me through these one by one,"* *"break it down for me,"* *"I don't know where to start,"* *"help me weigh my options."*
- You can also type **`/breakdown-to-decide`** or just describe a pile of choices in your own words.
- Claude presents you with the **`AskUserQuestion`** tool. See the [developer documentation](https://code.claude.com/docs/en/agent-sdk/user-input#handle-clarifying-questions) for more info on how the tool works and its limitations.
- At the end you get a short recap of what you chose. (It doesn't apply changes — acting on a decision is a separate, explicit step.)

Two rules the skill holds to: 
   1. **decompose completely:** surface the foundational decision that constrains the rest first
   2. **keep it tight:** a sentence or two per segment

---

*Everything below is reference — you don't need it to use the skill.*

## How it works — the decision contract

Every decision is presented this way:

- **Issue** — what was raised.
- **Why it matters** — the impact/risk if left unaddressed.
- **Options** (2–4), each carrying an **Implication** (what choosing *this* causes) and **Trade-offs** (gain vs. give up *vs. the other options*).
- A **recommendation** with a **Why**
   - single-select: the recommended option is first, labelled `(Recommended)`
   - multi-select: each recommended option is marked (a recommended *set*).

**The hook** mirrors this as a machine check. A shared parser finds gaps (an option missing Implication/Trade-offs, or no recommended option with a Why); the `MODE`-gated decision layer then either nudges (`soft`, default — returns a reminder, never blocks) or denies-and-asks-for-a-fix (`strict` — with a per-session loop-breaker and a `quick:`-header bypass for trivial questions). It only encodes the segment *keys* (`Implication` / `Trade-offs` / `Why`); the contract above is the source of truth. Note: `AskUserQuestion` is unavailable inside subagents, so the hook only applies to the main session.

## How it was built

Designed spec-first, then built and measured with the `skill-creator` eval harness. Five eval cases (code-review findings, stack decomposition, multi-select auth hardening, an under-specified "what do you think?", and a design-spec review) run with-skill vs. a no-skill baseline, graded by a deterministic objective check plus a calibration-gated LLM judge (reference decision sets, completeness, recommendation quality). Latest run: **100%** with-skill vs **97%** baseline — the skill's distinctive wins are decomposition completeness and inducing the structured walk when you didn't explicitly ask. Dev artifacts:

- `evals/evals.json` — the 5 eval prompts.
- `evals/grading_criteria.md` — the grading spec (objective + semantic judge).
- `evals/objective_checks.py` — deterministic checks.
- Eval run outputs land in a sibling `breakdown-to-decide-workspace/` (git-ignored scratch; *not bundled*).
- Design spec (source repo only, *not bundled*): `plans/2026-06-01-breakdown-to-decide-design.md`.

## Future Improvements

### Shipping it as a plugin

A bare `.skill` package can't carry the hook (registration doesn't travel), so to make the skill **and** hook install + activate as one unit — and to publish for others — package it as a **Claude Code plugin**:

```
breakdown-to-decide-plugin/
├── .claude-plugin/plugin.json     # name, description, version
├── skills/breakdown-to-decide/    # this skill
└── hooks/hooks.json               # the PreToolUse hook, command via ${CLAUDE_PLUGIN_ROOT}
```

Installing the plugin registers the skill and activates the hook automatically. Distribute via a git-based marketplace (`.claude-plugin/marketplace.json` → the plugin repo); users `/plugin install`. Don't commit built `.skill`/`.zip` artifacts — the git source is the distribution.

### Revisit once live

- **Strict hook by default** — once the soft nudge has proven itself.
- **Durable decision record** — persist decisions to a file (append per-pick for resumability) beyond the in-chat recap.
- **Deferral routing** — e.g. append punted items to a backlog.
- **Acting on decisions** — apply fixes vs. record + suggested next action; mapping a decision to a concrete action for non-code findings.
- **Large-N UX** — an optional fast bulk-triage pass before the deep walk.
- **Findings-set confirmation** — confirm which set when prior-context findings are ambiguous.
- **>4 options** — the picker is [limited](https://code.claude.com/docs/en/agent-sdk/user-input#limitations) to 4 options.
