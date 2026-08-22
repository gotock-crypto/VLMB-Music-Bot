# VLMB Music Bot — production update

Upload the release to `/root/VLMB-release.tar.gz`, then on the server:

```bash
rm -rf /root/vlmb_release && mkdir -p /root/vlmb_release
tar -xzf /root/VLMB-release.tar.gz -C /root/vlmb_release
RELEASE_DIR=/root/vlmb_release/MusBot /root/MusBot/scripts/deploy_release.sh
```

The deployment creates a backup, preserves `.env`, SQLite and `venv`, installs/checks the YouTube JS runtime, runs preflight/tests/healthcheck, restarts systemd, verifies one bot process, and restores the previous tree automatically if deployment fails.
