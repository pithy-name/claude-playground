---
name: session-journal
description: This skill should be used at the start of every session, at meaningful milestones during the session, and at the end of every session. Creates and maintains a journal entry file per session documenting goals, progress, decisions, and outcomes.
user-invocable: false
---

# Session Journal

Create and maintain a journal entry for every session in `.claude/journals/`. One file per session.

## File Naming

`.claude/journals/YYYY-MM-DD_HH-MM_<slug>.md`

Use local time in 24-hour clock format. `<slug>` is a 2-4 word kebab-case summary of the session goal (e.g. `setup-gitignore-skill`).

## When to Write

| Trigger | What to write |
|--------|---------------|
| Session start | Create the file with header, goal, and repo context |
| Milestone reached | Append a milestone block with deliverables and subheadings |
| Session end | Append the closing summary block |

## What Counts as a Milestone

A milestone represents something completed or delivered — a skill created, a format finalized, a bug fixed. Research, exploration, and prep work are not milestones on their own; they belong under the milestone they contributed to as `#### Research/Work`.

## Journal File Format

```markdown
# Session Journal — YYYY-MM-DD HH:MM

**Repo:** owner/repo (last two path segments of the working directory — never the full absolute path)
**Started:** YYYY-MM-DD HH:MM (local 24h)
**Ended:** YYYY-MM-DD HH:MM (fill in at close)

## Goal
What we set out to do this session.

---

## Timeline

### YYYY-MM-DD HH:MM — Milestone: <milestone title>
- Deliverable or outcome, including the implication of any decisions (e.g. "Set to `user-invocable: false` so it fires automatically")
- Additional deliverable bullets as needed

#### User Prompt
"first prompt text"
"second prompt text if there were multiple"

(include all prompts the user gave that relate to this milestone)

#### Q&A
**Claude:** question text (Claude asking the user for clarification — not the user asking Claude)
**User:** answer text

(include all Q&A exchanges that relate to this milestone)

#### Research/Work
- Steps taken, exploration done, or prep work that led to this milestone
- Add as many bullets as needed

#### User Feedback
"first piece of feedback"
"second piece of feedback if there were multiple"

(include all feedback or corrections the user gave during this milestone)

(repeat ### milestone block for each milestone)

---

## Closing Summary

**Completed:**
- bullet list of what was finished

**Left incomplete / next steps:**
- bullet list of outstanding work

**User preferences or feedback noted:**
- anything the user corrected, confirmed, or asked to remember

**Files changed this session:**
- list of files touched
```

## Instructions

1. At session start: create the file immediately with repo, start datetime, and goal.
2. Each ### milestone block represents a completed deliverable. Put the outcome bullets directly under the ### heading.
3. Under each milestone, add only the #### subheadings that apply — Research/Work, User Prompt, Q&A, User Feedback. Omit any that are not relevant.
4. Deliverable bullets must include the *implication* of decisions, not just the bare fact (e.g. "so it fires automatically", "so history stays with the repo").
5. Research/Work captures the steps, exploration, or prep that led to the milestone — it is a sibling to User Prompt and Q&A, not part of the deliverable bullets.
6. At session end: append the Closing Summary block and fill in the end datetime.
7. Never overwrite previous blocks — always append.
8. All timestamps must use local time in 24-hour clock format: `YYYY-MM-DD HH:MM`.
9. If the goal is unclear at session start, write "To be determined" and update it at the first milestone.
