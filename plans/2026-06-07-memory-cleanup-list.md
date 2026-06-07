# Plan: Session-Log Memory Cleanup

**Date:** 2026-06-07
**Status:** Ready to execute **after** the session-log skill is promoted globally + validated.

## Context

The session-log skill now carries the session-log conventions (they travel with the skill, not as per-repo memories). So memories that only **restate skill-covered conventions** are redundant → delete; broadly-useful **general** memories → promote to global `~/.claude/CLAUDE.md`; the rest stay. This is the first real job for the memory-curation skill (`plans/2026-06-06-memory-curation-design.md`).

## Hard rules

- **Back up first:** `tar` `~/.claude/projects/*/memory/` before any delete — deletion is destructive and auto-memory is machine-local (no cloud copy).
- **Confirm each file's content before acting** — buckets below are classified by **filename** (heuristic), not full content review.
- After deletes/promotions, update each affected `MEMORY.md` index.

## Scope (grep, 2026-06-06)

- Global `~/.claude/CLAUDE.md`: **9 hits** — the "Session Management" section. Remove it (the skill replaces it).
- **46 memory files** across ~8 project memory dirs (`~/.claude/projects/<slug>/memory/`) mention scratchpad / session-log / journal. Most are keepers; only the convention ones below are delete candidates.

## Bucket A — DELETE (session-log/scratchpad/journal conventions now in the skill)

Confirm each restates only skill-covered conventions, then delete:

- `feedback_session_log_terminology.md`
- `feedback_session_log_chronological.md`
- `feedback_session_log_depth.md`
- `feedback_session_log_session_start_date.md`
- `feedback_journal_timestamp.md`
- `feedback_journals_location.md`
- `feedback_scratchpad_timestamps.md`
- `project_session_log_location.md`
- `session-logs-directory.md`
- `feedback_datetime_headers_scratchpads.md`

## Bucket B — PROMOTE to global `~/.claude/CLAUDE.md` (confirm generality + the <200-line budget)

Broadly-useful working-style memories worth loading everywhere (review content + dedupe before moving):

- `feedback_process_corrections_global.md` (already about global scope)
- `feedback_timestamps_run_date.md`
- `feedback_language_precision.md`
- `feedback_cheap_lookups_first.md`
- `feedback_self_contained_specs.md`
- `feedback_github_pii_permanent.md`

## Bucket C — KEEP

Everything else — project-specific or domain feedback unrelated to session-log conventions.

## Process

1. Back up the memory dirs.
2. Bucket A: open → confirm skill-covered → delete → update that `MEMORY.md`.
3. Bucket B: open → confirm generality → merge into global `CLAUDE.md` (keep < 200 lines) → delete source or leave a pointer.
4. Remove the global `CLAUDE.md` "Session Management" section.
5. Re-grep to confirm.

Doing this by hand across ~8 dirs is the slog the **memory-curation skill** (`plans/2026-06-06-memory-curation-design.md`) is meant to automate — consider building it first and using this as its test case.
