#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

{
  printf '[%s] skillarmor publish cron start\n' "$(date +'%Y-%m-%dT%H:%M:%S%z')"
  /bin/bash "$ROOT/scripts/publish-skillarmor-feed.sh"
  printf '[%s] skillarmor publish cron end\n' "$(date +'%Y-%m-%dT%H:%M:%S%z')"
} >> "$LOG_DIR/skillarmor-publish-cron.log" 2>&1
