#!/usr/bin/env python3
"""session-log governance — deterministic GREEN/RED gate.

Answers one question with no LLM and no network: is it safe yet to remove the
old session-log guidance from CLAUDE.md files and auto-memories?

Four scans, everything under a Claude root (machine-local):
  1. trigger audit   — Skill tool calls in project transcripts (.jsonl)
  2. conformance     — parse_session_log.py over central logs
  3. stale guidance  — watch-list markers still present in CLAUDE.md + memories
  4. tells           — non-conforming names / logs written inside a repo

GREEN only when: 100% of central logs conform, from >= MIN_REPOS distinct
repos, with >= MIN_SESSIONS sessions showing the skill trigger, and zero tells.
The gate fails safe: anything uncertain (no logs, parser missing, crash) -> RED.

Root defaults to ~/.claude; override with SESSION_LOG_GOVERNANCE_ROOT (used by
the test suite to point at a fixture tree).

Usage:
  python3 governance.py          # human report
  python3 governance.py --json   # machine-readable
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILLS = {"session-log", "breakdown-to-decide"}

# --- gate thresholds (tunable) -------------------------------------------------
MIN_REPOS = 2            # distinct repos with a conforming central log
MIN_SESSIONS = 3         # sessions in which session-log fired
PARSER_TIMEOUT = 30      # seconds per conformance check

# --- stale-guidance signals ----------------------------------------------------
# memory filenames whose whole purpose is a session-log convention the skill now owns
STALE_MEMORY_NAMES = {
    "feedback_journals_location.md",
    "feedback_session_log_terminology.md",
    "feedback_session_log_chronological.md",
    "feedback_session_log_depth.md",
    "feedback_session_log_session_start_date.md",
    "feedback_journal_timestamp.md",
    "feedback_scratchpad_timestamps.md",
    "feedback_datetime_headers_scratchpads.md",
    "project_session_log_location.md",
    "session-logs-directory.md",
}
# text markers that contradict the skill if found in a CLAUDE.md
CLAUDE_MD_MARKERS = [
    ("scratchpad filename", re.compile(r"scratchpad-YYYY", re.I)),
    ("in-repo .claude/session-logs", re.compile(r"\.claude/session-logs", re.I)),
    ("'Learnings about the user'", re.compile(r"Learnings about the user")),
    ("'# Session Management' section", re.compile(r"#\s*Session Management")),
    ("scratchpads/ dir", re.compile(r"scratchpads/")),
]


def claude_root() -> Path:
    env = os.environ.get("SESSION_LOG_GOVERNANCE_ROOT")
    return Path(env) if env else Path.home() / ".claude"


def make_paths(root: Path) -> dict:
    return {
        "root": root,
        "projects": root / "projects",
        "session_logs": root / "session-logs",
        "global_md": root / "CLAUDE.md",
    }


def resolve_parser() -> Path | None:
    here = Path(__file__).resolve().parent
    for cand in (
        here / "parse_session_log.py",                 # same dir (if co-located)
        here.parent / "scripts" / "parse_session_log.py",  # sibling scripts/ (repo layout)
        Path.home() / ".claude" / "skills" / "session-log" / "scripts" / "parse_session_log.py",
    ):
        if cand.exists():
            return cand
    return None


def iter_project_dirs(projects: Path):
    if not projects.exists():
        return
    for proj in sorted(projects.iterdir()):
        if proj.is_dir():
            yield proj


def project_cwd(proj: Path) -> str | None:
    """Real working directory for a project, read from its transcripts.

    The slug dir name is a lossy encoding (every '/' '.' '_' becomes '-'), so it
    cannot be reversed. Transcript records carry the true 'cwd'. Read the NEWEST
    transcript first so a migrated project reports its current cwd, not a stale one.
    """
    try:
        jsonls = sorted(proj.glob("*.jsonl"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return None
    for jsonl in jsonls:
        try:
            with jsonl.open(errors="ignore") as fh:
                for line in fh:
                    if '"cwd"' not in line:
                        continue
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    cwd = o.get("cwd")
                    if cwd:
                        return cwd
        except OSError:
            continue
    return None


# --- scan 1: trigger audit -----------------------------------------------------
def _skill_calls_in_line(line: str):
    """Yield skill names from any Skill tool_use blocks on a transcript line."""
    if '"Skill"' not in line:        # cheap pre-filter before JSON parse
        return
    try:
        o = json.loads(line)
    except json.JSONDecodeError:
        return
    msg = o.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(content, list):
        return
    for b in content:
        if (isinstance(b, dict) and b.get("type") == "tool_use"
                and b.get("name") == "Skill"):
            skill = (b.get("input") or {}).get("skill")
            if skill:
                yield skill


def scan_triggers(projects: Path, cwd_map: dict) -> dict:
    per_repo: dict[str, dict[str, int]] = {}
    # session identity = (project slug, transcript stem); stems are UUIDs but
    # pairing with the project guards against any cross-repo filename collision.
    sessions_with_skill: dict[str, set] = {s: set() for s in SKILLS}
    for proj in iter_project_dirs(projects):
        repo = cwd_map.get(proj.name) or proj.name
        counts: dict[str, int] = {}
        for jsonl in proj.glob("*.jsonl"):
            try:
                text = jsonl.read_text(errors="ignore")
            except OSError:
                continue
            for line in text.splitlines():
                for skill in _skill_calls_in_line(line):
                    if skill in SKILLS:
                        counts[skill] = counts.get(skill, 0) + 1
                        sessions_with_skill[skill].add((proj.name, jsonl.stem))
        if counts:
            per_repo[repo] = counts
    return {
        "per_repo": per_repo,
        "sessions_with_skill": {s: len(v) for s, v in sessions_with_skill.items()},
    }


# --- scan 2: conformance -------------------------------------------------------
def scan_conformance(session_logs: Path, parser: Path | None) -> dict:
    logs = sorted(session_logs.glob("*/*.md")) if session_logs.exists() else []
    results = []
    repos_conforming: set[str] = set()
    for log in logs:
        conforming, reason = None, ""
        if parser:
            try:
                proc = subprocess.run(
                    [sys.executable, str(parser), str(log)],
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    timeout=PARSER_TIMEOUT,
                )
                conforming = proc.returncode == 0
                if not conforming:
                    out = (proc.stderr or proc.stdout or "").strip().splitlines()
                    reason = out[-1][:160] if out else f"exit {proc.returncode}"
            except subprocess.TimeoutExpired:
                conforming, reason = False, "parser timeout"
            except OSError as e:
                conforming, reason = False, f"parser error: {e}"
        repo = log.parent.name
        if conforming:
            repos_conforming.add(repo)
        results.append({"file": str(log), "repo": repo,
                        "conforming": conforming, "reason": reason})
    total = len(results)
    ok = sum(1 for r in results if r["conforming"])
    return {
        "total": total,
        "conforming": ok,
        "rate": (ok / total) if total else None,
        "repos_conforming": sorted(repos_conforming),
        "results": results,
    }


# --- scan 3: stale guidance ----------------------------------------------------
def scan_stale(projects: Path, global_md: Path, cwd_map: dict) -> dict:
    hits = []
    checked_md: set[str] = set()

    def check_md(path: Path):
        if str(path) in checked_md:
            return
        checked_md.add(str(path))
        try:
            if not path.exists():
                return
            text = path.read_text(errors="ignore")
        except OSError:
            return
        for label, rx in CLAUDE_MD_MARKERS:
            if rx.search(text):
                hits.append({"where": str(path), "marker": label})

    check_md(global_md)
    for proj in iter_project_dirs(projects):
        cwd = cwd_map.get(proj.name)
        if cwd:
            check_md(Path(cwd) / "CLAUDE.md")

    stale_mem = []
    if projects.exists():
        for mem in projects.glob("*/memory/*.md"):
            if mem.name in STALE_MEMORY_NAMES:
                stale_mem.append(str(mem))
    return {"claude_md_hits": hits, "stale_memories": sorted(stale_mem)}


# --- scan 4: tells -------------------------------------------------------------
def scan_tells(projects: Path, conf: dict, cwd_map: dict) -> list[str]:
    tells = []
    for r in conf["results"]:
        if r["conforming"] is False:
            tells.append(f"non-conforming central log: {r['file']} ({r['reason']})")
        if Path(r["file"]).name.startswith("scratchpad-"):
            tells.append(f"central log uses scratchpad- name: {r['file']}")
    seen: set[str] = set()
    for proj in iter_project_dirs(projects):
        cwd = cwd_map.get(proj.name)
        if not cwd:
            continue
        for sub in ("scratchpads", ".claude/session-logs", ".claude/journals"):
            d = Path(cwd) / sub
            if str(d) in seen:
                continue
            seen.add(str(d))
            try:
                if d.exists() and any(d.glob("*.md")):
                    tells.append(f"session logs written inside a repo: {d}")
            except OSError:
                continue
    return tells


def build_report(root: Path, parser: Path | None) -> dict:
    paths = make_paths(root)
    cwd_map = {proj.name: project_cwd(proj)
               for proj in iter_project_dirs(paths["projects"])}
    triggers = scan_triggers(paths["projects"], cwd_map)
    conf = scan_conformance(paths["session_logs"], parser)
    stale = scan_stale(paths["projects"], paths["global_md"], cwd_map)
    tells = scan_tells(paths["projects"], conf, cwd_map)

    sess = triggers["sessions_with_skill"].get("session-log", 0)
    rate_ok = conf["rate"] == 1.0 and conf["total"] > 0
    repos_ok = len(conf["repos_conforming"]) >= MIN_REPOS
    sessions_ok = sess >= MIN_SESSIONS
    no_tells = len(tells) == 0
    green = bool(parser) and rate_ok and repos_ok and sessions_ok and no_tells

    blockers = []
    if not parser:
        blockers.append("parse_session_log.py not found — cannot verify conformance")
    if not rate_ok:
        blockers.append(f"conformance {conf['conforming']}/{conf['total']} (need 100% of >0)")
    if not repos_ok:
        blockers.append(f"conforming repos {len(conf['repos_conforming'])} (need >= {MIN_REPOS})")
    if not sessions_ok:
        blockers.append(f"session-log trigger sessions {sess} (need >= {MIN_SESSIONS})")
    if not no_tells:
        blockers.append(f"{len(tells)} watch-list tell(s)")

    return {
        "verdict": "GREEN" if green else "RED",
        "blockers": blockers,
        "triggers": triggers,
        "conformance": {k: conf[k] for k in ("total", "conforming", "rate", "repos_conforming")},
        "conformance_results": conf["results"],
        "stale_guidance": stale,
        "tells": tells,
        "parser_found": bool(parser),
    }


def print_report(report: dict) -> None:
    print(f"\n=== session-log governance — gate: {report['verdict']} ===")
    if report["blockers"]:
        print("blockers:")
        for b in report["blockers"]:
            print(f"  - {b}")
    t = report["triggers"]
    print(f"\ntrigger audit (sessions where skill fired): {t['sessions_with_skill']}")
    for repo, counts in t["per_repo"].items():
        print(f"  {repo}: {counts}")
    c = report["conformance"]
    print(f"\nconformance: {c['conforming']}/{c['total']} conforming; repos={c['repos_conforming']}")
    for r in report["conformance_results"]:
        mark = "ok " if r["conforming"] else "FAIL"
        print(f"  [{mark}] {r['file']}" + (f"  <- {r['reason']}" if r["reason"] else ""))
    print("\nstale guidance still present:")
    s = report["stale_guidance"]
    for h in s["claude_md_hits"]:
        print(f"  CLAUDE.md: {h['marker']}  ({h['where']})")
    for m in s["stale_memories"]:
        print(f"  memory: {m}")
    if not s["claude_md_hits"] and not s["stale_memories"]:
        print("  (none — cleanup already done)")
    print(f"\ntells: {len(report['tells'])}")
    for tell in report["tells"]:
        print(f"  - {tell}")
    if not report["parser_found"]:
        print("\nWARNING: parse_session_log.py not found — conformance unverifiable.")
    print()


# --- running markdown report (for scheduled runs) ------------------------------
REPORT_HEADER = """# Session-Log Governance Report

GREEN = safe to delete the old session-log guidance from CLAUDE.md + memories.
RED   = not safe yet (blockers listed below).

It checks 5 things; GREEN needs ALL 5:
  1. log parser available
  2. every central session log conforms (parser exit 0) — 100%
  3. conforming logs exist in >= {min_repos} different repos
  4. session-log skill fired in >= {min_sessions} sessions
  5. zero "tells" (no scratchpad-named logs, no logs written inside a repo)

This file is regenerated on every run from an append-only sibling
`.<name>-history.jsonl` (the data of record) — so the tally is counted, not guessed.
"""


def current_timestamp() -> str:
    """Local 'YYYY-MM-DD HH:MM TZ'. Override with SESSION_LOG_GOVERNANCE_NOW (tests)."""
    env = os.environ.get("SESSION_LOG_GOVERNANCE_NOW")
    if env:
        return env
    from datetime import datetime
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def history_path_for(report_path: Path) -> Path:
    return report_path.parent / ("." + report_path.stem + "-history.jsonl")


def report_record(report: dict, ts: str) -> dict:
    c = report["conformance"]
    sess = report["triggers"]["sessions_with_skill"].get("session-log", 0)
    return {
        "ts": ts,
        "verdict": report["verdict"],
        "conformance": f"{c['conforming']}/{c['total']}",
        "repos": f"{len(c['repos_conforming'])}/{MIN_REPOS}",
        "sessions": f"{sess}/{MIN_SESSIONS}",
        "tells": len(report["tells"]),
        "blockers": report["blockers"],
        "nonconforming": [f"{r['file']} <- {r['reason']}"
                          for r in report["conformance_results"]
                          if r["conforming"] is False],
        "stale_md": len(report["stale_guidance"]["claude_md_hits"]),
        "stale_mem": len(report["stale_guidance"]["stale_memories"]),
        "tells_list": report["tells"],
        "parser_found": report["parser_found"],
    }


def load_history(history_path: Path) -> list:
    records = []
    if history_path.exists():
        for line in history_path.read_text(errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def render_report(records: list) -> str:
    header = REPORT_HEADER.format(min_repos=MIN_REPOS, min_sessions=MIN_SESSIONS)
    green = sum(1 for r in records if r.get("verdict") == "GREEN")
    red = sum(1 for r in records if r.get("verdict") == "RED")
    since = records[0]["ts"].split()[0] if records else "—"
    lines = [header, "## Tally",
             f"GREEN: {green}    RED: {red}    (since {since})", "",
             "## History (newest first)",
             "| Date | Verdict | Conformance | Repos | Sessions | Tells |",
             "|------|---------|-------------|-------|----------|-------|"]
    for r in reversed(records):
        lines.append(f"| {r['ts']} | {r['verdict']} | {r['conformance']} | "
                     f"{r['repos']} | {r['sessions']} | {r['tells']} |")
    if records:
        last = records[-1]
        lines += ["", f"## Latest detail ({last['ts']})", "Blockers:"]
        bl = [f"  - {b}" for b in last["blockers"]]
        lines += bl if bl else ["  (none)"]
        if last["nonconforming"]:
            lines.append("Non-conforming logs:")
            lines += [f"  - {n}" for n in last["nonconforming"]]
        if not last.get("parser_found", True):
            lines.append("WARNING: parse_session_log.py not found — conformance unverifiable.")
        lines.append(f"Stale guidance still present: {last['stale_md']} CLAUDE.md hit(s), "
                     f"{last['stale_mem']} memory file(s)")
        lines.append(f"Tells ({last['tells']}):")
        tl = [f"  - {t}" for t in last["tells_list"]]
        lines += tl if tl else ["  (none)"]
    return "\n".join(lines) + "\n"


def write_md_report(report_path: Path, report: dict, ts: str):
    """Append this run to the history jsonl, then regenerate the markdown report."""
    history = history_path_for(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with history.open("a") as f:
        f.write(json.dumps(report_record(report, ts)) + "\n")
    report_path.write_text(render_report(load_history(history)))
    return report_path, history


def _arg_value(argv, flag, default):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            return argv[i + 1]
    return default


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    report = build_report(claude_root(), resolve_parser())

    wrote = None
    if "--md-report" in argv:
        default_path = str(Path.home() / ".claude" / "governance-report.md")
        path = Path(_arg_value(argv, "--md-report", default_path)).expanduser()
        wrote, _ = write_md_report(path, report, current_timestamp())

    if "--json" in argv:
        print(json.dumps(report, indent=2))
    elif wrote:
        print(f"gate: {report['verdict']} — report: {wrote}")
    else:
        print_report(report)
    return 0 if report["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
