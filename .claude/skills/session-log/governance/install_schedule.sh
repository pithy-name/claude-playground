#!/usr/bin/env bash
# Install a weekly launchd job that runs the session-log governance gate and
# refreshes ~/.claude/governance-report.md. macOS only (uses launchd).
#
# launchd, unlike cron, runs a missed StartCalendarInterval job on next wake —
# so a weekly check still fires even if the Mac was asleep at the scheduled time.
#
# Usage:   bash install_schedule.sh           # install + load (Mondays 09:00)
#          bash install_schedule.sh --uninstall
#
# Paths are resolved from $HOME at install time and written into the generated
# plist under ~/Library/LaunchAgents — nothing here hardcodes a username.
set -euo pipefail

LABEL="sessionlog.governance"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
SCRIPT="${HOME}/.claude/skills/session-log/governance/governance.py"
REPORT="${HOME}/.claude/governance-report.md"
LOG="${HOME}/.claude/governance-cron.log"

if [ "${1:-}" = "--uninstall" ]; then
  launchctl unload "${PLIST}" 2>/dev/null || true
  rm -f "${PLIST}"
  echo "uninstalled ${LABEL} (report + history left in place)"
  exit 0
fi

PY="$(command -v python3 || true)"
[ -n "${PY}" ] || { echo "ERROR: python3 not found on PATH"; exit 1; }
[ -f "${SCRIPT}" ] || { echo "ERROR: governance.py not found at ${SCRIPT} — install the skill globally first"; exit 1; }

mkdir -p "${HOME}/Library/LaunchAgents"

cat > "${PLIST}" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PY}</string>
    <string>${SCRIPT}</string>
    <string>--md-report</string>
    <string>${REPORT}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>1</integer>
    <key>Hour</key><integer>9</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>${LOG}</string>
  <key>StandardErrorPath</key>
  <string>${LOG}</string>
</dict>
</plist>
PLIST

launchctl unload "${PLIST}" 2>/dev/null || true
launchctl load "${PLIST}"

echo "installed ${LABEL}: runs ${PY} weekly (Mon 09:00), writes ${REPORT}"
echo "  check:     launchctl list | grep ${LABEL}"
echo "  run now:   launchctl start ${LABEL}"
echo "  uninstall: bash install_schedule.sh --uninstall"
