# session-log governance

> ℹ️ **Status: experimental — vetted 2026-06-13.** Test-run and working: its 15 unit tests pass and a read-only `python3 governance.py` (no flags) produces a coherent verdict. As of that run the gate reads **RED** — the skills haven't been dogfooded across enough sessions/repos yet to safely remove the old backup guidance, which is the correct conservative answer, not a failure. Note: `install_schedule.sh` (which registers a weekly launchd job) has **not** been reviewed or installed — don't run it without review. The skills graduated to global on lived experience, independent of this gate.

A deterministic **GREEN/RED gate** — no LLM, no network — that answers one question:

> Is it safe yet to remove the old session-log guidance from `CLAUDE.md` files and auto-memories?

## TL;DR

- **What it does:** scans `~/.claude` across every workspace on this machine — counts when the skill fired, runs the parser on every session log, greps for leftover old guidance — and prints **GREEN** (safe to delete the old guidance) or **RED + the reasons**.
- **What it needs from you:** *dogfood* the skill in real sessions across ≥2 repos so it has data to judge; when it flips **GREEN**, give the go-ahead to delete the old guidance.
- **Why it matters:** replaces guessing "is the skill ready?" with a hard repeatable check, and stops you deleting the safety-net guidance too early (which would leave a gap where neither skill nor guidance fires).

## Why this exists

The session-log conventions now travel with the **skill**. The same conventions are *also* still written into a global `CLAUDE.md` "Session Management" section, per-project `CLAUDE.md`s, and several auto-memories — redundant, and in places contradictory with the skill. Deleting that old guidance is only safe once the skill has demonstrably taken over: it triggers reliably and produces parser-conforming logs across real sessions. This tool measures exactly that. Full rollout plan: `plans/2026-06-07-session-log-dogfood-and-cleanup-plan.md`.

## Files

| File | What it is |
|------|-----------|
| `governance.py` | The scanner + gate. Reads `~/.claude`, prints a verdict, optionally writes a report. |
| `test_governance.py` | 15 `unittest` cases over a fixture tree (never touches real `~/.claude`). |
| `install_schedule.sh` | Installs a weekly macOS **launchd** job that refreshes the report. |
| `README.md` | This file. |

It is a **scanner**, not a parser — for the conformance scan it shells out to the skill's real `../scripts/parse_session_log.py`.

## How to run it

```bash
python3 governance.py                                   # human-readable report to stdout
python3 governance.py --json                            # machine-readable
python3 governance.py --md-report ~/.claude/governance-report.md   # write/refresh the running report
```

Exit code: **0 = GREEN**, **1 = RED**. Runs from anywhere (resolves its own paths). Reads `~/.claude`, so it must run as you, on this machine. To point it at a fixture (what the tests do): `SESSION_LOG_GOVERNANCE_ROOT=/path/to/fake/.claude`.

## What GREEN / RED mean, and what it tests

> **This gate is NOT about merging PRs.** The skills can (and should) be merged and promoted globally before this gate matters. GREEN/RED answers a separate question that comes *after* the skills are live: have they proven themselves in enough real sessions to safely delete the old backup guidance?

- **GREEN** — the skill has taken over everywhere; the old guidance is now pure redundancy → safe to delete.
- **RED** — the skill isn't proven yet, or drift exists; deleting now risks a gap. The blockers say what's missing.

GREEN requires **all 5**:

1. the log parser is available;
2. **every** central session log conforms (parser exit 0) — 100%;
3. conforming logs exist in **≥ `MIN_REPOS`** different repos (default 2);
4. the session-log skill fired in **≥ `MIN_SESSIONS`** sessions (default 3);
5. **zero "tells"** — no `scratchpad-`named logs, no logs written *inside* a repo.

**Fail-safe:** empty root, missing parser, or zero logs → always RED, never GREEN-by-default. Stale-guidance *presence* is reported but is **not** a GREEN blocker — its whole purpose is to be deleted, so its existence doesn't make deletion unsafe. Thresholds are module constants (`MIN_REPOS`, `MIN_SESSIONS`, `PARSER_TIMEOUT`).

## How it works (the four scans)

1. **`cwd_map`** — for each `~/.claude/projects/<slug>/`, read the newest transcript and pull its real `cwd`. The slug dir name is a *lossy* encoding of the path (`/` `.` `_` all become `-`), so it is never reverse-decoded — the true `cwd` comes from the transcript records.
2. **Trigger audit** — scan every `*.jsonl`; for each `Skill` tool-use block (`message.content[].input.skill`), count `session-log` / `breakdown-to-decide` invocations per repo and track distinct sessions as `(slug, transcript-stem)` pairs.
3. **Conformance** — run `parse_session_log.py` on every `~/.claude/session-logs/*/*.md`; exit 0 = conforming. Report the rate + the set of distinct repos with ≥1 conforming log. Hardened: UTF-8 with replacement, a subprocess timeout, exception catches — any failure counts as non-conforming (fail safe).
4. **Stale-guidance presence** — regex markers (`scratchpad-YYYY`, `.claude/session-logs`, `Learnings about the user`, `# Session Management`, `scratchpads/`) over the global + per-repo `CLAUDE.md`s, plus a known set of stale memory filenames. The *to-delete inventory*.
5. **Tells** — old behavior still happening: a non-conforming central log, a `scratchpad-`named central log, or a `scratchpads/` · `.claude/session-logs/` · `.claude/journals/` directory **inside a repo** still holding `.md` files.

## The running report (`--md-report`)

`--md-report PATH` appends this run to an append-only sibling `.<name>-history.jsonl` (the data of record), then **regenerates** the markdown report at `PATH` from the full history — so the GREEN/RED **tally is counted, not re-parsed from prose**. You read the `.md`; the `.jsonl` is plumbing you can ignore. Default `PATH` is `~/.claude/governance-report.md`.

The report contains: a static explanation of GREEN/RED + the 5 checks; a **Tally** (`GREEN: n  RED: n  since <date>`); a **History** table (one row per run, newest first: date, verdict, conformance, repos, sessions, tells); and **Latest detail** (blockers, non-conforming logs + reasons, stale-guidance counts, the tells list).

> The generated report holds absolute machine paths — it lives under `~/.claude/`, is **machine-local, and must never be committed** to a public repo. The code here is path-agnostic and safe to commit.

## Scheduling (macOS, launchd)

```bash
bash install_schedule.sh              # weekly, Mondays 09:00 -> refreshes ~/.claude/governance-report.md
bash install_schedule.sh --uninstall
```

launchd (not cron) is used deliberately: it runs a missed run on next **wake**, so the weekly check still fires if the Mac was asleep. The installer resolves `python3` and all paths from `$HOME` at install time and writes the plist to `~/Library/LaunchAgents/sessionlog.governance.plist` — nothing hardcodes a username. **Requires the skill installed globally** (`~/.claude/skills/session-log/`) so the scheduled path exists. A scheduled run is deterministic and needs no LLM — which is why a local job is the right tool here, not a Claude-driven scheduler.

## What it deliberately does NOT do

Being deterministic, it only sees what *did* happen. It cannot tell you the skill *should* have fired but didn't (a false negative), nor whether a log was actually *useful*. That needs an LLM-judge over a random sample of sessions — a separate, occasional, qualitative pass, kept out of this gate on purpose (Phase 3 follow-up in the rollout plan).

## Tests

```bash
python3 test_governance.py     # 15 cases, ~0.3s
```

Each builds a fake `~/.claude` in a tempdir (fake projects, transcripts, central logs, repo cwds) via `SESSION_LOG_GOVERNANCE_ROOT`, and asserts each scan, both verdicts, the running report (accumulation + newest-first ordering + corruption tolerance), and robustness (malformed JSON lines, non-UTF8 bytes, empty root). They use the **real** parser, so a parser regression also trips them.
