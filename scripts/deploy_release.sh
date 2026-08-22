#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/root/MusBot}"
RELEASE_DIR="${RELEASE_DIR:-/root/vlmb_release/MusBot}"
SERVICE="${SERVICE:-musicbot}"
VENV="$APP_DIR/venv"
BACKUP="/root/MusBot-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
BACKUP_DIR=""
DEPLOY_STARTED=0

fail() { echo "ERROR: $*" >&2; exit 1; }

[[ -d "$RELEASE_DIR" ]] || fail "Release directory not found: $RELEASE_DIR"
[[ -f "$APP_DIR/.env" ]] || fail "Missing $APP_DIR/.env — refusing deployment."
[[ -x "$VENV/bin/python3" ]] || fail "Missing production venv: $VENV/bin/python3"
command -v rsync >/dev/null || fail "rsync is required"

# Validate the release while the current production bot is still running.
"$VENV/bin/python3" "$RELEASE_DIR/scripts/preflight.py" --env-file "$APP_DIR/.env" || \
  fail "Release preflight failed; production was not touched."
"$VENV/bin/python3" -m py_compile \
  "$RELEASE_DIR/music_bot_user_mixes.py" \
  "$RELEASE_DIR/config.py" \
  "$RELEASE_DIR/services"/*.py \
  "$RELEASE_DIR/scripts"/*.py

cd /root
# Backup code + production data before any runtime/dependency mutation.
# Never secrets or the production venv.
tar -czf "$BACKUP" \
  --exclude='MusBot/venv' \
  --exclude='MusBot/.env' \
  MusBot

echo "Backup: $BACKUP"

# Bring the existing runtime up to the release requirements only after the
# backup exists, so a failed dependency operation cannot leave us without a
# recoverable application snapshot.
if [[ -f "$RELEASE_DIR/requirements.txt" ]]; then
  "$VENV/bin/pip" install -r "$RELEASE_DIR/requirements.txt"
fi

rollback() {
  local rc=$?
  if (( DEPLOY_STARTED == 1 )); then
    echo "Deployment failed (exit $rc); restoring previous release..." >&2
    systemctl stop "$SERVICE" >/dev/null 2>&1 || true

    BACKUP_DIR="$(mktemp -d /root/musbot-rollback.XXXXXX)"
    tar -xzf "$BACKUP" -C "$BACKUP_DIR"

    # Restore only the backed-up tree. The production .env and venv are kept.
    rsync -a --delete \
      --exclude='.env' \
      --exclude='venv/' \
      --exclude='bot_stats.db' \
      --exclude='bot_stats.db-shm' \
      --exclude='bot_stats.db-wal' \
      --exclude='vk_tokens.db' \
      --exclude='bot.log' \
      --exclude='bot-debug.log' \
      "$BACKUP_DIR/MusBot/" "$APP_DIR/"

    if [[ -f "$APP_DIR/systemd/vlmb-musicbot.service" ]]; then
      cp "$APP_DIR/systemd/vlmb-musicbot.service" /etc/systemd/system/musicbot.service
    fi
    systemctl daemon-reload >/dev/null 2>&1 || true
    systemctl start "$SERVICE" >/dev/null 2>&1 || true
    if ! systemctl is-active --quiet "$SERVICE"; then
      echo "ERROR: rollback restored files but service did not start" >&2
    fi
    rm -rf "$BACKUP_DIR"
  fi
  exit "$rc"
}
trap rollback ERR

DEPLOY_STARTED=1
systemctl stop "$SERVICE"

rsync -a --delete \
  --exclude='.env' \
  --exclude='bot_stats.db' \
  --exclude='bot_stats.db-shm' \
  --exclude='bot_stats.db-wal' \
  --exclude='vk_tokens.db' \
  --exclude='bot.log' \
  --exclude='bot-debug.log' \
  --exclude='venv/' \
  "$RELEASE_DIR/" "$APP_DIR/"

# Guarded production rollback drill: after cutover, deliberately fail once so the ERR trap
# must restore the previous application tree. Never enable this in normal releases.
if [[ "${FORCE_FAIL_AFTER_CUTOVER:-0}" == "1" ]]; then
  echo "FORCE_FAIL_AFTER_CUTOVER=1: intentionally failing after code cutover to verify rollback" >&2
  false
fi

cp "$APP_DIR/systemd/vlmb-musicbot.service" /etc/systemd/system/musicbot.service
if [[ -f "$APP_DIR/systemd/vlmb-healthcheck.service" && -f "$APP_DIR/systemd/vlmb-healthcheck.timer" ]]; then
  cp "$APP_DIR/systemd/vlmb-healthcheck.service" /etc/systemd/system/vlmb-healthcheck.service
  cp "$APP_DIR/systemd/vlmb-healthcheck.timer" /etc/systemd/system/vlmb-healthcheck.timer
fi
systemctl daemon-reload

"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/preflight.py" --env-file "$APP_DIR/.env"
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/healthcheck.py"

systemctl start "$SERVICE"
sleep 8
systemctl is-active --quiet "$SERVICE"
pgrep -fc music_bot_user_mixes.py | grep -qx '1'
"$APP_DIR/venv/bin/python3" "$APP_DIR/scripts/healthcheck.py"
if [[ -f /etc/systemd/system/vlmb-healthcheck.timer ]]; then
  systemctl enable --now vlmb-healthcheck.timer
fi

trap - ERR
echo "Deployment completed successfully. Backup: $BACKUP"
