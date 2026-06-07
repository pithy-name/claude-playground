# session-log — evals

Test suite for the `session-log` skill. Prompts + assertions live in `evals.json`.

## The four evals

| id | name | what it exercises |
|----|------|-------------------|
| 1 | create-log | creating a conforming log from scratch |
| 2 | incremental-update | adding a decision + a mistake to an in-progress log |
| 3 | close-audit | the close-out (strike done todos, final Update, populate Learnings) |
| 4 | accumulation-extraction | a **non-enumerated** update to a content-rich log — does the skill extract *implicit* learnings into the right Learnings subsections? |

## How to run

Not a one-command harness. Per iteration: spawn one subagent **with the skill** and one **baseline** (no skill) per eval, save each output, then grade with a workspace script (parser + assertion checks), aggregate with skill-creator's `aggregate_benchmark`, and view with `eval-viewer/generate_review.py --static`. Workspaces go in a scratch dir (e.g. `/tmp/sl-evals/iteration-N/`), not in the repo.

## Results so far

- **iteration-1 (v1 format):** with-skill 1.00 / baseline 0.20 — lift +0.80.
- **iteration-2 (v2 format):** with-skill 1.00 / baseline 0.70 — lift +0.30.
- **iteration-3 (v2, sharpened eval-4):** with-skill 1.00 / baseline 0.70 — lift +0.30.

The clearest, durable signal is **eval-1 (create-from-scratch): 1.00 vs 0.00.** Unaided, Claude invents a non-conforming format (wrong filename, old headings, no Started/Session-ID). For *updating an already-conforming log*, the baseline scores high because the existing log scaffolds the format by example — so the skill's marginal lift there is small, which is expected, not a defect.

## ⚠️ Known limitation — the harness can't reproduce the real-world "Learnings-skip"

In real use, Claude often **fails to add Learnings** unless told "go top to bottom and update every section." The motivation for eval-4 was to catch that. **It doesn't** — both with-skill and baseline populate Learnings in the eval. Two reasons:

1. **Seeds scaffold the baseline.** A content-rich seed with already-populated Learnings teaches even the no-skill agent to add parallel entries by example.
2. **Single-shot ≠ the real condition.** The skip is a **competing-priority** phenomenon, not a session-length one: in real work the log is a *side-chore* during a primary task, so the reflective Learnings extraction gets dropped. In the eval, *updating the log is the agent's sole task* — full attention → no skip. (Confirmed against a long session that was <50% context, so it's not context-load.)

**What would isolate it (not yet run) — "Design B":** give the agent a *primary* task (e.g. fix a failing function) where a wrong-then-right attempt naturally produces a mistake + a win, plus a standing "keep a session log per the skill," and check whether Learnings gets populated **without** anyone saying "update the log." Higher variance (depends on the agent actually erring) — likely needs 2–3 runs.

**Mitigation in lieu of an eval:** the skill's **update-discipline** section ("walk every section; don't skip Learnings") + the **close-audit gate** ("Learnings populated") + real-session dogfooding. Don't read eval-4's green as proof the skip is fixed — it isn't tested.
