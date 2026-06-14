# privacy-check — Design Spec (draft)

**Date:** 2026-06-06
**Status:** Draft — for review
**Type:** Claude Code skill (user-invocable) + optional pre-push/pre-commit hook
**Motivation:** This is a public repo with a hard no-PII / no-absolute-paths rule. The PII scans run during the breakdown-to-decide work were ad-hoc one-off `grep` commands — effective but inconsistent, **diff-scoped (not whole-repo)**, and one of them silently false-cleaned on a shell quoting bug. A dedicated skill makes the check repeatable, complete, and hard to get wrong.

---

## Purpose

Scan the repository for content that must not be published — real-identity PII, absolute paths containing a username, stray emails, and secrets — and report every hit as `file:line`, before anything is committed or pushed. Refuse to green-light a commit/push when real PII is found.

---

## Hard requirements (lessons baked in)

1. **Case-insensitive.** All identity/keyword matching is case-insensitive (`grep -i`) — a name token must match regardless of case (e.g. `Lastname` / `lastname` / `LASTNAME`). (The ad-hoc scans used `-i`; the skill must make it non-optional.)
2. **Scope is explicit and defaults to the WHOLE repo.** The ad-hoc scans only checked the *branch diff / staged files* — they would **miss pre-existing PII elsewhere in the repo**. The skill must support and clearly label these scopes, defaulting to whole-tracked-tree:
   - `tracked` (default) — all git-tracked files (`git ls-files`), the true "is the published repo clean" check.
   - `staged` — `git diff --cached --name-only`, the pre-commit gate.
   - `branch` — `git diff --name-only origin/main...HEAD`, the pre-push/PR gate.
   - Always print which scope ran, and warn that non-`tracked` scopes can miss PII outside the change.
3. **Never conflate command failure with "clean."** The ad-hoc scan once printed "clean" because `grep` errored on a bad argument and an `|| echo clean` fallback fired. The skill must check exit status explicitly (grep exit 1 = clean, 2 = error → fail loud) and never treat an error as a pass.
4. **Safe file-list handling.** Pass file lists as NUL-delimited args (`git ls-files -z | xargs -0`), not a quoted blob — and note the zsh gotcha that unquoted `$var` does not word-split. A scoping bug must not silently shrink the scan.
5. **Allowlist the approved public identity.** `pithy-name` and `pithy.name@fastmail.com` are the intentional public committer identity and must NOT be flagged. Everything else identity-shaped is a hit.

---

## What it scans for

Derived from the commands actually run this session:

- **Real-identity markers** — the developer's real first/last name and known handles/aliases. **Do NOT hardcode these tokens in this public doc** (that would leak the very thing we're protecting); keep the actual list in a **git-ignored** config (e.g. `privacy-check.local`) or in private memory, and load it at scan time. Use `grep -niwE` (word-boundary) for short/ambiguous tokens to avoid substring false-positives.
- **Absolute paths with a username:** `/Users/<name>/…`, `/home/<name>/…` — these leak identity even without a name string.
- **Emails:** a generic address regex (`[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}`) plus explicit `fastmail` / `gmail`, minus the allowlisted pseudonym.
- **Secrets:** `ghp_`, `sk-`, `xox[baprs]`, `-----BEGIN … PRIVATE KEY-----`, `AKIA[0-9A-Z]{16}`, `api[_-]?key`, `secret[_-]?key`, `password=`, `bearer ` (case-insensitive).
- **Other identifying info** (from project rules): employer/client names — keep a small configurable denylist.

Patterns live in one place (a config block / array) so they're maintained once, not copy-pasted per invocation.

---

## Behavior

1. Resolve scope (default `tracked`); list the files; print the scope + file count.
2. Run each pattern group; collect `file:line: match` hits. Check exit codes; a grep error aborts with a loud failure (never "clean").
3. Apply the allowlist (drop approved-pseudonym lines).
4. **Report:** if hits remain → list them grouped by category and **fail** (exit non-zero / tell the user "do NOT commit/push"). If none → state "clean" *and* which scope proved it.
5. As a hook (optional): wire as a pre-push (or `PreToolUse` on `git push`/`git commit`) gate that blocks on real hits.

---

## Open questions (for the builder)

- Implement as a deterministic shell/python script the skill calls (preferred — fast, reliable, scriptable in a hook) vs. model-driven scanning. Lean script.
- Whole-repo also covers git **history**? Out of MVP — history rewrite is a separate, heavier concern (see the existing memory: GitHub retains diffs at compare URLs even after force-push). Note it; don't build it.
- Where the denylist/allowlist config lives (a `privacy-check.config` in the skill, or read from project settings).

---

## Non-goals

- Scrubbing git history (separate, dangerous).
- Network calls / external scanners — keep it local (privacy-by-default).
