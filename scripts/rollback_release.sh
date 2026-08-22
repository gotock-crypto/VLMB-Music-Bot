#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${APP_DIR:-/root/MusBot}"
SERVICE="${SERVICE:-musicbot}"
BACKUP="${1:-}"
[[ -n "$BACKUP" && -f "$BACKUP" ]] || { echo "Usage: $0 /root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz" >&2; exit 2; }
[[ -f "$APP_DIR/.env" ]] || { echo "Missing $APP_DIR/.env — refusing rollback." >&2; exit 1; }
TMP_ENV="$(mktemp)"
cp "$APP_DIR/.env" "$TMP_ENV"
trap 'rm -f "$TMP_ENV"' EXIT
systemctl stop "$SERVICE"
rm -rf "$APP_DIR"
tar -xzf "$BACKUP" -C /root
cp "$TMP_ENV" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"
systemctl daemon-reload
systemctl start "$SERVICE"
sleep 5
systemctl is-active --quiet "$SERVICE"
pgrep -fc music_bot_user_mixes.py | grep -qx '1'
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/healthcheck.py"
echo "Rollback completed: $BACKUP"
