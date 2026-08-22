# 🎵 VLMB Music Bot 3.0.6

Асинхронный Telegram-бот для поиска и скачивания музыки из Яндекс.Музыки, VK и YouTube.

## Что есть в 3.0.6

- 🔎 **Search Engine**: нормализация, artist/title scoring и дедупликация результатов.
- 🏥 **Provider Router**: failover, классификация ошибок и circuit breaker primitives.
- ⚡ **Cache**: Redis + LRU и persistent search sessions.
- 📦 **Download Queue**: bounded async queue, workers, retry, cancellation и concurrency limits.
- 📚 **Playlists / Albums**: URL-based discovery через yt-dlp с пакетной очередью.
- ❤️ **История и избранное**: сохранение истории, избранных треков и повторная загрузка.
- ❤️ **Native favorite button**: после скачивания избранное добавляется через Telegram callback без открытия `/start`.
- 💔 **Remove from favorites**: кнопка переключается после успешного добавления.
- ⚙️ **Settings**: предпочтительный источник и качество.
- 📊 **Metrics**: requests, downloads, provider health и P50/P95/P99 latency.
- 🚨 **Health monitor**: production-проверки и Telegram alerts/recovery.
- 🛡️ **Security**: secret scan, input/path safety, rate limits и защита временных данных.
- 🚀 **CI / Deployment**: GitHub Actions, preflight, release audit, backup, healthcheck и automatic rollback.
- 🎲 **Discovery**: подборки, чарты, похожие исполнители и групповые digest.

## Бесплатный сервис

VLMB полностью бесплатен. В проекте **нет монетизации, Premium, платежей или подписок**.

## Структура

```text
music_bot_user_mixes.py   # Основное приложение и существующая логика Telegram-бота
config.py                 # Runtime-конфигурация
services/
  provider_router.py       # Failover + circuit breaker
  search_engine.py        # Ranking + dedup
  provider_health.py      # Состояние провайдеров
  metrics.py              # Метрики и latency
  download_queue.py       # Bounded async queue
  playlist_manager.py     # Playlist/album discovery
  security.py             # Проверки входных данных и путей
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
- production `.env` с секретами вне Git
- существующий runtime `/root/MusBot/venv`
- SQLite-данные сохраняются при deployment
- Redis рекомендуется; локальный LRU fallback остаётся доступным

## Deployment

Для production используйте `README_DEPLOYMENT_QUICK.md` и `DEPLOYMENT.md`.

Deployment script выполняет preflight/release validation, создаёт backup, сохраняет `.env` и данные, обновляет приложение, перезапускает systemd-сервис, выполняет healthcheck и при ошибке делает rollback.

## Проверки

Перед release рекомендуется выполнить:

```bash
python -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py tests/*.py
python -m pytest -q
python scripts/release_audit.py --ci
```

Для релиза 3.0.6 в репозитории находятся regression-тесты для provider failover, search engine, metrics, security, playlist manager, navigation и favorite callback/UID logic.

## Безопасность

Секреты не хранятся в Git. Используйте production `.env` на сервере и `.env.example` как шаблон. Файл `.env` исключён из репозитория.

Не добавляйте Telegram token, API keys, Redis credentials или другие production secrets в issues, commits, logs или архивы релиза.

## Git Source of Truth

Начиная с production release **3.0.6**, Git `master` является источником истины для production-кода. Production-релиз должен собираться из зафиксированного Git commit и проходить CI, release audit, preflight и healthcheck.

## Лицензия

MIT License
