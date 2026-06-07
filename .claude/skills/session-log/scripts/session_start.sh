#!/usr/bin/env bash
# SessionStart hook for the session-log skill.
# Creates this session's Session Log if absent — idempotent, NEVER overwrites.
#
# Logs are stored CENTRALLY at ~/.claude/session-logs/<repo>/ — OUTSIDE any repo — so they're
# never a public-repo privacy risk and need no per-project .gitignore. <repo> is the repo's
# directory name, resolved via git-common-dir so all worktrees of one repo share a dir (like
# auto-memory); falls back to the project-dir basename outside git.
#
# Filename is time-prefixed (YYYY-MM-DDTHHMM-topic.md, no colon/TZ) so same-repo sessions don't
# collide. Idempotency is keyed on the session_id (from stdin JSON): on a resume the wall-clock
# differs, so we find this session's existing log by its embedded session_id and reuse it.
# A numeric suffix guards the rare same-minute case. SessionStart stdout is injected into context.
set -euo pipefail

# session_id from the SessionStart stdin JSON (no jq; tolerant of empty stdin).
session_id="$(python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('session_id', ''))
except Exception:
    print('')
" 2>/dev/null || true)"
[ -z "${session_id}" ] && session_id="unknown"

proj="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Repo-stable slug (shared across worktrees, like auto-memory). git-common-dir points at the
# main repo's .git even from a linked worktree; its parent dir is the repo root.
slug=""
if gcd="$(git -C "${proj}" rev-parse --git-common-dir 2>/dev/null)"; then
  case "${gcd}" in
    /*) repo_root="$(dirname "${gcd}")" ;;   # absolute → worktree case
    *)  repo_root="${proj}" ;;               # relative ".git" → main repo
  esac
  slug="$(basename "${repo_root}")"
fi
[ -z "${slug}" ] && slug="$(basename "${proj}")"

dir="${HOME}/.claude/session-logs/${slug}"
mkdir -p "${dir}"

# Resume-safe: if a log already carries this session_id, reuse it (don't make a second file).
if [ "${session_id}" != "unknown" ]; then
  existing="$(grep -rlF "**Session ID:** ${session_id}" "${dir}" 2>/dev/null | head -1 || true)"
  if [ -n "${existing}" ]; then
    echo "Session Log already exists at ${existing} (matched by session_id). Update it as the session progresses; never overwrite it."
    exit 0
  fi
fi

started="$(date '+%Y-%m-%d %H:%M %Z')"
prefix="$(date +%Y-%m-%dT%H%M)"   # T-separated, no colon, no TZ
file="${dir}/${prefix}-session.md"
if [ -f "${file}" ]; then
  n=2
  while [ -f "${dir}/${prefix}-session-${n}.md" ]; do n=$((n + 1)); done
  file="${dir}/${prefix}-session-${n}.md"
fi

cat > "${file}" <<EOF
# Session Log — session

**Started:** ${started}
**Session ID:** ${session_id}
**Goal:** TBD — set when the session's intent is clear.

## What happened

## Decisions & trade-offs

## Learnings

### Mistakes & corrections

### What worked & what to repeat

### User preferences & conventions

## To-do
EOF
echo "Session Log created at ${file}. Next: set the **Goal:** line, and rename the file to ${prefix}-<topic>.md once the session's main work is clear. Update it incrementally — walk every section, don't skip Learnings."
