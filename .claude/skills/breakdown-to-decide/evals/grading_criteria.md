# breakdown-to-decide — grading criteria (iteration-2, rev 2)

> **Status:** proposed; awaiting user sign-off before iteration-2 grading runs.

**Why rev 2.** An adversarial review of rev 1 found it would re-ship the iteration-1 blind spot: its "completeness" check (S1) was unmeasurable because the judge was never told what the *complete* decision set is — so it could not see a missing decision, which is exactly the eval-2 regression (skill surfaced 5 decisions and folded "app architecture"; the baseline surfaced 7 with app-architecture as the pivotal first decision — the baseline *beat* the skill). Rev 2 fixes three things: reference decision sets, paired judging with a calibration gate, and no single aggregate score.

---

## Reference decision sets (the ground truth S1 needs)

For each eval, the canonical decisions a good walk should surface. The **pivotal** decision (the one that constrains the rest and should stand alone, ideally first) is flagged. Coverage is **merge-tolerant**: consciously combining two decisions *with a stated rationale* is fine; an *unconscious* fold that buries the pivotal decision is not.

- **eval-1 (code findings) — closed set of 5** (from the prompt; independent, no pivotal):
  off-by-one token expiry; JWT secret unvalidated; bcrypt cost 8; no login rate-limiting; cookie missing SameSite.
- **eval-2 (pick a stack) — OPEN; reference set:**
  **app-architecture (monolith vs SPA+API) — PIVOTAL, must be standalone**; backend framework; frontend approach; database; auth; hosting; styling (*optional*). This is the only eval where the skill must derive the set itself, so the reference set matters most here.
- **eval-3 (auth hardening) — closed set of 3:** rate-limiting approach; *which optional protections* (multi-select); bcrypt cost factor.
- **eval-4 (under-specified PR review) — closed set of 5** (the prompt lists them, casually): dup logic across users.py/orgs.py; `process()` 120 lines; no serializer tests; `86400` hardcoded ×3; error-handling swallows exceptions. *Ordering note:* "error swallowing" is the natural first (it masks the others) — graded as ordering (S3b), not a hard bar.
- **eval-5 (design-spec review) — closed set of 6** (from the prompt).

> Keep reference sets **minimal** — hard-bar only the pivotal decision; treat the rest as expected-but-merge-tolerant coverage. Otherwise the grader just encodes one person's opinion of "the right decisions" as truth (a bias swap).

---

## Layer 1 — Objective checks (`objective_checks.py`, deterministic)

- **O1 — Fabrication/omission guard.** For the closed-set evals, the walk covers the given items and invents none: count matches (eval-1: 5, eval-3: 3, eval-4: 5, eval-5: 6) **and** each given finding maps to a decision (keyword identity check — catches "hit the count but dropped one and invented another"). eval-2 is open → no count; completeness handled in S1.
- **O2 — Multi-select discrimination (eval-3 only).** A multi-select question appears for decision 2; the others are single-select.

## Layer 2 — Semantic checks (LLM judge)

**Primary (discriminating — this is where the skill must earn its keep):**

- **S1a — Pivotal present & standalone** *(single-output, anchored to the reference set)*. Is the pivotal decision surfaced as its own decision, not folded into another? Quote where. (Near-deterministic; would have failed the eval-2 with-skill run.)
- **S1b — Coverage** *(paired, see method)*. Which reference decisions are present / missing / merged? Report as a **fraction + the named missing/folded decisions**, not a boolean. Justified merges count as covered.
- **S3a — Sequenced.** Decisions are distinct units the user can decide one at a time, not one blended essay.
- **S3b — Dependency ordering.** Are decisions ordered so the foundational ones come before what depends on them? (The skill explicitly claims this.)
- **S6 — Recommendation defensibility** *(absolute bar)*. Is each `(Recommended)` pick justified by the stated trade-offs and the user's constraints (e.g. eval-2's "solo, strong Python, weak JS")? Grades whether the advice is *good*, not just present.

**Hygiene gates (must-pass, NOT part of the comparative score — both skill and baseline pass these, so they carry no signal):**

- **S2 — Contract content.** Each decision conveys issue, why, ≥2 real (non-strawman) options, each with implication AND trade-offs, and a recommendation.
- **S4 — No bulk-acting.** Framed as the user's decisions; doesn't go apply fixes.
- **S5 — Recap** at the end.

---

## Judging method

- **Paired + position-randomized** for S1b and S3 (completeness and ordering are only visible in contrast — that's how the human caught eval-2). Give the judge both outputs as A/B with order randomized per run; ask which decomposes more completely / orders better, and **name what the weaker one misses**.
- **Single-output, reference-anchored** for S1a, S2, S6 (these have a right answer independent of the comparator).
- **Multi-run** (2–3×, or 2 distinct judge prompts) on S1/S3; if judges disagree, flag for human review rather than averaging it away.
- **Calibration gate (regression test for the grader itself):** before trusting any judge config, run it on the labeled pair — eval-2 baseline (7, app-arch standalone) = good vs eval-2 with-skill (5, app-arch folded) = bad. If it does **not** rank the good one higher on completeness, the config is **disqualified**. This is the check iteration-1 never had.

## Reporting

- **No single pass-rate.** Report a **per-criterion vector**. The headline is S1 (coverage fraction + named gaps), S3b (ordering), and S6 — reported separately. S2/S4/S5 reported as hygiene pass/fail only.
- **"Skill < baseline" is a first-class outcome** — the grader must be able to say the skill lost (it did on eval-2). Don't assume skill ≥ baseline.
- Always surface `missing/folded decisions: [...]` so a regression is unhideable by construction.

## Honest expectation

This is not a "skill blows out baseline" story. Baselines write good content (S2) and don't bulk-act (S4) — they pass the hygiene gates. The skill's defensible, measurable wins are **completeness discipline (S1), dependency ordering (S3b), one-at-a-time capture (S3a), and consistency**. If iteration-2 still shows the skill losing to the baseline on S1 for any case, that's a real finding to fix in the skill — not a number to average away.
