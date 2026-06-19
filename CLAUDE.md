# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal sandbox for exploring Claude Code features — primarily skills and automation.

## Skills

Skills live in `skills/` as a **publishable library** — source to copy or globalize, **not auto-loaded by this repo**. Claude Code only discovers skills under `.claude/skills/` (project) or `~/.claude/skills/` (global), so nothing in `skills/` runs here on its own. Two are installed globally and drive this repo's runtime: `session-log` and `breakdown-to-decide`. Pattern: develop a skill here; run the global (production) copy. The trigger types below describe each skill's behavior **where it is installed**, not in-repo.

- `gitignore-init` — automatic; creates `.gitignore` if absent, then delegates to `gitignore-checker`
- `gitignore-checker` — automatic; ensures `.DS_Store` and `.env` entries are present in a `.gitignore`
- `meetgeek-to-md` — user-invocable; converts MeetGeek DOCX transcript exports to clean markdown
- `session-report` — user-invocable; project-scoped override of the session-report plugin
- `session-journal` — automatic; 🧪 experimental, superseded by the Session logs workflow below; creates per-session journal entries
- `session-log` — automatic; installed globally; produces the session logs described below
- `breakdown-to-decide` — user-invocable (`/breakdown-to-decide`) + auto-triggers on decision overwhelm; walks a set of decisions one at a time (issue / why / options with implications + trade-offs / recommendation) via `AskUserQuestion`. Ships a PreToolUse hook (`hook/contract_hook.py`, **soft mode** — never blocks) that nudges any `AskUserQuestion` whose options miss the contract; register it per the skill README (this repo relies on the global install, not a tracked project `.claude/settings.json`). Spec: `plans/2026-06-01-breakdown-to-decide-design.md`.

## Tools

- `tools/` — standalone HTML tools, each in its own subdirectory. For any third-party tool, retain the upstream LICENSE in its subdirectory and verify license compliance before committing.

## Plans

Design specs for in-progress work live in `plans/` at the repo root, named `YYYY-MM-DD-<topic>-design.md`. A plan is reviewed and approved before the work it describes is built.

## Session logs

Session logs are produced by the `session-log` skill and stored **centrally** at `~/.claude/session-logs/<repo>/` — outside any repo, so they're never a public-repo privacy risk and need no per-project `.gitignore`. The repo's `.gitignore` lists `.claude/` (which covers `.claude/session-logs/`) as belt-and-suspenders against stray local writes.

## Workflow

- Single-responsibility branches (one logical change per branch/PR)
- Squash merge to `main`
- Always ask before committing or pushing (no auto-chain)
- Backlog and planned work live in `TODO.md` at the repo root

## Privacy rules

This is a public repo. All files must be free of PII and absolute paths.

- No real names, email addresses, employer names, client names, or other identifying information
- No absolute paths — use relative paths or placeholders
- Before staging any file, check it against these rules
- If a file contains PII or an absolute path, **flag it immediately and do not commit it**
- Before committing, verify `git config user.name` is `pithy-name` and `git config user.email` is `pithy.name@fastmail.com`; if not, stop and flag it
