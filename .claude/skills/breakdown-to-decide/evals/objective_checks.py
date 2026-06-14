#!/usr/bin/env python3
"""Objective (deterministic) eval checks for breakdown-to-decide — O1/O2 only.

Semantic criteria (S1-S6 in grading_criteria.md) are graded by an LLM judge,
not here. This script does only what text-matching can do reliably:
  O1 - fabrication/omission guard: count matches AND each given finding maps to
       a decision (closed-set evals only; eval-2 is open -> completeness via S1).
  O2 - multi-select discrimination (eval-3 only).

Usage: python3 objective_checks.py <walk.md> <eval_id>
Prints a JSON fragment: {"expectations": [...]}  (text/passed/evidence)
Python 3.9-safe (no PEP 604 unions) so it runs under system python.
"""
import json, re, sys

# Closed-set expected counts. eval-2 is OPEN (None) -> count not checked here.
EXPECTED_COUNT = {"1": 5, "2": None, "3": 3, "4": 5, "5": 6}
MULTISELECT_EVAL = "3"

# Decision-identity keywords: per closed-set eval, one keyword-group per given
# finding. A finding is "present" if ANY of its keywords appears (case-insensitive).
FINDING_KEYWORDS = {
    "1": [
        ["off-by-one", "<=", "expiry", "verifytoken"],
        ["jwt secret", "secret"],
        ["bcrypt", "cost factor"],
        ["rate limit", "rate-limit", "rate limiting"],
        ["samesite"],
    ],
    "3": [
        ["token bucket", "fixed window", "rate limit"],
        ["lockout", "mfa", "allowlist", "optional protection"],
        ["bcrypt", "cost factor"],
    ],
    "4": [
        ["duplicat", "users.py", "orgs.py"],
        ["process(", "120 line", "long function"],
        ["serializer"],
        ["86400", "magic number", "named constant"],
        ["swallow", "exception", "error handling"],
    ],
    "5": [
        ["defer", "backlog"],
        ["memory", "interrupt", "persist"],
        ["apply fix", "concrete action", "code-fixable", "non-code"],
        ["hardcoded", "absolute path"],
        ["confirm", "which set", "candidate set", "several"],
        ["four", "cap", ">4", "more than 4"],
    ],
}


def count_decisions(text):
    n = len(re.findall(r"Decision\s+\d+\s+of\s+\d+", text, re.I))
    if n:
        return n, "Decision N of M headers"
    n = len(re.findall(r"(?m)^#{1,4}\s*\d+[.)]", text))
    return n, "numbered section headings"


def has_multiselect(text):
    return bool(re.search(r"multi-?\s?select|check all that apply|any combination|choose any|pick (?:one or )?more", text, re.I))


def missing_findings(text, eval_id):
    low = text.lower()
    groups = FINDING_KEYWORDS.get(eval_id, [])
    missing = []
    for i, kws in enumerate(groups, 1):
        if not any(k in low for k in kws):
            missing.append(i)
    return missing, len(groups)


def main(path, eval_id):
    text = open(path, encoding="utf-8").read()
    n, how = count_decisions(text)
    exps = []
    exp = EXPECTED_COUNT.get(eval_id)

    if exp is not None:
        missing, total = missing_findings(text, eval_id)
        count_ok = (n == exp)
        identity_ok = (len(missing) == 0)
        exps.append({
            "text": "O1 - Covers exactly the {} given findings; none dropped or fabricated".format(exp),
            "passed": count_ok and identity_ok,
            "evidence": "count {} (expected {}) via {}; ".format(n, exp, how) +
                        ("all {} findings detected".format(total) if identity_ok
                         else "MISSING finding indices {} of {}".format(missing, total)),
        })
    else:
        exps.append({
            "text": "O1 - (open set) count is informational; completeness judged by S1 + reference set",
            "passed": True,
            "evidence": "found {} decisions via {}".format(n, how),
        })

    if eval_id == MULTISELECT_EVAL:
        ms = has_multiselect(text)
        exps.append({
            "text": "O2 - Uses a multi-select framing where genuinely warranted (decision 2)",
            "passed": ms,
            "evidence": "multi-select markers present" if ms else "no multi-select markers found",
        })

    print(json.dumps({"expectations": exps}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
