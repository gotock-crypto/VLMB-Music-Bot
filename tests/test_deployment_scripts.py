from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_deploy_preserves_runtime_and_secrets():
    text = (ROOT / "scripts/deploy_release.sh").read_text()
    assert "--exclude='.env'" in text
    assert "--exclude='venv/'" in text
    assert "--exclude='bot_stats.db'" in text
    assert "--exclude='vk_tokens.db'" in text
    assert "systemctl stop \"$SERVICE\"" in text
    assert "DEPLOY_STARTED=1" in text


def test_deploy_uses_env_file_for_preflight():
    text = (ROOT / "scripts/deploy_release.sh").read_text()
    assert '--env-file "$APP_DIR/.env"' in text


def test_rollback_does_not_delete_venv_or_env():
    text = (ROOT / "scripts/rollback_release.sh").read_text()
    assert "[[ -x \"$APP_DIR/venv/bin/python3\" ]]" in text
    assert "--exclude='.env'" in text
    assert "--exclude='venv/'" in text
    assert "rm -rf \"$APP_DIR\"" not in text


def test_preflight_supports_explicit_env_file():
    text = (ROOT / "scripts/preflight.py").read_text()
    assert '"--env-file"' in text
    assert "parse_env_file" in text
    assert "os.environ" in text
