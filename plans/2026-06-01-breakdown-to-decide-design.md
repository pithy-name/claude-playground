# breakdown-to-decide — Design Spec

**Date:** 2026-06-01
**Status:** Draft — awaiting user review
**Type:** Claude Code skill (user-invocable)
**Location when built:** `.claude/skills/breakdown-to-decide/SKILL.md`

---

## Purpose

Walk a user through a set of findings one at a time. For each finding, present a structured writeup (issue, why it matters, options, trade-offs, recommendation), then capture the user's decision via the `AskUserQuestion` tool. Collect all decisions and act on them at the end.

Replaces the ad-hoc pattern of dumping a wall of findings and asking the user to respond to all at once.

---

## Invocation

- User-invocable skill, triggered with `/breakdown-to-decide`.
- Also triggers when the user asks to "walk through findings one by one", "go through these issues / decide on each", or similar.

---

## Input gathering

The skill resolves the findings list in fixed priority order:

1. **Prior conversation context** — if Claude has already produced findings this session (code review, audit, analysis), use them. This is the common case.
2. **User-supplied** — if none in context, parse what the user provided: pasted text, a file path, or a PR reference.
3. **Ask** — if neither is present, ask the user to supply findings. Never fabricate findings.

After resolving the source, the skill enumerates findings into an ordered list with a total count.

---

## Per-finding loop

Process findings strictly one at a time, in order. For each finding:

### Step 1 — Text writeup (markdown, printed to chat)

```
### Finding N of TOTAL — <short title>

**Issue** — what was raised.
**Why it's a problem** — impact / risk if unaddressed.
**Options**
- Option A — ...
- Option B — ...
**Trade-offs**
- Option A — pros / cons
- Option B — pros / cons
**Recommendation** — Claude's pick and the reasoning.
```

### Step 2 — Decision via AskUserQuestion

- Single-select question for this finding.
- Up to **4** option slots, all used for real resolution choices.
- The recommended choice is listed **first**, its label suffixed with `(Recommended)`.
- Skip / won't-fix / "let's discuss more" are NOT dedicated buttons. They are covered by:
  - the free **"Other"** text field (always present), and
  - the **dismiss-to-chat** escape (user dismisses the card and types a general reply; backed by the tool's `response` field).
- If a finding genuinely has more than 4 resolution options, the top 4 (by Claude's judgment) become buttons; the rest are described in the Step 1 writeup and remain reachable via "Other".

### Step 3 — Record

Record the chosen option against the finding. **No code changes or file edits happen mid-walk.**

---

## End summary

After the last finding, do all four of:

1. **Recap table** — print a markdown table: `Finding │ Decision`.
2. **Write decisions to file** — save the recap to `.claude/session-logs/` so the choices persist.
3. **Route deferrals** — any finding the user punted/deferred is appended to `TODO.md` at repo root.
4. **Offer to act** — offer to apply the chosen fixes (edits, etc.). Per the project ask-before-doing rule, get explicit go-ahead before making changes.

---

## Edge cases

| Case | Behavior |
|------|----------|
| 0 findings resolvable | Ask the user to supply findings; do not fabricate. |
| Large number of findings | Still strictly one-by-one; no batching. |
| Finding with >4 options | Top 4 become buttons; remainder in writeup text + "Other". |
| User dismisses to chat mid-walk | Handle the reply, then resume the loop where it left off. |

---

## Non-goals (YAGNI)

- No automatic fixing without confirmation.
- No persistence format beyond a plain markdown recap.
- No integration with external trackers beyond appending to `TODO.md`.
- No multi-select per finding (one decision per finding).

---

## Follow-up tasks (outside this skill)

- Update project `CLAUDE.md` "Active skills" list to include `breakdown-to-decide` once built.
