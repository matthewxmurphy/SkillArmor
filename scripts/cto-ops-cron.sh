#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$AN_ROOT/logs"
mkdir -p "$LOG_DIR"

{
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] cto-ops scan start"
  python3 "$AN_ROOT/scripts/cto-ops-scan.py"
  python3 "$AN_ROOT/scripts/build-cto-dashboard-data.py"
  python3 "$AN_ROOT/scripts/build-vhost-migration-plan.py"
  python3 "$AN_ROOT/scripts/build-need-md.py"
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] cto-ops scan done"
} >> "$LOG_DIR/cto-ops-cron.log" 2>&1
