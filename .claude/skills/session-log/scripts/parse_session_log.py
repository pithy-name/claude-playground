#!/usr/bin/env python3
"""Deterministic parser for Session Log markdown files.

This is the reference implementation of the hard acceptance criterion: a
conforming Session Log must be extractable WITHOUT an LLM. The parser pulls the
Goal, every required section's body, every timestamped Update block (in
chronological order), and the To-do items, using only regex over the Markdown.

Usage:
    python3 parse_session_log.py <path-to-session-log.md>
    python3 parse_session_log.py --self-test

Exit codes:
    0  the log conforms (all required fields extracted with zero manual fixup)
    1  a required field failed to parse (the log is non-conforming)
    2  file/argument error
"""

import argparse
import json
import re
import sys

# The fixed, exact enum of required section headings, in order. The parser — and
# therefore the format — depends on these being present and spelled exactly.
REQUIRED_SECTIONS = [
    "What happened",
    "Decisions & trade-offs",
    "Mistakes & corrections",
    "What worked & what to repeat",
    "Learnings about the user",
    "Where to pick up",
    "To-do",
]

# Title line: "# Session: <topic> — <YYYY-MM-DD>"  (em dash separator)
TITLE_RE = re.compile(r"^#\s+Session:\s+(?P<topic>.+?)\s+—\s+(?P<date>\d{4}-\d{2}-\d{2})\s*$")
# Goal line: "**Goal:** <one line>"
GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(?P<goal>.+?)\s*$")
# Any level-2 heading.
H2_RE = re.compile(r"^##\s+(?P<heading>.+?)\s*$")
# The one canonical Update-block timestamp format: YYYY-MM-DDTHH:MM TZ (24h, tz label).
UPDATE_RE = re.compile(r"^Update\s+(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}\s+[A-Z]{2,5})$")
# A naive sort key from the timestamp (tz label dropped — labels aren't offsets).
TS_SORTKEY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})")


class ParseError(Exception):
    pass


def parse(text):
    """Parse Session Log text into a structured dict. Raise ParseError if a
    required field is missing or malformed."""
    lines = text.splitlines()

    # --- Title + date ---
    title = None
    title_idx = None
    for i, line in enumerate(lines):
        m = TITLE_RE.match(line)
        if m:
            title = {"topic": m.group("topic"), "date": m.group("date")}
            title_idx = i
            break
    if title is None:
        raise ParseError("missing or malformed title line "
                         "(expected `# Session: <topic> — YYYY-MM-DD`)")

    # --- Goal (must appear before the first H2) ---
    goal = None
    for line in lines[title_idx + 1:]:
        if H2_RE.match(line):
            break
        m = GOAL_RE.match(line)
        if m:
            goal = m.group("goal")
            break
    if goal is None:
        raise ParseError("missing Goal line (expected `**Goal:** ...` under the title)")

    # --- Walk H2 headings, collecting section bodies and Update blocks ---
    sections = {}          # heading -> body text
    updates = []           # list of {"timestamp", "body"} in document order
    order = []             # document order of non-Update section headings
    current = None         # ("section", heading) | ("update", ts) | None
    buf = []

    def flush():
        if current is None:
            return
        body = "\n".join(buf).strip()
        kind, key = current
        if kind == "section":
            sections[key] = body
            order.append(key)
        else:
            updates.append({"timestamp": key, "body": body})

    for line in lines[title_idx + 1:]:
        m = H2_RE.match(line)
        if m:
            flush()
            buf = []
            heading = m.group("heading")
            um = UPDATE_RE.match(heading)
            if um:
                current = ("update", um.group("ts"))
            elif re.match(r"^Update\b", heading):
                # Looks like an Update block but the timestamp is malformed — the
                # exact failure (guessed/wrong-format time) the skill prevents.
                raise ParseError(
                    f"malformed Update heading: `## {heading}` "
                    "(expected `## Update YYYY-MM-DDTHH:MM TZ`, 24h + tz label)")
            else:
                current = ("section", heading)
        else:
            if current is not None:
                buf.append(line)
    flush()

    # --- Validate required sections present ---
    missing = [s for s in REQUIRED_SECTIONS if s not in sections]
    if missing:
        raise ParseError("missing required section(s): " + ", ".join(missing))

    # --- Required-section order check (ignoring Update blocks) ---
    present_required = [h for h in order if h in REQUIRED_SECTIONS]
    if present_required != REQUIRED_SECTIONS:
        raise ParseError("required sections out of order.\n"
                         f"  expected: {REQUIRED_SECTIONS}\n"
                         f"  found:    {present_required}")

    # --- Update blocks must be chronological (ascending naive timestamp) ---
    def sortkey(ts):
        mm = TS_SORTKEY_RE.match(ts)
        return mm.group(1) if mm else ts
    ts_list = [u["timestamp"] for u in updates]
    if ts_list != sorted(ts_list, key=sortkey):
        raise ParseError("Update blocks are not in chronological order: " + ", ".join(ts_list))

    # --- To-do items ---
    todo_open, todo_done = [], []
    for line in sections["To-do"].splitlines():
        s = line.strip()
        if re.match(r"^- \[ \]\s+", s):
            todo_open.append(re.sub(r"^- \[ \]\s+", "", s))
        elif re.match(r"^- \[[xX]\]\s+", s) or re.match(r"^- ~~.*~~", s):
            todo_done.append(re.sub(r"^- (\[[xX]\]\s+)?", "", s))

    return {
        "title": title,
        "goal": goal,
        "sections": {s: sections[s] for s in REQUIRED_SECTIONS},
        "updates": updates,
        "todo": {"open": todo_open, "done": todo_done},
    }


def parse_file(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return parse(fh.read())
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


# The reference example, kept in sync with references/format-spec.md. Used by
# --self-test so the parser ships with its own acceptance test.
REFERENCE_EXAMPLE = """# Session: script-folders — 2026-05-18

**Goal:** Reorganize tool scripts into self-contained per-tool folders.

## What happened
- Reorganized tool scripts into per-tool folders; added READMEs.

## Decisions & trade-offs
**Folder granularity:** one folder per tool vs one shared utils/. Chose per-tool — keeps each tool self-contained and independently runnable.

## Mistakes & corrections
**Symptom:** Moved a script before updating its relative import.
**Root cause:** Edited path in one place, not the caller.
**Correct approach:** grep for references before moving a file.

## What worked & what to repeat
**Grep-before-move, once adopted:** after the first slip, grepping for references ahead of each move caught two more stale imports. Why it worked: surfaced callers the editor didn't show. Repeat for every file move.

## Learnings about the user
Wants verification before "done" — asked "did you actually run it?" after a claim. Run it, then report.

## Where to pick up
Next: add tests for `find_files.py`. Reference: `tools/find-files/README.md`.

## Update 2026-05-18T14:02 PT
- Set up the find-files tool; completed "split utils" (struck in To-do below).

## To-do
- ~~Split shared utils into per-tool folders~~ done
- [ ] Add tests for find_files.py
"""


def self_test():
    result = parse(REFERENCE_EXAMPLE)
    assert result["title"]["topic"] == "script-folders", result["title"]
    assert result["title"]["date"] == "2026-05-18", result["title"]
    assert result["goal"].startswith("Reorganize tool scripts"), result["goal"]
    for s in REQUIRED_SECTIONS:
        assert result["sections"][s].strip(), f"empty required section: {s}"
    assert len(result["updates"]) == 1, result["updates"]
    assert result["updates"][0]["timestamp"] == "2026-05-18T14:02 PT"
    assert result["todo"]["open"] == ["Add tests for find_files.py"], result["todo"]
    assert len(result["todo"]["done"]) == 1, result["todo"]
    print("self-test PASSED — every required field extracted with zero manual fixup")


def main():
    ap = argparse.ArgumentParser(description="Parse / validate a Session Log markdown file.")
    ap.add_argument("path", nargs="?", help="path to a Session Log .md file")
    ap.add_argument("--self-test", action="store_true",
                    help="parse the bundled reference example and assert all fields extract")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if not args.path:
        ap.error("provide a path to a Session Log, or --self-test")

    try:
        result = parse_file(args.path)
    except ParseError as e:
        print(f"NON-CONFORMING: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nCONFORMING: extracted goal + {len(result['sections'])} required sections "
          f"+ {len(result['updates'])} update block(s) + "
          f"{len(result['todo']['open'])} open / {len(result['todo']['done'])} done to-dos",
          file=sys.stderr)


if __name__ == "__main__":
    main()
