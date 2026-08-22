# Quick Deployment

1. Upload release archive to the server.
2. Extract it to a temporary release directory.
3. Run preflight, compile, release audit and tests.
4. Deploy with `RELEASE_DIR=/root/vlmb_release/MusBot ./scripts/deploy_release.sh`.
5. Verify healthcheck and systemd status.
