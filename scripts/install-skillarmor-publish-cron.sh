#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/skillarmor-publish-cron.sh"
MARKER="# skillarmor-feed-publish-cron"
ENTRY="0 */12 * * * /bin/bash \"$RUNNER\" $MARKER"

if ! command -v crontab >/dev/null 2>&1; then
  echo "crontab_not_found"
  exit 1
fi

TMP="$(mktemp)"
crontab -l 2>/dev/null | sed "/$MARKER/d" > "$TMP" || true
echo "$ENTRY" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

echo "installed:$ENTRY"
