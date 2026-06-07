# breakdown-to-decide

*A Claude Code skill that walks you through a pile of decisions one at a time — each as a clear, structured choice — instead of dumping them all at once.*

## What it is

When you're facing several decisions or findings to resolve, this skill makes Claude present them **one at a time**. Each one comes as a structured choice — the issue, why it matters, your options (each with its implications and trade-offs), and a recommendation — captured with Claude Code's `AskUserQuestion` picker. You decide each, then get a recap.

## The problem it solves

A wall of ten findings gets a worse response than the same ten taken one at a time. Dumping everything at once is exactly when people freeze or rubber-stamp. Front-loading the thinking (implications + trade-offs + a reasoned recommendation) and sequencing the choices lets you make a real call on each, fast.

## Components

- **`SKILL.md`** — the skill itself (the one-at-a-time walk + the decision contract Claude follows).
- **`hook/contract_hook.py`** — an *optional* `PreToolUse` hook that enforces the contract on **every** `AskUserQuestion`, not just inside the skill. Soft by default: it only nudges, never blocks.
- **`README.md`** — this file.
- **`evals/`** — test prompts + grading used to develop the skill (not needed to run it).

## Install

There's no one-click install yet (bundling as a plugin is future work — see the bottom). For now:

1. **Copy the whole `breakdown-to-decide/` directory** into your `.claude/skills/`:
   - For one project: `<your-project>/.claude/skills/breakdown-to-decide/`
   - For all your projects: `~/.claude/skills/breakdown-to-decide/`

   That gives you the skill **and** the hook script. (Copying the directory is the only way to get the hook without a plugin.)

2. **(Optional) Turn on the hook** so the contract is enforced on every `AskUserQuestion`. Add this to `settings.json` — `.claude/settings.json` for one project, or `~/.claude/settings.json` for all of them — pointing at wherever you copied the skill:

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

   Then run `/hooks` (or restart) so Claude Code loads it. The hook needs `python3`.

### Globalize it (use it everywhere)

Copy the directory to `~/.claude/skills/breakdown-to-decide/` and register the hook in **`~/.claude/settings.json`** — but point the command at the global path (not `$CLAUDE_PROJECT_DIR`, which is per-project):

```json
{ "type": "command", "command": "python3 \"$HOME/.claude/skills/breakdown-to-decide/hook/contract_hook.py\"", "statusMessage": "Checking decision contract" }
```

(Want it to *block* until each question meets the contract, not just nudge? Set `BTD_HOOK_MODE=strict` in your settings `env`. Default is soft.)

## How to use it

- Type **`/breakdown-to-decide`**, or just describe a pile of choices in your own words: *"walk me through these one by one,"* *"break it down for me,"* *"I don't know where to start,"* *"help me weigh my options."* It also kicks in naturally after a review/audit produces several findings.
- Claude presents your decisions in a **single `AskUserQuestion` card** (up to 4 at a time) that you navigate with prev/next and submit once; more than four are chunked. A decision that depends on an earlier answer is asked on its own first.
- At the end you get a short recap of what you chose. (It doesn't apply changes — acting on a decision is a separate, explicit step.)

---

*Everything below is reference — you don't need it to use the skill.*

## How it works — the decision contract

Every decision is presented this way:

- **Issue** — what was raised.
- **Why it matters** — the impact/risk if left unaddressed.
- **Options** (2–4), each carrying an **Implication** (what choosing *this* causes) and **Trade-offs** (gain vs. give up *vs. the other options*).
- A **recommendation** with a **Why** — single-select: the recommended option is first, labelled `(Recommended)`; multi-select: each recommended option is marked (a recommended *set*).

Two rules the skill holds to: **decompose completely** (surface the foundational decision that constrains the rest first; don't stop short — under-decomposing is the main failure mode) and **keep it tight, keep your voice** (a sentence or two per segment; the structure is a skeleton, not a straitjacket).

**The hook** mirrors this as a machine check. A shared parser finds gaps (an option missing Implication/Trade-offs, or no recommended option with a Why); the `MODE`-gated decision layer then either nudges (`soft`, default — returns a reminder, never blocks) or denies-and-asks-for-a-fix (`strict` — with a per-session loop-breaker and a `quick:`-header bypass for trivial questions). It only encodes the segment *keys* (`Implication` / `Trade-offs` / `Why`); the contract above is the source of truth. Note: `AskUserQuestion` is unavailable inside subagents, so the hook only applies to the main session.

## How it was built

Designed spec-first, then built and measured with the `skill-creator` eval harness. Five eval cases (code-review findings, stack decomposition, multi-select auth hardening, an under-specified "what do you think?", and a design-spec review) run with-skill vs. a no-skill baseline, graded by a deterministic objective check plus a calibration-gated LLM judge (reference decision sets, completeness, recommendation quality). Latest run: **100%** with-skill vs **97%** baseline — the skill's distinctive wins are decomposition completeness and inducing the structured walk when you didn't explicitly ask. Dev artifacts:

- `evals/evals.json` — the 5 eval prompts.
- `evals/grading_criteria.md` — the grading spec (objective + semantic judge).
- `evals/objective_checks.py` — deterministic checks.
- Eval run outputs land in a sibling `breakdown-to-decide-workspace/` (git-ignored scratch; *not bundled*).
- Design spec (source repo only, *not bundled*): `plans/2026-06-01-breakdown-to-decide-design.md`.

## Shipping it as a plugin (future)

A bare `.skill` package can't carry the hook (registration doesn't travel), so to make the skill **and** hook install + activate as one unit — and to publish for others — package it as a **Claude Code plugin**:

```
breakdown-to-decide-plugin/
├── .claude-plugin/plugin.json     # name, description, version
├── skills/breakdown-to-decide/    # this skill
└── hooks/hooks.json               # the PreToolUse hook, command via ${CLAUDE_PLUGIN_ROOT}
```

Installing the plugin registers the skill and activates the hook automatically. Distribute via a git-based marketplace (`.claude-plugin/marketplace.json` → the plugin repo); users `/plugin install`. Don't commit built `.skill`/`.zip` artifacts — the git source is the distribution.

## Future / revisit once live

- **Strict hook by default** — once the soft nudge has proven itself.
- **Durable decision record** — persist decisions to a file (append per-pick for resumability) beyond the in-chat recap.
- **Deferral routing** — e.g. append punted items to a backlog.
- **Acting on decisions** — apply fixes vs. record + suggested next action; mapping a decision to a concrete action for non-code findings.
- **>4 options** — ranking + overflow UX (the picker caps at 4).
- **Large-N UX** — an optional fast bulk-triage pass before the deep walk.
- **Findings-set confirmation** — confirm which set when prior-context findings are ambiguous.
