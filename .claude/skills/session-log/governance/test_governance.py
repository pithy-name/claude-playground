#!/usr/bin/env python3
"""Test suite for governance.py — deterministic, fixture-based, stdlib only.

Builds a fake Claude root in a tempdir (projects/, session-logs/, CLAUDE.md,
fake repo cwds) and asserts each scan + the GREEN/RED verdict. Points the script
at the fixture via SESSION_LOG_GOVERNANCE_ROOT. Uses the REAL parse_session_log.py
(sibling) for conformance, so a parser regression also trips these tests.

Run:  python3 test_governance.py
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import governance as gov

CONFORMING_LOG = """# Session Log — Fixture

**Started:** 2026-06-08 14:00 PDT
**Session ID:** sess-fixture
**Goal:** fixture log for tests.

## What happened

- did a thing

## Decisions & trade-offs

**A decision**
- Options considered: x, y
- Chosen: x
- Why: because

## Learnings

### Mistakes & corrections

- **Symptom:** s **Root cause:** r **Correct approach:** c

### What worked & what to repeat

- **win**
  Why it worked: reason
  Repeat: yes

### User preferences & conventions

- prefers x (signal: said so)

## To-do

- [ ] open item
"""

# missing the third required H3 -> parser should reject
NONCONFORMING_LOG = """# Session Log — Bad

**Started:** 2026-06-08 14:00 PDT
**Session ID:** sess-bad
**Goal:** broken.

## What happened

- thing

## Decisions & trade-offs

## Learnings

### Mistakes & corrections

- none

### What worked & what to repeat

- none

## To-do

- [ ] x
"""


def transcript_line(cwd: str, skill: str | None = None, plain: bool = False) -> str:
    """One JSONL record. skill -> a Skill tool_use; plain -> a user line w/ cwd."""
    if plain:
        return json.dumps({"cwd": cwd, "type": "user",
                           "message": {"content": "hi"}})
    if skill:
        return json.dumps({
            "cwd": cwd, "sessionId": "x",
            "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}
            ]},
        })
    return json.dumps({"cwd": cwd, "message": {"content": []}})


class GovernanceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name) / ".claude"
        (self.root / "projects").mkdir(parents=True)
        (self.root / "session-logs").mkdir(parents=True)
        self.repos = Path(self._tmp.name) / "repos"
        self.repos.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixture builders --
    def add_project(self, slug, cwd, lines):
        d = self.root / "projects" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.jsonl").write_text("\n".join(lines) + "\n")
        return d

    def add_central_log(self, repo, name, body):
        d = self.root / "session-logs" / repo
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body)

    def add_repo_cwd(self, name, claude_md=None, scratchpad_md=False):
        repo = self.repos / name
        repo.mkdir(parents=True, exist_ok=True)
        if claude_md is not None:
            (repo / "CLAUDE.md").write_text(claude_md)
        if scratchpad_md:
            sp = repo / "scratchpads"
            sp.mkdir()
            (sp / "scratchpad-2026-01-01-x.md").write_text("old")
        return str(repo)

    def report(self):
        return gov.build_report(self.root, gov.resolve_parser())

    # -- tests --
    def test_parser_resolves(self):
        self.assertIsNotNone(gov.resolve_parser(),
                             "parse_session_log.py must sit beside governance.py")

    def test_trigger_audit_counts_and_sessions(self):
        cwd = self.add_repo_cwd("repoA")
        self.add_project("slugA", cwd, [
            transcript_line(cwd, plain=True),
            transcript_line(cwd, skill="session-log"),
            transcript_line(cwd, skill="session-log"),
            transcript_line(cwd, skill="breakdown-to-decide"),
            transcript_line(cwd, skill="not-our-skill"),
        ])
        rep = self.report()
        self.assertEqual(rep["triggers"]["per_repo"][cwd],
                         {"session-log": 2, "breakdown-to-decide": 1})
        # one transcript file => one session, even with 2 session-log calls
        self.assertEqual(rep["triggers"]["sessions_with_skill"]["session-log"], 1)

    def test_conformance_pass_and_fail(self):
        self.add_central_log("repoA", "2026-06-08T1400-a.md", CONFORMING_LOG)
        self.add_central_log("repoA", "2026-06-08T1500-bad.md", NONCONFORMING_LOG)
        rep = self.report()
        self.assertEqual(rep["conformance"]["total"], 2)
        self.assertEqual(rep["conformance"]["conforming"], 1)
        results = {Path(r["file"]).name: r for r in rep["conformance_results"]}
        self.assertTrue(results["2026-06-08T1400-a.md"]["conforming"])
        self.assertFalse(results["2026-06-08T1500-bad.md"]["conforming"])

    def test_stale_guidance_detected(self):
        cwd = self.add_repo_cwd("repoA", claude_md="see .claude/session-logs/ here")
        self.add_project("slugA", cwd, [transcript_line(cwd, plain=True)])
        (self.root / "CLAUDE.md").write_text(
            "# Session Management\nScratchpad-YYYY-MM-DD; Learnings about the user")
        (self.root / "projects" / "slugA" / "memory").mkdir()
        (self.root / "projects" / "slugA" / "memory"
         / "feedback_journals_location.md").write_text("x")
        rep = self.report()
        markers = {h["marker"] for h in rep["stale_guidance"]["claude_md_hits"]}
        self.assertIn("'# Session Management' section", markers)
        self.assertIn("in-repo .claude/session-logs", markers)
        self.assertTrue(any("feedback_journals_location.md" in m
                            for m in rep["stale_guidance"]["stale_memories"]))

    def test_tells_inrepo_and_nonconforming(self):
        cwd = self.add_repo_cwd("repoA", scratchpad_md=True)
        self.add_project("slugA", cwd, [transcript_line(cwd, plain=True)])
        self.add_central_log("repoA", "2026-06-08T1500-bad.md", NONCONFORMING_LOG)
        rep = self.report()
        joined = " ".join(rep["tells"])
        self.assertIn("written inside a repo", joined)
        self.assertIn("non-conforming central log", joined)

    def test_scratchpad_named_central_log_is_a_tell(self):
        self.add_central_log("repoA", "scratchpad-2026-06-08-x.md", CONFORMING_LOG)
        rep = self.report()
        self.assertTrue(any("scratchpad- name" in t for t in rep["tells"]))

    def test_verdict_green_when_all_pass(self):
        # 2 conforming repos, 3 session-log sessions, clean cwds (no tells)
        for i in range(3):
            cwd = self.add_repo_cwd(f"clean{i}")  # no CLAUDE.md, no scratchpads
            self.add_project(f"slug{i}", cwd, [transcript_line(cwd, skill="session-log")])
        self.add_central_log("repoA", "2026-06-08T1400-a.md", CONFORMING_LOG)
        self.add_central_log("repoB", "2026-06-08T1500-b.md", CONFORMING_LOG)
        rep = self.report()
        self.assertEqual(rep["verdict"], "GREEN", rep["blockers"])
        self.assertEqual(rep["blockers"], [])

    def test_verdict_red_when_too_few_sessions(self):
        self.add_central_log("repoA", "2026-06-08T1400-a.md", CONFORMING_LOG)
        self.add_central_log("repoB", "2026-06-08T1500-b.md", CONFORMING_LOG)
        cwd = self.add_repo_cwd("clean0")
        self.add_project("slug0", cwd, [transcript_line(cwd, skill="session-log")])
        rep = self.report()
        self.assertEqual(rep["verdict"], "RED")
        self.assertTrue(any("trigger sessions" in b for b in rep["blockers"]))

    def test_verdict_red_when_one_log_nonconforming(self):
        for i in range(3):
            cwd = self.add_repo_cwd(f"clean{i}")
            self.add_project(f"slug{i}", cwd, [transcript_line(cwd, skill="session-log")])
        self.add_central_log("repoA", "2026-06-08T1400-a.md", CONFORMING_LOG)
        self.add_central_log("repoB", "2026-06-08T1500-b.md", NONCONFORMING_LOG)
        rep = self.report()
        self.assertEqual(rep["verdict"], "RED")

    def test_empty_root_is_red_not_crash(self):
        rep = self.report()  # nothing added
        self.assertEqual(rep["verdict"], "RED")
        self.assertIsNone(rep["conformance"]["rate"])

    def test_robust_to_malformed_json_and_nonutf8(self):
        cwd = self.add_repo_cwd("repoA")
        d = self.add_project("slugA", cwd, [
            transcript_line(cwd, skill="session-log"),
            "{ this is not valid json",
            '{"message": {"content": "not-a-list"}}',
        ])
        # append raw non-UTF8 bytes as another transcript
        (d / "binary.jsonl").write_bytes(b'\xff\xfe"name":"Skill"\x00\n')
        rep = self.report()  # must not raise
        self.assertEqual(rep["triggers"]["sessions_with_skill"]["session-log"], 1)

    # -- running markdown report --
    def _make_green(self):
        for i in range(3):
            cwd = self.add_repo_cwd(f"clean{i}")
            self.add_project(f"slug{i}", cwd, [transcript_line(cwd, skill="session-log")])
        self.add_central_log("repoA", "a.md", CONFORMING_LOG)
        self.add_central_log("repoB", "b.md", CONFORMING_LOG)

    def test_md_report_first_run_red(self):
        self.add_central_log("repoA", "bad.md", NONCONFORMING_LOG)  # forces RED
        rep = self.report()
        out = Path(self._tmp.name) / "governance-report.md"
        gov.write_md_report(out, rep, "2026-06-08 17:20 PDT")
        txt = out.read_text()
        self.assertIn("GREEN: 0", txt)
        self.assertIn("RED: 1", txt)
        self.assertIn("2026-06-08 17:20 PDT | RED", txt)
        hist = gov.history_path_for(out)
        self.assertTrue(hist.exists())
        self.assertEqual(len([l for l in hist.read_text().splitlines() if l.strip()]), 1)

    def test_md_report_accumulates_green_after_red(self):
        out = Path(self._tmp.name) / "governance-report.md"
        gov.write_md_report(out, self.report(), "2026-06-08 17:20 PDT")  # RED (empty)
        self._make_green()
        rep2 = self.report()
        self.assertEqual(rep2["verdict"], "GREEN", rep2["blockers"])
        gov.write_md_report(out, rep2, "2026-06-15 09:00 PDT")
        txt = out.read_text()
        self.assertIn("GREEN: 1", txt)
        self.assertIn("RED: 1", txt)
        self.assertIn("2026-06-15 09:00 PDT | GREEN", txt)
        # newest-first: green row appears above the older red row
        self.assertLess(txt.index("2026-06-15 09:00 PDT"), txt.index("2026-06-08 17:20 PDT"))
        hist = gov.history_path_for(out)
        self.assertEqual(len([l for l in hist.read_text().splitlines() if l.strip()]), 2)

    def test_md_report_history_survives_corrupt_line(self):
        out = Path(self._tmp.name) / "governance-report.md"
        hist = gov.history_path_for(out)
        hist.parent.mkdir(parents=True, exist_ok=True)
        hist.write_text("{ not json\n")  # pre-existing garbage line
        gov.write_md_report(out, self.report(), "2026-06-08 17:20 PDT")
        self.assertIn("RED: 1", out.read_text())  # must not crash

    def test_project_cwd_prefers_newest_transcript(self):
        import os, time
        d = self.root / "projects" / "slugA"
        d.mkdir(parents=True)
        old = d / "old.jsonl"
        new = d / "new.jsonl"
        old.write_text(transcript_line("/old/path", plain=True) + "\n")
        new.write_text(transcript_line("/new/path", plain=True) + "\n")
        # force new to be newer
        past = time.time() - 1000
        os.utime(old, (past, past))
        self.assertEqual(gov.project_cwd(d), "/new/path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
