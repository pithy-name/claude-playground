# session-journal

**Maturity:** 🧪 Experimental — not actively maintained | **Type:** Automatic

Creates and maintains a structured journal entry per session in `.claude/journals/`. Fires automatically at session start, meaningful milestones, and session end — no user action required.

> **Note:** This workflow has been **superseded** by a Session Log-based approach. Published here as a record of the iteration, not as a recommendation.

## What it produces

One `.md` file per session under `.claude/journals/`, named `YYYY-MM-DD_HH-MM_<slug>.md`. Each file captures:

- Session goal
- Timeline of milestones with deliverables, prompts, Q&A, and feedback
- Closing summary with completed work, next steps, and files changed
