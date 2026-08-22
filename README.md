# 🎵 VLMB Music Bot 3.0.0

Асинхронный Telegram-бот для поиска и скачивания музыки из Яндекс.Музыки, VK и YouTube.

## Что есть в 3.0.0

- 🔎 Search Engine 2.0: нормализация, artist/title scoring, дедупликация.
- 🏥 Provider Router: классификация ошибок, circuit breaker и failover primitives.
- ⚡ Redis + LRU cache и persistent Redis search sessions.
- 📦 Bounded Download Queue: workers, retry, cancellation и concurrency limits.
- 📚 `/playlist` и `/album` для URL-based playlist/album discovery через yt-dlp с пакетной очередью.
- ❤️ История, избранное, повторная загрузка.
- ⚙️ `/settings`: предпочтительный источник и качество.
- 📊 Метрики: requests, downloads, provider health, P50/P95/P99 latency.
- 🚨 Production health monitor с Telegram alert/recovery.
- 🛡️ Secret scan, input/path safety helpers, rate limits.
- 🚀 CI, preflight, release audit, deployment, backup и automatic rollback.
- 🎲 Подборки, чарты, похожие исполнители и групповые digest.

## Бесплатный сервис

VLMB полностью бесплатен. В проекте **нет монетизации, Premium, платежей или подписок**.

## Структура

```text
music_bot_user_mixes.py   # Telegram application / existing bot behavior
config.py                 # runtime configuration
services/
  provider_router.py       # failover + circuit breaker
  search_engine.py        # relevance ranking + dedup
  provider_health.py      # provider metrics
  metrics.py               # app metrics / latency
  download_queue.py        # bounded async queue
  playlist_manager.py     # playlist/album discovery
  security.py              # input/path safety
scripts/
  preflight.py
  healthcheck.py
  release_audit.py
  deploy_release.sh
  rollback_release.sh
  monitor.py
systemd/
  vlmb-musicbot.service
  vlmb-healthcheck.service
  vlmb-healthcheck.timer
.github/workflows/ci.yml
```

## Production requirements

- Ubuntu 24.04+
- Python 3.12+
- existing `/root/MusBot/venv`
- `/root/MusBot/.env` with `0600`
- SQLite databases are preserved by deployment
- Redis is recommended; local LRU fallback remains available

## Deployment

Use `README_DEPLOYMENT_QUICK.md` for the exact production procedure.

The deployment script validates the release before cutover, creates a backup, preserves secrets/data, restarts the service, runs healthcheck, verifies a single bot process, and enables the 5-minute health monitor.

## Development checks

```bash
python -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py
python -m pytest -q
python scripts/release_audit.py --ci
```

Expected release test result for 3.0.0:

```text
18 passed
Release audit OK
```
