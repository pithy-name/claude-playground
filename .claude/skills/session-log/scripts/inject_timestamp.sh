#!/usr/bin/env bash
# PreToolUse hook (matcher Write|Edit) for the session-log skill.
# PreToolUse plain stdout does NOT reach Claude — context must be injected via JSON
# hookSpecificOutput.additionalContext. This surfaces the real current time so Session Log
# Update-block timestamps are taken from the clock, never guessed.
set -euo pipefail

ts="$(date "+%Y-%m-%dT%H:%M %Z")"

# Emit JSON with python3 (no jq dependency) so the timestamp is safely escaped.
python3 - "$ts" <<'PY'
import json, sys
ts = sys.argv[1]
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "Current local time is " + ts +
            ". Use this exact value for any Session Log `## Update` timestamp "
            "(format: YYYY-MM-DDTHH:MM TZ). Do not guess the time."
        ),
    }
}))
PY
