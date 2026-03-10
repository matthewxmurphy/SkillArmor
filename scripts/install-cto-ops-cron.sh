#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/cto-ops-cron.sh"
CRON_LINE="0 * * * * /bin/bash \"$SCRIPT_PATH\" # cto-ops-cron"

if [[ ! -x "$SCRIPT_PATH" ]]; then
  chmod +x "$SCRIPT_PATH"
fi

CURRENT="$(crontab -l 2>/dev/null || true)"
UPDATED="$(printf "%s\n" "$CURRENT" | sed '/# cto-ops-cron/d' | sed '/cto-ops-cron.sh/d')"
{
  printf "%s\n" "$UPDATED"
  printf "%s\n" "$CRON_LINE"
} | crontab -

echo "Installed hourly CTO ops cron."
echo "$CRON_LINE"
