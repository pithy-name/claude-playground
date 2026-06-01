# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal sandbox for exploring Claude Code features — primarily skills and automation.

## Active skills

- `gitignore-init` — automatic; runs on first repo exploration; creates `.gitignore` if absent, then delegates to `gitignore-checker`
- `gitignore-checker` — automatic; runs whenever a `.gitignore` is read/created/edited; ensures `.DS_Store` and `.env` entries are present
- `meetgeek-to-md` — user-invocable; converts MeetGeek DOCX transcript exports to clean markdown
- `session-report` — user-invocable; project-scoped override of the session-report plugin
- `session-journal` — automatic; 🧪 experimental, superseded by the Session logs workflow below; creates per-session journal entries

## Tools

- `tools/` — standalone HTML tools, each in its own subdirectory. For any third-party tool, retain the upstream LICENSE in its subdirectory and verify license compliance before committing.

## Plans

Design specs for in-progress work live in `plans/` at the repo root, named `YYYY-MM-DD-<topic>-design.md`. A plan is reviewed and approved before the work it describes is built.

## Session logs

Session logs live at `.claude/session-logs/` (the project's term for what the global default calls "scratchpads"). Gitignored.

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
