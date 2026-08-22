#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${APP_DIR:-/root/MusBot}"
RELEASE_DIR="${RELEASE_DIR:-/root/vlmb_release/MusBot}"
SERVICE="${SERVICE:-musicbot}"
BACKUP="/root/MusBot-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
[[ -d "$RELEASE_DIR" ]] || { echo "Release directory not found: $RELEASE_DIR" >&2; exit 1; }
[[ -f "$APP_DIR/.env" ]] || { echo "Missing $APP_DIR/.env — refusing deployment." >&2; exit 1; }
command -v rsync >/dev/null || { echo "rsync is required" >&2; exit 1; }
cd /root
tar -czf "$BACKUP" --exclude='MusBot/venv' --exclude='MusBot/.env' MusBot
echo "Backup: $BACKUP"
TMP_ENV="$(mktemp)"
cp "$APP_DIR/.env" "$TMP_ENV"
chmod 600 "$TMP_ENV"
cleanup() { rm -f "$TMP_ENV"; }
trap cleanup EXIT
systemctl stop "$SERVICE"
rollback() {
  echo "Deployment failed; restoring previous tree..." >&2
  systemctl stop "$SERVICE" >/dev/null 2>&1 || true
  rm -rf "$APP_DIR"
  tar -xzf "$BACKUP" -C /root
  cp "$TMP_ENV" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  systemctl daemon-reload >/dev/null 2>&1 || true
  systemctl start "$SERVICE" >/dev/null 2>&1 || true
}
trap rollback ERR
rsync -a --delete \
  --exclude='.env' --exclude='bot_stats.db' --exclude='bot_stats.db-shm' --exclude='bot_stats.db-wal' \
  --exclude='vk_tokens.db' --exclude='bot.log' --exclude='bot-debug.log' --exclude='venv/' \
  "$RELEASE_DIR/" "$APP_DIR/"
cp "$APP_DIR/systemd/vlmb-musicbot.service" /etc/systemd/system/musicbot.service
systemctl daemon-reload
"$APP_DIR/scripts/ensure_youtube_runtime.sh"
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/preflight.py"
"$APP_DIR/venv/bin/python3" -m pytest -q
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/healthcheck.py"
systemctl start "$SERVICE"
sleep 8
systemctl is-active --quiet "$SERVICE"
pgrep -fc music_bot_user_mixes.py | grep -qx '1'
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/healthcheck.py"
trap - ERR
echo "Deployment completed successfully. Backup: $BACKUP"
