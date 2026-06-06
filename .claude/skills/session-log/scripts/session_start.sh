#!/usr/bin/env bash
# SessionStart hook for the session-log skill.
# Creates today's Session Log if it doesn't exist yet — idempotent, NEVER overwrites.
# SessionStart stdout is injected into Claude's context, so we report the path + next step.
set -euo pipefail

proj="${CLAUDE_PROJECT_DIR:-$(pwd)}"
dir="${proj}/.claude/session-logs"
date_str="$(date +%Y-%m-%d)"
# Placeholder topic "session" — the skill renames the file to <date>-<topic>.md once the
# session's main work is clear. Date-only naming means at most one auto-created stub per day;
# a second same-day session reuses (or the skill renames the first before the second starts).
file="${dir}/${date_str}-session.md"

mkdir -p "${dir}"

if [ ! -f "${file}" ]; then
  cat > "${file}" <<EOF
# Session: session — ${date_str}

**Goal:** TBD — set when the session's intent is clear.

## What happened

## Decisions & trade-offs

## Mistakes & corrections

## What worked & what to repeat

## Learnings about the user

## Where to pick up

## To-do
EOF
  echo "Session Log created at ${file}. Next: set the **Goal:** line, and rename the file to ${date_str}-<topic>.md once the session's main work is clear. Update it incrementally — do not reconstruct at close."
else
  echo "Session Log already exists at ${file}. Update it as the session progresses; never overwrite it."
fi
