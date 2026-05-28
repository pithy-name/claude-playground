# claude-playground

A personal sandbox for building with [Claude Code](https://claude.ai/code).

## Skills

| Skill | Invocation | Maturity | Description |
|-------|------------|----------|-------------|
| [`gitignore-init`](.claude/skills/gitignore-init/) | Automatic | v0.1 | Creates a `.gitignore` if none exists when first exploring a repo. |
| [`gitignore-checker`](.claude/skills/gitignore-checker/) | Automatic | v0.1 | Ensures `.DS_Store` and `.env` are in every `.gitignore`, silently. |
| [`meetgeek-to-md`](.claude/skills/meetgeek-to-md/) | `/meetgeek-to-md <path>` | v0.1 | Converts a MeetGeek DOCX transcript to clean markdown with corrected speaker attribution and Key Takeaways. |
| [`session-report`](.claude/skills/session-report/) | `/session-report` | 🧪 experimental | Project-scoped override of the `session-report` plugin — redirects output to a configurable directory. Playground experiment. |
