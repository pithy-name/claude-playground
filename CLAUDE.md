# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal sandbox for exploring Claude Code features — primarily skills and automation.

## Skill system

Skills live in `.claude/skills/<skill-name>/SKILL.md`. Each file has a YAML frontmatter header followed by instructions.

**Frontmatter fields:**
- `name` — identifier
- `description` — when to apply (used as the trigger condition)
- `user-invocable` — if `true`, can be called with `/<skill-name>`; if `false`, triggers automatically based on context

**Active skills:**
- `gitignore-init` — automatic; runs on first repo exploration; creates `.gitignore` if absent, then delegates to `gitignore-checker`
- `gitignore-checker` — automatic; runs whenever a `.gitignore` is read/created/edited; ensures `.DS_Store` and `.env` entries are present
- `meetgeek-to-md` — user-invocable; converts MeetGeek DOCX transcript exports to clean markdown

## Adding a new skill

1. Create `.claude/skills/<your-skill-name>/SKILL.md`
2. Add frontmatter (`name`, `description`, `user-invocable`) and instructions
3. Claude Code picks it up automatically — no registration needed

## Privacy rules

This is a public repo. All files must be free of PII and absolute paths.

- No real names, email addresses, employer names, client names, or other identifying information
- No absolute paths — use relative paths or placeholders
- Before staging any file, check it against these rules
- If a file contains PII or an absolute path, **flag it immediately and do not commit it**
- Before committing, verify `git config user.name` is `pithy-name` and `git config user.email` is `pithy.name@fastmail.com`; if not, stop and flag it
