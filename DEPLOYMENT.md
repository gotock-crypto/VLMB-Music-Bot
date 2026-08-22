# Production Deployment

Use `scripts/deploy_release.sh` for release deployment with backup, preflight, restart, healthcheck and rollback.

Keep production secrets in `/root/MusBot/.env`; never commit `.env` to Git.
