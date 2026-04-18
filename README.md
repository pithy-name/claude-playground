# claude-playground

A personal sandbox for exploring Claude Code and keeping technical skills sharp.

## What's here

Experiments with Claude Code features.

## How skills work

Skills live in `.claude/skills/<skill-name>/SKILL.md`. Each file contains a frontmatter header (name, description, trigger behavior) and instructions Claude follows when the skill is invoked. Skills can be user-invocable (called with `/skill-name`) or automatic (triggered by context).

## Skills in this repo

| Skill | Description |
|-------|-------------|
| `gitignore-init` | Automatic. When first exploring a repo, checks if a `.gitignore` exists and creates one if not. |
| `gitignore-checker` | Automatic. Whenever a `.gitignore` is read, created, or edited, ensures `.DS_Store` and `.env` are present. |
| `session-journal` | Automatic. Creates and maintains a per-session journal entry in `.claude/journals/`, documenting goals, milestones, decisions, and outcomes. Fires at session start, at meaningful milestones, and at session end. |

## Adding a new skill

1. Create a folder under `.claude/skills/<your-skill-name>/`
2. Add a `SKILL.md` with frontmatter and instructions
3. Claude Code will pick it up automatically
