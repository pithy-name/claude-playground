# session-log-skill-bundle

Self-contained, portable bundle to **build the `session-log` skill in `claude-playground`**. Move this whole directory into that repo, then start a fresh Claude Code session with `BUILD-PROMPT.md`.

## Contents

| File | What it is |
|------|------------|
| `BUILD-PROMPT.md` | The prompt to drop into a fresh session in `claude-playground`. Start here. |
| `session-log-skill-spec.md` | **Canonical build input** — format spec + validated-pattern library. Build skill content from this alone. |
| `session-log-prd.md` | Strategy / naming / architecture / hooks / scope / deferred items. Read for the *why* and *how to build*; not for format detail. |

All three are PII-safe and path-agnostic — safe for a public repo. If spec and PRD ever disagree on format, the **spec wins**.

## Not included (and why)

- **`scratchpad-management-skill.DEPRECATED.md`** — frozen historical source in the origin repo. Carries `/Users/<name>/` absolute paths; explicitly *not* a build input. Left behind by design.
- **The design session log** (`2026-05-28-session-log-skill-prd-spec.md`) — design-history record, not needed to build. Stays in the origin repo.

## Origin-repo cleanup (handled separately, not part of this build)

Once the skill ships in `claude-playground`: remove the origin repo's CLAUDE.md "Session Management" section (the skill replaces it) and archive/freeze the spec there so it can't drift into a competing copy. Tracked in the origin repo's `plans/TODO.md`.
