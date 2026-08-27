# VLMB 4.0.0-rc2 Upgrade Procedure

Target production root remains `/root/MusBot`; do not replace `.env`, SQLite databases or `venv`.

## Upload
```bash
scp VLMB-Music-Bot-4.0.0-rc2-2026-08-27.tar.gz root@45.43.90.131:/root/VLMB-release-rc2.tar.gz
ssh root@45.43.90.131
```

## Extract without touching production
```bash
rm -rf /root/vlmb_release
mkdir -p /root/vlmb_release
tar -xzf /root/VLMB-release-rc2.tar.gz -C /root/vlmb_release
mv /root/vlmb_release/VLMB-Music-Bot-4.0.0-rc2 /root/vlmb_release/MusBot
cd /root/vlmb_release/MusBot
```

## Validate before cutover
```bash
/root/MusBot/venv/bin/python3 scripts/preflight.py --env-file /root/MusBot/.env
/root/MusBot/venv/bin/python3 -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py application/use_cases/*.py domain/*.py providers/*.py storage/*.py
/root/MusBot/venv/bin/python3 scripts/release_audit.py --ci
/root/MusBot/venv/bin/python3 scripts/release_artifact_audit.py
```
If any command fails: **STOP. Do not run deployment.**

## Deploy
```bash
RELEASE_DIR=/root/vlmb_release/MusBot ./scripts/deploy_release.sh
```

The deployment script creates a backup before dependency mutation, preserves `.env`, databases, logs and `venv`, then performs cutover, restart and healthcheck with rollback on post-cutover failure.

## Verify
```bash
systemctl is-active musicbot
pgrep -fc music_bot_user_mixes.py
/root/MusBot/venv/bin/python3 /root/MusBot/scripts/healthcheck.py
journalctl -u musicbot -n 80 --no-pager
```
Expected process count: `1`.

## Telegram smoke test
Verify `/start`, `/help`, `/settings`, `/history`, `/favorites`, `/playlist`, `/album`, search, result → download, favorite/remove-favorite, history → redownload, similar → search → back, pagination and settings → back.

## Rollback
Use the exact backup path printed by deployment:
```bash
/root/MusBot/scripts/rollback_release.sh /root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz
```
Do not overwrite production `.env`, databases or `venv` from the archive.
