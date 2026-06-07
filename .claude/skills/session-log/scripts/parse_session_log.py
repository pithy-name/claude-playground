#!/usr/bin/env python3
"""Deterministic parser for Session Log markdown files (v2 format).

Reference implementation of the hard acceptance criterion: a conforming Session Log
must be extractable WITHOUT an LLM. Pulls the topic, Started, Session ID, Goal, every
required H2 section, the three required H3 subsections under `## Learnings`, every
timestamped Update block (chronological), and the To-do items — using only regex.

Usage:
    python3 parse_session_log.py <path-to-session-log.md>
    python3 parse_session_log.py --self-test

Exit codes:
    0  conforming (all required fields extracted with zero manual fixup)
    1  a required field failed to parse (non-conforming)
    2  file/argument error
"""

import argparse
import json
import re
import sys

# Fixed, exact enums. The parser — and the format — depend on these spellings.
REQUIRED_H2 = [
    "What happened",
    "Decisions & trade-offs",
    "Learnings",
    "To-do",
]
# H3 subsections required under `## Learnings`, in order.
REQUIRED_H3 = [
    "Mistakes & corrections",
    "What worked & what to repeat",
    "User preferences & conventions",
]

TITLE_RE = re.compile(r"^#\s+Session Log\s+—\s+(?P<topic>.+?)\s*$")
STARTED_RE = re.compile(r"^\*\*Started:\*\*\s*(?P<started>.+?)\s*$")
SESSION_ID_RE = re.compile(r"^\*\*Session ID:\*\*\s*(?P<sid>.+?)\s*$")
GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(?P<goal>.+?)\s*$")
H2_RE = re.compile(r"^##\s+(?P<h>.+?)\s*$")
H3_RE = re.compile(r"^###\s+(?P<h>.+?)\s*$")
# One canonical Update-block timestamp: YYYY-MM-DDTHH:MM TZ (24h, tz label).
UPDATE_RE = re.compile(r"^Update\s+(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}\s+[A-Z]{2,5})$")
TS_SORTKEY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})")


class ParseError(Exception):
    pass


def parse(text):
    lines = text.splitlines()

    # --- Title (H1) ---
    title = None
    title_idx = None
    for i, line in enumerate(lines):
        m = TITLE_RE.match(line)
        if m:
            title = {"topic": m.group("topic")}
            title_idx = i
            break
    if title is None:
        raise ParseError("missing or malformed title (expected `# Session Log — <Topic>`)")

    # --- Metadata block (Started required; Session ID optional; Goal required) before first H2 ---
    started = session_id = goal = None
    for line in lines[title_idx + 1:]:
        if H2_RE.match(line):
            break
        if (m := STARTED_RE.match(line)):
            started = m.group("started")
        if (m := SESSION_ID_RE.match(line)):
            session_id = m.group("sid")
        if (m := GOAL_RE.match(line)):
            goal = m.group("goal")
    if started is None:
        raise ParseError("missing `**Started:**` line under the title")
    if goal is None:
        raise ParseError("missing `**Goal:**` line under the title")

    # --- Walk H2 / H3, collecting section bodies, Learnings subsections, and Update blocks ---
    sections = {}     # H2 heading -> body
    learnings = {}    # H3 heading (under Learnings) -> body
    updates = []      # {"timestamp", "body"} in document order
    h2_order = []     # H2 section headings (excludes Update blocks)
    h3_order = []     # H3 headings seen under the Learnings H2
    cur = None        # ("h2", name) | ("update", ts) | ("h3", name)
    cur_h2 = None     # name of the enclosing H2
    buf = []

    def flush():
        if cur is None:
            return
        body = "\n".join(buf).strip()
        kind, key = cur
        if kind == "h2":
            sections[key] = body
        elif kind == "update":
            updates.append({"timestamp": key, "body": body})
        elif kind == "h3":
            learnings[key] = body

    for line in lines[title_idx + 1:]:
        m2 = H2_RE.match(line)
        m3 = H3_RE.match(line)
        if m2:
            flush(); buf = []
            heading = m2.group("h")
            um = UPDATE_RE.match(heading)
            if um:
                cur = ("update", um.group("ts")); cur_h2 = None
            elif re.match(r"^Update\b", heading):
                raise ParseError(
                    f"malformed Update heading: `## {heading}` "
                    "(expected `## Update YYYY-MM-DDTHH:MM TZ`)")
            else:
                cur = ("h2", heading); cur_h2 = heading
                h2_order.append(heading)
        elif m3:
            flush(); buf = []
            heading = m3.group("h")
            cur = ("h3", heading)
            if cur_h2 == "Learnings":
                h3_order.append(heading)
        else:
            if cur is not None:
                buf.append(line)
    flush()

    # --- Validate required H2 present + in order (Update blocks ignored) ---
    missing2 = [s for s in REQUIRED_H2 if s not in sections]
    if missing2:
        raise ParseError("missing required section(s): " + ", ".join(missing2))
    present2 = [h for h in h2_order if h in REQUIRED_H2]
    if present2 != REQUIRED_H2:
        raise ParseError(f"required sections out of order.\n  expected: {REQUIRED_H2}\n  found:    {present2}")

    # --- Validate required H3 under Learnings present + in order ---
    missing3 = [s for s in REQUIRED_H3 if s not in learnings]
    if missing3:
        raise ParseError("missing required Learnings subsection(s): " + ", ".join(missing3))
    present3 = [h for h in h3_order if h in REQUIRED_H3]
    if present3 != REQUIRED_H3:
        raise ParseError(f"Learnings subsections out of order.\n  expected: {REQUIRED_H3}\n  found:    {present3}")

    # --- Update blocks must be chronological ---
    def sortkey(ts):
        mm = TS_SORTKEY_RE.match(ts)
        return mm.group(1) if mm else ts
    ts_list = [u["timestamp"] for u in updates]
    if ts_list != sorted(ts_list, key=sortkey):
        raise ParseError("Update blocks not in chronological order: " + ", ".join(ts_list))

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
        "started": started,
        "session_id": session_id,
        "goal": goal,
        "sections": {s: sections[s] for s in REQUIRED_H2},
        "learnings": {s: learnings[s] for s in REQUIRED_H3},
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


# Reference example (kept in sync with references/format-spec.md). Drives --self-test.
REFERENCE_EXAMPLE = """# Session Log — script-folders

**Started:** 2026-05-18 14:02 PT
**Session ID:** sess-2f9c1a4b
**Goal:** Reorganize tool scripts into self-contained per-tool folders.

## What happened
- Reorganized tool scripts into per-tool folders; added READMEs.

## Decisions & trade-offs
**Folder granularity**
- Options considered: one folder per tool vs one shared utils/.
- Chosen: per-tool.
- Why: keeps each tool self-contained and independently runnable.
- Implication: shared helpers are promoted deliberately, not duplicated by accident.

## Learnings

### Mistakes & corrections
**Symptom:** Moved a script before updating its relative import.
**Root cause:** Edited the path in one place, not the caller.
**Correct approach:** grep for references before moving a file.

### What worked & what to repeat
**Grep-before-move, once adopted**
Why it worked: surfaced callers the editor didn't show, catching two more stale imports.
Repeat: for every file move.

### User preferences & conventions
- Wants verification before "done" — asked "did you actually run it?" after a claim. Run it, then report.

## Update 2026-05-18T14:02 PT
- Set up the find-files tool; completed "split utils" (struck in To-do).

## Update 2026-05-18T14:42 PT
- Added a second tool folder; refreshed its README.

## To-do
- [x] ~~Split shared utils into per-tool folders~~ done
- [ ] Add tests for find_files.py
"""


def self_test():
    r = parse(REFERENCE_EXAMPLE)
    assert r["title"]["topic"] == "script-folders", r["title"]
    assert r["started"] == "2026-05-18 14:02 PT", r["started"]
    assert r["session_id"] == "sess-2f9c1a4b", r["session_id"]
    assert r["goal"].startswith("Reorganize"), r["goal"]
    for s in REQUIRED_H2:
        assert r["sections"][s] is not None, s
    for s in REQUIRED_H3:
        assert r["learnings"][s].strip(), f"empty Learnings subsection: {s}"
    assert [u["timestamp"] for u in r["updates"]] == ["2026-05-18T14:02 PT", "2026-05-18T14:42 PT"], r["updates"]
    assert r["todo"]["open"] == ["Add tests for find_files.py"], r["todo"]
    assert len(r["todo"]["done"]) == 1, r["todo"]
    print("self-test PASSED — every required field extracted with zero manual fixup")


def main():
    ap = argparse.ArgumentParser(description="Parse / validate a Session Log markdown file (v2).")
    ap.add_argument("path", nargs="?", help="path to a Session Log .md file")
    ap.add_argument("--self-test", action="store_true", help="parse the bundled reference example")
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
    print(f"\nCONFORMING: topic + Started + Goal + {len(result['sections'])} H2 sections "
          f"+ {len(result['learnings'])} Learnings subsections + {len(result['updates'])} update(s) "
          f"+ {len(result['todo']['open'])} open / {len(result['todo']['done'])} done to-dos",
          file=sys.stderr)


if __name__ == "__main__":
    main()
