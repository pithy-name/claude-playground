# Plan: Session-Log Dogfood + Guidance Cleanup

**Date:** 2026-06-07
**Status:** Active — dogfood phase blocks the cleanup phase.
**Supersedes/extends:** `plans/2026-06-07-memory-cleanup-list.md` (the *what-to-delete* bucket list). This doc adds the *when* (dogfood gate), the *contradiction watch-list*, and the *execution order*.

## Why

The `session-log` skill now carries the session-log conventions (they travel with the skill, globally). The old guidance for the same conventions still lives in three places:

- **Global `~/.claude/CLAUDE.md`** — the "Session Management" section.
- **Project `CLAUDE.md`** (this repo) — the "Session logs" section.
- **Per-repo auto-memories** — several `feedback_*` / location memories.

Right now skill + guidance **double up**. That is mostly harmless redundancy — *except* where the old guidance says something the skill now contradicts. Those contradictions can make a model emit a **hybrid, non-parser-conforming** log during the transition. Goal: prove the global skill wins in real sessions, then remove the stale guidance in safe order without leaving a vacuum.

## The contradictions to watch for (the dangerous bits)

Verified 2026-06-07 against `~/.claude/CLAUDE.md`, this repo's `CLAUDE.md`, and the skill (`~/.claude/skills/session-log/SKILL.md`). Each row is a place old guidance pulls *away* from a conforming log.

| # | Topic | Old guidance says | Skill (new) says | Risk if not removed |
|---|-------|-------------------|------------------|---------------------|
| 1 | **Filename** | `scratchpads/scratchpad-YYYY-MM-DD-topic.md` (date only, `scratchpad-` prefix) | `YYYY-MM-DDTHHMM-topic.md` (date **+ time**, no prefix) | Wrong filename; same-session collisions; topic/date drift |
| 2 | **Location** | Global: `scratchpads/` (repo root). Project: `.claude/session-logs/` (in-repo, gitignored) | Central `~/.claude/session-logs/<repo>/`, **outside any repo** | Log written into a (public) repo → privacy/leak risk — the whole reason for central storage |
| 3 | **Section structure** | Top-level siblings: What happened / Decisions / **Mistakes & corrections** / **Learnings about the user** / To-do | What happened / Decisions / **Learnings (H2)** → 3 H3s {Mistakes & corrections, What worked & what to repeat, User preferences & conventions} / To-do | Parser **non-conformance** (exit ≠ 0): missing the `## Learnings` wrapper + the 3 required H3s |
| 4 | **"What worked" section** | *absent* | Required H3 "What worked & what to repeat" (with `Why it worked:` on its own line) | Retro half-blind — captures what went wrong, not what to repeat |
| 5 | **"Learnings" meaning** ⚠️ | Only "**Learnings about the user**" exists | "Learnings" = **all three** subsections; user-prefs is just one | **Most insidious:** old wording reinforces the exact bug the skill fixes — "capture learnings" → model writes only user-prefs |
| 6 | **H1 title** | unspecified | Exact `# Session Log — [Topic]` (parser keys on it) | Parser can't extract topic → non-conformance |
| 7 | **Start-time acquisition** | `feedback_journal_timestamp`: *always ask the user for session start time* | SessionStart hook auto-stamps; present-time is an accepted fallback | Needless friction; conflicts with the automated flow |
| 8 | **Timestamp for updates** | `feedback_scratchpad_timestamps`: run `date` before each update header | `inject_timestamp` PreToolUse hook supplies it automatically | Not contradictory — **redundant/automated**. Safe to retire once hook is trusted |
| 9 | **Chronological append** | `feedback_session_log_chronological` | Skill states the same rule | Redundant, not contradictory — skill supersedes |
| 10 | **Old location memories** | `feedback_journals_location` (`.claude/journals/`), `feedback_session_log_terminology` (`.claude/session-logs/`) | Central `~/.claude/session-logs/<repo>/` | Stale locations actively contradict central storage |

**During dogfood, the tells that the skill is NOT winning:** a log named `scratchpad-…`; a log written inside a repo; a flat `## Mistakes & corrections` / `## Learnings about the user` instead of the nested `## Learnings` block; only the user-prefs subsection filled when asked for "learnings"; the model asking for the session start time instead of using the hook stamp. Any of these → old guidance still has a grip; do **not** start cleanup.

## Phase 1 — Dogfood (gates Phase 2)

**Do not remove any guidance until ALL of these hold:**

1. PRs #8 (breakdown-to-decide) and #9 (session-log) are merged to `main`.
2. At least one **restart / fresh session** has occurred so the global hooks actually load (this build session's hooks were project-level).
3. The global skill auto-fires correctly in **≥2 different repos** across **~3–5 real sessions**: log auto-created at the central path, conforming filename, sections maintained — **without** the user prompting "start at the top / update every section."
4. `parse_session_log.py` exits 0 on those real logs (not just test stubs).
5. No watch-list tell (above) observed in those sessions.

**Record during dogfood:** for each real session, note repo, whether the log auto-created, parser exit code, and any watch-list tell. A short tally is enough — if a tell recurs, fix the **skill** (description/SKILL.md wording) before blaming the old guidance.

## Phase 2 — Cleanup (only after the gate passes)

Order is low→high blast radius. **Back up first:** `tar` `~/.claude/projects/*/memory/` before any memory delete (auto-memory is machine-local, no cloud copy).

1. **This repo's `CLAUDE.md`** — replace the "Session logs" section (line ~26–28, the `.claude/session-logs/` claim) with a one-line pointer: *"Session logs handled by the `session-log` skill (central store `~/.claude/session-logs/<repo>/`)."* Do **not** leave a vacuum.
2. **This repo's auto-memories (Bucket A subset present here):** confirm content, then delete `feedback_journals_location.md`, `feedback_session_log_terminology.md`, and re-evaluate `feedback_session_log_chronological.md` / `feedback_scratchpad_timestamps.md` / `feedback_journal_timestamp.md` (retire only what the skill+hooks fully cover). Update this repo's `MEMORY.md` index.
3. **Global `~/.claude/CLAUDE.md`** — remove the "Session Management" section; replace with a one-line pointer to the skill. This is the highest-leverage change (affects every repo) — do it only after the skill is proven global.
4. **Cross-repo memories** — run the full `plans/2026-06-07-memory-cleanup-list.md` Bucket A across the ~8 project memory dirs (the slog the memory-curation skill is meant to automate). Confirm each file's content (plan classifies by filename only) before deleting; update each `MEMORY.md`.

**Keep (NOT session-log conventions — do not remove):** `feedback_github_pii_permanent`, `feedback_pii_scan_patterns`, `feedback_git_push`, `feedback_check_branch_before_work`, `feedback_language_precision`, and the verify-before-presenting / commit-approval rules in CLAUDE.md.

## Phase 3 — Deterministic governance tool (automates the gate)

The Phase 1 gate and the watch-list are mechanical — automate them. A single stdlib Python script over `~/.claude/` (no network, no LLM, path-agnostic via `Path.home()`) produces a GREEN/RED verdict on "safe to remove the old guidance." Runs across **all Claude workspaces on this machine**.

**Four deterministic scans:**

1. **Trigger audit** — glob `~/.claude/projects/*/*.jsonl`; count `Skill` tool calls whose input skill is `session-log` / `breakdown-to-decide`, grouped by project (decode the slug). Reuses what `session-report` already parses — build-vs-buy: don't reinvent the transcript reader. Answers "when/where did the skill fire."
2. **Conformance** — run `parse_session_log.py` over every file in `~/.claude/session-logs/*/`; report conforming %, list non-conformers + reason.
3. **Stale-guidance presence** — grep global `~/.claude/CLAUDE.md`, decoded per-repo `CLAUDE.md`s, and every `~/.claude/projects/*/memory/*.md` for the watch-list markers (`scratchpad-` filename pattern, in-repo `.claude/session-logs/`, "Learnings about the user", journals location). Tells you whether cleanup is pending or done.
4. **Watch-list tells** — flag any central log named `scratchpad-*`; any session log written *inside* a repo working tree; any conforming-required H3 missing.

**Verdict logic:** GREEN to remove guidance only when conformance = 100% over central logs from **≥2 distinct repos**, **≥3 sessions** show the skill triggering, and **zero tells**. Else RED with the specific blockers. Thresholds are tunable constants.

**Delivery surface (pick later):** a one-shot CLI report; a `SessionStart` hook line that prints the verdict each session ("dogfood 3/5 repos, 100% conforming — gate RED, keep going"); and/or a `/schedule` weekly run. Bundle the script with the skill (`scripts/`) so it travels and is runnable in any workspace.

**The non-deterministic seam (explicitly out of scope for this tool):** transcripts show when a skill *did* fire, not when it *should have but didn't* (false negatives), nor whether the output was *useful*. That needs an LLM-judge over a random sample of sessions — a separate, occasional, qualitative pass. Keep it out of the deterministic gate; track it as a follow-up.

## Safety / rollback

- Memory backup tar is the rollback for deletes.
- CLAUDE.md edits are git-tracked (global CLAUDE.md: confirm whether it's under version control before editing; if not, copy it aside first).
- If a watch-list tell reappears *after* cleanup, the fix is to harden the skill, not to re-add the old guidance.

## Open questions

- Pointer vs. full removal in CLAUDE.md — confirmed leaning *pointer* (avoid silent loss if skill disabled). OK?
- Build the memory-curation skill first and use Bucket A as its test case, or do the cross-repo pass by hand this once?
