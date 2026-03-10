#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$ROOT/logs"
CONFIG_PATH="$ROOT/data/comment-post-config.json"
mkdir -p "$LOG_DIR"

ts() {
  date +"%Y-%m-%dT%H:%M:%S%z"
}

log() {
  printf '[%s] %s\n' "$(ts)" "$*"
}

{
  log "comment-queue cron run started"

  if [[ ! -f "$ROOT/data/audit-findings.json" ]]; then
    log "audit-findings.json missing; running analytizer refresh first"
    python3 "$ROOT/scripts/clawhub-analytizer.py"
  fi

  ENABLED="false"
  MAX_POSTS="1"
  POST_CMD=""
  if [[ -f "$CONFIG_PATH" ]]; then
    CFG_OUT="$(python3 - "$CONFIG_PATH" <<'PY'
import json, sys
path = sys.argv[1]
cfg = json.load(open(path, encoding="utf-8"))
enabled = bool(cfg.get("enabled", False))
max_posts = int(cfg.get("maxPostsPerRun", 1) or 1)
post_cmd = str(cfg.get("postCommandTemplate", "") or "")
print("true" if enabled else "false")
print(max(1, max_posts))
print(post_cmd)
PY
)"
    ENABLED="$(printf '%s\n' "$CFG_OUT" | sed -n '1p')"
    MAX_POSTS="$(printf '%s\n' "$CFG_OUT" | sed -n '2p')"
    POST_CMD="$(printf '%s\n' "$CFG_OUT" | sed -n '3p')"
  fi

  if [[ "$ENABLED" == "true" && -n "$POST_CMD" ]]; then
    log "queue process mode enabled; posting up to $MAX_POSTS item(s)"
    python3 "$ROOT/scripts/process-comment-queue.py" \
      --process \
      --max-posts "$MAX_POSTS" \
      --post-command "$POST_CMD"
  else
    log "queue generation only (post command disabled or not configured)"
    python3 "$ROOT/scripts/process-comment-queue.py"
  fi

  log "comment-queue cron run completed"
} >> "$LOG_DIR/comment-queue-cron.log" 2>&1
