---
name: breakdown-to-decide
description: Walk the user through a set of decisions one at a time — each as a structured choice (issue, why it matters, options with implications and trade-offs, a recommendation) captured via the AskUserQuestion tool. Use this whenever the user faces multiple decisions/findings/issues to resolve and would benefit from deciding on them one by one instead of all at once — e.g. after a code review, audit, or analysis produces several findings, or when the user says "walk me through these one by one", "go through these and let me decide on each", "break it down for me", "help me understand my options", "I don't know where to start", or "how do I choose". Prefer this even when the user doesn't name it explicitly but is clearly facing a pile of choices.
user-invocable: true
---

# breakdown-to-decide

Turn a pile of decisions into a calm, one-at-a-time walk. For each decision you present a short structured writeup and then capture the user's choice with `AskUserQuestion`. This replaces the ad-hoc pattern of dumping a wall of findings and asking the user to react to all of them at once — which is exactly when people freeze or rubber-stamp.

The decision contract below is this skill's own, self-contained definition — follow it as written. (The skill's `README.md`, which travels in this directory, mirrors it for human readers.)

## What counts as a "decision"

A **decision** is a user-facing choice among options to resolve a problem / finding / issue / question. Pure clarifiers — questions with no meaningful options or trade-offs ("which file did you mean?") — are *not* decisions and don't need the full treatment. Use judgment: if there's a real trade-off worth weighing, it's a decision.

## The decision contract

Present every decision this way. The structure isn't bureaucracy — it's what lets the user actually weigh the choice instead of guessing.

**The prose writeup (before the widget):**
- **Issue** — what was raised.
- **Why it matters** — the impact or risk if left unaddressed. A decision without stakes is just trivia; the "why" is what makes it worth a moment of the user's attention.

**The options (in the `AskUserQuestion` widget):**
- 2–4 options. Each option's `description` must carry:
  - **Implication** — what choosing *this* option causes (its direct consequence).
  - **Trade-offs** — what you gain vs. give up *relative to the other options*. (Implication is about this option alone; trade-offs are comparative — keep them distinct or they collapse into mush.)
- Mark the recommended path and say **why**. The user is asking you to think, not just list — an unranked menu pushes the work back onto them.

**Single-select (default):**
- Put the recommended option **first**, label suffixed with `(Recommended)`, and put the **Why** in its description.

**Multi-select** (set `multiSelect: true` when the decision genuinely allows several compatible picks, e.g. "apply the fix AND add a test"):
- "Recommended-first" no longer applies. Mark each recommended option `(Recommended)` (a recommended *set*), each carrying its own **Why**.

You don't need to spend option slots on "skip" or "let's discuss" — `AskUserQuestion` always gives the user a free-text "Other" field and a way to dismiss the card and reply in chat. Lean on those.

**Keep it tight, keep your voice.** Each segment is a sentence or two, not an essay — a decision the user can read in 20 seconds beats a thorough one they skim. And the contract is a skeleton, not a straitjacket: write in your natural voice (a little personality helps). Completeness and clarity are the goal, not robotic uniformity.

## Running the walk

1. **Gather the decision set — completely.** Prefer decisions already present in the conversation (a review/audit/analysis you just produced — the common case). If none are evident, ask the user to supply them. **Never fabricate decisions** to fill a list.
   - **When *you* identify the decisions** (the user hands you a goal, not a list — "help me pick a stack"), decompose the *whole* problem, not a convenient subset. Surface the **foundational decision that constrains the rest first** ("monolith vs. SPA" before "which framework"), then the ones that depend on it. **Under-decomposing is the main failure mode** — if you drop the pivotal decision or stop early, the user thinks they're done when they aren't. Fewer, deeper decisions is *not* the goal; completeness is.

2. **List the full set, then confirm.** Before walking, state the complete set you're about to cover (count + one-line titles) so the user sees the whole map and can catch anything missing. If it's ambiguous which set they mean (the chat holds several analyses), confirm which before starting.

3. **Group independent decisions into one question card.** `AskUserQuestion` takes **up to 4 questions per call** and gives the user native prev/next navigation across them plus a single summary Submit — that *is* the "one at a time" experience, and it's better than firing a separate card per decision. So:
   - **Default — batch.** For independent decisions (the common case — they don't depend on each other), print the short prose writeups (Issue + Why) for the group, then fire **one** `AskUserQuestion` carrying them as contract-shaped questions (chunks of ≤4). The user walks them with the widget's own navigation and submits once; the summary Submit recaps their picks.
   - **Go sequential (separate calls, one decision each) only when** a later decision genuinely depends on the user's answer to an earlier one. Then fire, wait, adapt, fire the next.
   - **More than 4 decisions:** chunk into successive batches of ≤4.
   - **Don't label separate calls "Decision N of M."** That promises in-widget pagination that separate calls don't have (the user can't arrow across them, and each card's Submit looks like a phantom extra decision). Within a single batched call the widget numbers the questions for you.
   - The point isn't one *tool call* per decision — it's that each decision is a distinct, fully-formed choice the user weighs on its own, never a blended wall.

4. **Recap at the end.** Print a simple table of each decision and the choice made. That's the deliverable — see Boundaries.

## Presenting each decision — example

````
### Decision 2 of 6 — Token expiry check is off-by-one

**Issue** — `verifyToken()` uses `<` instead of `<=`, so a token expiring exactly now is accepted.
**Why it matters** — A one-second window of accepting expired tokens; small, but it's an auth correctness bug and trivial to fix.

**Options** (in the question below)
````

Then call `AskUserQuestion` with options whose descriptions follow the contract, e.g.:
- Option A — label `Fix to <= (Recommended)` — *Implication:* expired-now tokens are rejected. *Trade-offs:* correct and one line; negligible risk. *Why:* it's the actual bug and cheap to fix.
- Option B — label `Leave as-is` — *Implication:* the one-second window persists. *Trade-offs:* zero effort now; carries a known auth bug.
- Option C — label `Fix + add a regression test` — *Implication:* fixes it and guards against recurrence. *Trade-offs:* a bit more work; best durability.

For a set of independent decisions, pass several such questions in a **single** `AskUserQuestion` call (≤4) rather than one call each — the user then navigates the whole set in one widget and submits once. Print each decision's Issue + Why writeup first, then fire the one batched call.

## Boundaries

Deliver only the in-chat walk + end recap. Do **not** persist decisions to a file, route deferrals to a backlog, or act on the choices (apply fixes) — out of scope. If the user wants to act on a choice, that's a separate, explicitly-confirmed step.
