# Plan: Cross-Project Memory Curation

**Date:** 2026-06-06
**Status:** Idea — not started (captured from the session-log build session)

## Problem

Claude Code's memory model leaves broadly-useful lessons stranded in one repo:

- **Auto-memory** (`~/.claude/projects/<repo>/memory/`, with a `MEMORY.md` index) is **strictly per-repo**, keyed by the git repo. It loads only when the working directory is in that repo. (Worktrees of the same repo share it.)
- **Global `~/.claude/CLAUDE.md` is the only cross-project memory surface.** There is no global equivalent of the per-repo auto-memory directory.
- **No built-in promotion.** Moving a memory from a repo scope to global is manual copy/paste; `/memory` only browses/edits, `#` only appends.
- **No existing tool curates cross-project memory.** `claude-automation-recommender` and `claude-md-improver` operate on `CLAUDE.md` files, not the `~/.claude/projects/*/memory/` auto-memory. (Confirmed against code.claude.com/docs.)

Net effect: general feedback (e.g. "grep -w for short tokens", broadly-useful conventions) gets written into whatever repo happened to be open, then never loads anywhere else — so the same lesson is re-taught per repo.

## Why it matters

- **Lost leverage** — general lessons don't propagate; corrections repeat across repos.
- **Bloat risk if promoted carelessly** — docs say keep each `CLAUDE.md` under ~200 lines; naive promotion would balloon global.

## Proposed remediation — a memory-curation skill

**What it does:**
1. Scan `~/.claude/projects/*/memory/*.md` across all projects.
2. Classify each: project-specific (keep) vs broadly-useful (promotion candidate). Heuristics — `type: feedback`/`user`; no project-specific nouns (repo/service/file names); guidance that generalizes.
3. Detect near-duplicates across repos (same lesson learned separately) → merge candidates.
4. Present candidates to the user **one at a time** (reuse the `breakdown-to-decide` contract): promote / keep / merge, each with implication + trade-offs + a recommendation.
5. On approval: move/copy to the chosen global surface, keeping global lean; optionally leave a pointer in the source memory.
6. Optionally set up `.claude/rules/` **symlinks** to share a curated rule-set across repos without duplication (the docs-supported sharing mechanism).

**When it triggers:** user-invocable (e.g. `/curate-memories`, "promote my memories", "which memories should be global?"); optionally a periodic/weekly audit.

## Scope

- **v1 in:** scan + classify + dedup-detect + one-at-a-time review + promote-on-approval.
- **Deferred:** auto-promotion without review; cross-machine sync (auto-memory is machine-local); rewriting/condensing memory prose; automatic `.claude/rules/` symlink management.

## Open questions

- **Promotion target:** global `~/.claude/CLAUDE.md` vs a dedicated global rules file vs `.claude/rules/` symlinks — which surface (or a mix)?
- **Classification:** cheap heuristics vs an LLM judging "generality"?
- **Keeping global <200 lines:** condense on promote, or shard via path-scoped rules?
- **Build-vs-buy:** re-scan the skills registry before building — confirm nothing has appeared.

## Related

The `session-log` skill is the model for the inverse insight: **workflow knowledge belongs in a skill (which travels), not in per-repo memories.** Promoting the session-log skill globally is what makes *its* conventions cross-project — memory curation handles everything that genuinely belongs in memory rather than a skill.
