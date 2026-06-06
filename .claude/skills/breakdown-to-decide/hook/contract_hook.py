#!/usr/bin/env python3
"""breakdown-to-decide — PreToolUse hook for AskUserQuestion.

Enforces the decision contract on every AskUserQuestion call: each option's
description should carry an Implication and a Trade-offs segment, and the
recommended option(s) a Why. The CANONICAL contract lives in the skill's
SKILL.md / README.md / the design spec; this hook only encodes the segment
KEYS below — keep them in sync there, don't restate the contract prose here.

Architecture is built for expansion (see spec, "Build for expansion"):
the PARSER is separate from the DECISION LAYER, which is selected by a MODE.
  - MODE=soft  (default, MVP): never blocks. On gaps, returns additionalContext
    reminding the model of the contract so it self-applies on the next question.
  - MODE=strict (future): denies with an exact-template reason so the model
    fixes and retries; includes a per-session loop-breaker and a `quick:` bypass.

Set the mode via env var BTD_HOOK_MODE (default "soft").
Python 3.9-safe (no PEP 604 unions) so it runs under system python.

Registration (NOT done by this file — wire via the update-config skill):
  PreToolUse matcher "AskUserQuestion" ->
    command: "$CLAUDE_PROJECT_DIR/.claude/skills/breakdown-to-decide/hook/contract_hook.py"
"""
import json
import os
import re
import sys

# Single source of truth for the machine-checkable segment keys.
SEGMENTS = ["Implication", "Trade-offs", "Why"]
MAX_DENIALS = 3  # strict-mode loop-breaker: give up after this many in a row


def _has(text, key):
    # "Trade-offs" should also match "Tradeoffs"/"Trade offs"
    pat = key.replace("-", r"[-\s]?")
    return re.search(pat, text or "", re.I) is not None


def find_gaps(tool_input):
    """Return a list of human-readable contract gaps in the AskUserQuestion payload."""
    gaps = []
    questions = (tool_input or {}).get("questions") or []
    for qi, q in enumerate(questions, 1):
        opts = q.get("options") or []
        multi = bool(q.get("multiSelect"))
        label_q = q.get("header") or q.get("question") or "Q{}".format(qi)
        for oi, opt in enumerate(opts):
            desc = opt.get("description", "")
            if not _has(desc, "Implication"):
                gaps.append("Q{} '{}' option {}: missing an Implication".format(qi, label_q, oi + 1))
            if not _has(desc, "Trade-offs"):
                gaps.append("Q{} '{}' option {}: missing Trade-offs".format(qi, label_q, oi + 1))
        # recommendation
        if multi:
            rec = [o for o in opts if "(recommended)" in (o.get("label", "").lower())]
            if not rec:
                gaps.append("Q{} '{}': multi-select but no option marked (Recommended)".format(qi, label_q))
            elif not any(_has(o.get("description", ""), "Why") for o in rec):
                gaps.append("Q{} '{}': recommended option(s) missing a Why".format(qi, label_q))
        elif opts:
            if "(recommended)" not in opts[0].get("label", "").lower():
                gaps.append("Q{} '{}': first option is not marked (Recommended)".format(qi, label_q))
            elif not _has(opts[0].get("description", ""), "Why"):
                gaps.append("Q{} '{}': recommended option missing a Why".format(qi, label_q))
    return gaps


def _reminder(gaps):
    return (
        "breakdown-to-decide contract: every AskUserQuestion option needs an "
        "Implication and Trade-offs in its description, and the recommended "
        "option(s) a Why. Gaps this time:\n- " + "\n- ".join(gaps)
    )


def _emit(obj):
    if obj:
        print(json.dumps(obj))


def _allow_context(msg):
    _emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "additionalContext": msg,
    }})


# --- decision layers -------------------------------------------------------

def decide_soft(gaps, _data):
    if gaps:
        _allow_context(_reminder(gaps))  # never blocks; nudges the next question
    # no gaps -> exit silently (no output == default allow)


def _counter_path(session_id):
    tmp = os.environ.get("TMPDIR", "/tmp")
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "nosession")
    return os.path.join(tmp, "btd_hook_{}.count".format(safe))


def decide_strict(gaps, data):
    # bypass sentinel: header starting with "quick:" skips enforcement
    for q in (data.get("tool_input") or {}).get("questions") or []:
        if (q.get("header") or "").strip().lower().startswith("quick:"):
            return  # silent allow
    cpath = _counter_path(data.get("session_id", ""))
    if not gaps:
        try:
            os.remove(cpath)
        except OSError:
            pass
        return  # silent allow
    # gaps + loop-breaker
    n = 0
    try:
        with open(cpath) as f:
            n = int(f.read().strip() or "0")
    except (OSError, ValueError):
        n = 0
    if n >= MAX_DENIALS:
        _allow_context("Contract still unmet after {} retries; allowing to avoid a loop. {}"
                       .format(MAX_DENIALS, _reminder(gaps)))
        try:
            os.remove(cpath)
        except OSError:
            pass
        return
    try:
        with open(cpath, "w") as f:
            f.write(str(n + 1))
    except OSError:
        pass
    _emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Revise before asking. " + _reminder(gaps),
    }})


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return  # malformed input -> don't block anything
    if data.get("tool_name") != "AskUserQuestion":
        return
    gaps = find_gaps(data.get("tool_input"))
    mode = os.environ.get("BTD_HOOK_MODE", "soft").lower()
    (decide_strict if mode == "strict" else decide_soft)(gaps, data)


if __name__ == "__main__":
    main()
