# claude-playground

A personal sandbox for building with [Claude Code](https://claude.ai/code).

## Skills

**Ready to use:**

| Skill                                                | Invocation                    | Maturity   | Description                                                                                                                                                                                         |
| ---------------------------------------------------- | ----------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`session-log`](skills/session-log/)                 | Automatic                     | v1.0       | Per-session Session Log — what happened / decided / went wrong / learned — stored centrally outside any repo. Ships SessionStart + PreToolUse hooks (set up per its README) and a governance check. |
| [`breakdown-to-decide`](skills/breakdown-to-decide/) | `/breakdown-to-decide` + auto | v1.0       | Walks decisions one at a time — issue / why / options + trade-offs / recommendation — via `AskUserQuestion`. Ships a soft PreToolUse contract hook (set up per its README).                         |
| [`meetgeek-to-md`](skills/meetgeek-to-md/)           | `/meetgeek-to-md <path>`      | v0.1 (MVP) | Converts a MeetGeek DOCX transcript to clean markdown with corrected speaker attribution and Key Takeaways. Early — assumes MeetGeek's exact export format.                                         |

**Experimental — playground, not ready to rely on:**

| Skill | Invocation | Maturity | Description |
|-------|------------|----------|-------------|
| [`gitignore-init`](skills/gitignore-init/) | Automatic | 🧪 experimental | Creates a `.gitignore` if none exists when first exploring a repo. |
| [`gitignore-checker`](skills/gitignore-checker/) | Automatic | 🧪 experimental | Ensures `.DS_Store` and `.env` are in every `.gitignore`, silently. |
| [`session-report`](skills/session-report/) | `/session-report` | 🧪 experimental | Project-scoped override of the `session-report` plugin — redirects output to a configurable directory. |
| [`session-journal`](skills/session-journal/) | Automatic | 🧪 experimental — unmaintained | Per-session journal entry. Superseded by `session-log`. |

## Tools

| Tool | Description |
|------|-------------|
| [`claude-code-timeline`](tools/claude-code-timeline/) | Interactive timeline viewer for Claude Code session `.jsonl` transcripts. Download and open locally — no server needed. Source: simonw/tools (Apache-2.0). |
