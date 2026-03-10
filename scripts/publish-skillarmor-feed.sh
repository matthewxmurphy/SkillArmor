#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OPS_ROOT="${OPS_ROOT:-$(cd "$AN_ROOT/.." && pwd)}"
SITE_ROOT="${SKILLARMOR_SITE_ROOT:-$OPS_ROOT/skillarmor-site}"
CFG_PATH="${SKILLARMOR_DEPLOY_CONFIG:-$AN_ROOT/data/skillarmor-deploy-config.json}"
LOG_DIR="$AN_ROOT/logs"
mkdir -p "$LOG_DIR"

log() {
  printf '[%s] %s\n' "$(date +'%Y-%m-%dT%H:%M:%S%z')" "$*"
}

if [[ ! -f "$CFG_PATH" ]]; then
  log "Missing deploy config: $CFG_PATH"
  exit 1
fi

CFG_OUT="$(python3 - "$CFG_PATH" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1], encoding='utf-8'))
print("true" if bool(cfg.get("enabled", False)) else "false")
print(cfg.get("host", ""))
print(int(cfg.get("port", 22) or 22))
print(cfg.get("user", "ubuntu"))
print(cfg.get("sshKeyPath", ""))
print(cfg.get("remoteSiteDir", "/var/www/skillarmor"))
print("true" if bool(cfg.get("feedOnly", True)) else "false")
PY
)"

ENABLED="$(printf '%s\n' "$CFG_OUT" | sed -n '1p')"
HOST="$(printf '%s\n' "$CFG_OUT" | sed -n '2p')"
PORT="$(printf '%s\n' "$CFG_OUT" | sed -n '3p')"
USER="$(printf '%s\n' "$CFG_OUT" | sed -n '4p')"
KEY_PATH="$(printf '%s\n' "$CFG_OUT" | sed -n '5p')"
REMOTE_DIR="$(printf '%s\n' "$CFG_OUT" | sed -n '6p')"
FEED_ONLY="$(printf '%s\n' "$CFG_OUT" | sed -n '7p')"

if [[ "$ENABLED" != "true" ]]; then
  log "Deploy disabled in config."
  exit 0
fi
if [[ -z "$HOST" ]]; then
  log "Host is required in deploy config."
  exit 1
fi

SSH_OPTS=(-p "$PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
if [[ -n "$KEY_PATH" ]]; then
  SSH_OPTS+=(-i "$KEY_PATH")
fi

log "Building feed JSON"
mkdir -p "$SITE_ROOT/data"
python3 "$AN_ROOT/scripts/export-skillarmor-feed.py" --out "$SITE_ROOT/data/skillarmor-feed.json"
FEED_PATH="$SITE_ROOT/data/skillarmor-feed.json"
if [[ ! -f "$FEED_PATH" ]]; then
  log "Feed file missing after export: $FEED_PATH"
  exit 1
fi

if [[ "$FEED_ONLY" != "true" && ! -f "$SITE_ROOT/index.html" ]]; then
  log "Static site root missing index.html: $SITE_ROOT"
  exit 1
fi

log "Ensuring remote directories"
ssh "${SSH_OPTS[@]}" "$USER@$HOST" "mkdir -p '$REMOTE_DIR/data' '$REMOTE_DIR/assets'"

if [[ "$FEED_ONLY" == "true" ]]; then
  log "Uploading feed only"
  scp "${SSH_OPTS[@]}" "$FEED_PATH" "$USER@$HOST:$REMOTE_DIR/data/skillarmor-feed.json.new"
  ssh "${SSH_OPTS[@]}" "$USER@$HOST" "mv '$REMOTE_DIR/data/skillarmor-feed.json.new' '$REMOTE_DIR/data/skillarmor-feed.json'"
else
  log "Uploading full static site"
  rsync -az --delete -e "ssh ${SSH_OPTS[*]}" "$SITE_ROOT/" "$USER@$HOST:$REMOTE_DIR/"
fi

log "Publish complete"
