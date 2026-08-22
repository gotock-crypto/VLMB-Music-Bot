#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/root/MusBot}"
SERVICE="${SERVICE:-musicbot}"
BACKUP="${1:-}"

[[ -n "$BACKUP" && -f "$BACKUP" ]] || {
  echo "Usage: $0 /root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz" >&2
  exit 2
}
[[ -f "$APP_DIR/.env" ]] || {
  echo "Missing $APP_DIR/.env — refusing rollback." >&2
  exit 1
}
[[ -x "$APP_DIR/venv/bin/python3" ]] || {
  echo "Missing production venv — refusing rollback because the backup intentionally excludes it." >&2
  exit 1
}
command -v rsync >/dev/null || { echo "rsync is required" >&2; exit 1; }

TMP_DIR="$(mktemp -d /root/musbot-rollback.XXXXXX)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

tar -xzf "$BACKUP" -C "$TMP_DIR"
[[ -d "$TMP_DIR/MusBot" ]] || { echo "Invalid backup: MusBot tree missing" >&2; exit 1; }

systemctl stop "$SERVICE"

# Restore the backed-up tree without deleting the live .env, databases, logs or venv.
rsync -a --delete \
  --exclude='.env' \
  --exclude='venv/' \
  --exclude='bot_stats.db' \
  --exclude='bot_stats.db-shm' \
  --exclude='bot_stats.db-wal' \
  --exclude='vk_tokens.db' \
  --exclude='bot.log' \
  --exclude='bot-debug.log' \
  "$TMP_DIR/MusBot/" "$APP_DIR/"

cp "$APP_DIR/systemd/vlmb-musicbot.service" /etc/systemd/system/musicbot.service
chmod 600 "$APP_DIR/.env"
systemctl daemon-reload
systemctl start "$SERVICE"
sleep 5
systemctl is-active --quiet "$SERVICE"
pgrep -fc music_bot_user_mixes.py | grep -qx '1'
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/healthcheck.py"

echo "Rollback completed: $BACKUP"
