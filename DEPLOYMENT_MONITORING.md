# VLMB monitoring setup

Install the health monitor after the normal deployment:

```bash
cp /root/MusBot/systemd/vlmb-healthcheck.service /etc/systemd/system/
cp /root/MusBot/systemd/vlmb-healthcheck.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now vlmb-healthcheck.timer
systemctl status vlmb-healthcheck.timer --no-pager
```

The monitor runs `scripts/healthcheck.py` every five minutes. It sends a Telegram alert to the numeric IDs in `ADMIN_IDS` from `.env` only when health changes between healthy/unhealthy states. No token is printed by the monitor.

Check manually:

```bash
systemctl start vlmb-healthcheck.service
journalctl -u vlmb-healthcheck.service -n 50 --no-pager
```
