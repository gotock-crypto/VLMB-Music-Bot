# VLMB 3.0.0 — Quick deployment

## 1. Windows → server

PowerShell:

```powershell
scp "D:\1\Инет\VLMB-Music-Bot-release-2026-08-22-complete.tar.gz" root@45.43.90.131:/root/VLMB-release.tar.gz
ssh root@45.43.90.131
```

## 2. Prepare release directory

```bash
rm -rf /root/vlmb_release
mkdir -p /root/vlmb_release
tar -xzf /root/VLMB-release.tar.gz -C /root/vlmb_release
cd /root/vlmb_release/VLMB-Music-Bot
```

## 3. Validate without stopping production

```bash
/root/MusBot/venv/bin/python3 scripts/preflight.py --env-file /root/MusBot/.env
/root/MusBot/venv/bin/python3 -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py
/root/MusBot/venv/bin/python3 scripts/release_audit.py
/root/MusBot/venv/bin/python3 -m pytest -q
```

All checks must pass before cutover.

## 4. Deploy

The release script expects the release at `/root/vlmb_release/MusBot` by default. For this archive use:

```bash
rm -rf /root/vlmb_release/MusBot
mv /root/vlmb_release/VLMB-Music-Bot /root/vlmb_release/MusBot
cd /root/vlmb_release/MusBot
RELEASE_DIR=/root/vlmb_release/MusBot ./scripts/deploy_release.sh
```

The script creates a backup, preserves `.env`, SQLite, logs and `venv`, installs dependencies, switches code, restarts the service, runs health checks and automatically rolls back after a failed cutover.

## 5. Enable monitoring

```bash
cp /root/MusBot/systemd/vlmb-healthcheck.service /etc/systemd/system/
cp /root/MusBot/systemd/vlmb-healthcheck.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now vlmb-healthcheck.timer
systemctl status vlmb-healthcheck.timer --no-pager
```

The deployment now installs and enables the monitor automatically. It checks health every five minutes and sends a Telegram alert/recovery message to the configured admin IDs. It uses `ADMIN_IDS` from `.env` when present, otherwise the existing `config.py` admin list.

## 6. Final checks

```bash
systemctl is-active musicbot
pgrep -fc music_bot_user_mixes.py
/root/MusBot/venv/bin/python3 /root/MusBot/scripts/healthcheck.py
systemctl list-timers --all | grep vlmb-healthcheck
```

Expected:

```text
active
1
Healthcheck OK
vlmb-healthcheck.timer ... active
```

## 7. Telegram smoke test

Check:

```text
/start
search
VK/Yandex/YouTube download
/repeat
/history
/favorites
/favorite
/mix
/digest (if used in groups)
/settings
/playlist <YouTube playlist URL>
/album <YouTube playlist URL>
```

## 8. Rollback

Use the backup printed by deployment:

```bash
/root/MusBot/scripts/rollback_release.sh /root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz
```

Never overwrite the production `.env`, SQLite databases or `venv` with archive contents.
