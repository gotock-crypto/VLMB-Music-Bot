# 🎵 VLMB Music Bot 4.0.0-rc2

Асинхронный Telegram-бот для поиска и скачивания музыки из Яндекс.Музыки, VK и YouTube.

> **Статус:** `4.0.0-rc2` — Architecture & Reliability Release Candidate.
>
> Production уже работает на RC2. 4.0 сохраняет поэтапный архитектурный рефакторинг: `music_bot_user_mixes.py` остаётся compatibility bootstrap, а новые границы вводятся постепенно с обязательными тестами.

## Что есть в 4.0.0-rc2

### Пользовательские возможности

- 🔎 **Search Engine**: нормализация, artist/title scoring и дедупликация результатов.
- 🎵 **Music providers**: Яндекс.Музыка, VK и YouTube.
- ❤️ **История и избранное**: сохранение истории, избранных треков и повторная загрузка.
- ❤️ **Native favorite callback**: добавление в избранное непосредственно через Telegram callback без возврата в `/start`.
- 💔 **Remove from favorites**: кнопка меняется после успешного добавления.
- 👥 **Discovery**: похожие исполнители, подборки и чарты.
- 📚 **Playlists / Albums**: URL-based discovery с пакетной обработкой.
- ⚙️ **Settings**: предпочтительный источник и качество.

### Reliability & Production

- 🧭 **Callback / State Audit**: каталог callback namespaces и проверка регистрации callback-префиксов.
- 🧠 **State Machine**: формализованные критические state transitions.
- 🔌 **Provider Adapters**: единый интерфейс `search()`, `download()` и `health()` для provider implementations.
- 🏥 **Provider Router**: failover, error classification и circuit-breaker primitives.
- 📦 **Download Queue**: bounded async queue, workers, retry, cancellation, idempotent submission и graceful shutdown.
- ⚡ **Cache**: Redis + LRU fallback и persistent search sessions.
- 📊 **Metrics**: request/download metrics, provider health и P50/P95/P99 latency.
- 🚨 **Health Monitor**: production healthchecks и recovery alerts.
- 🛡️ **Security**: secret scan, input/path safety, rate limits и защита временных данных.
- 🚀 **CI / Deployment**: GitHub Actions, preflight, release audit, artifact integrity, backup, healthcheck и rollback flow.
- 🔬 **Architecture Audit**: проверка границ `application / domain / providers / storage`.
- 🧪 **Critical-flow tests**: callback/state contracts, provider adapters, queue/load smoke и rollback drill tests.

## Архитектура 4.0

```text
Telegram / bot handlers
        |
        v
application
  commands / callbacks / state
        |
        v
domain
  models / policies / errors
     |             |
     v             v
 providers       storage
   |               |
   v               v
 YM / VK / YT   SQLite / session state
```

Ключевое правило миграции: каждая новая выделенная ответственность получает тесты до удаления старой реализации. Основной `music_bot_user_mixes.py` пока остаётся compatibility bootstrap.

## Структура

```text
music_bot_user_mixes.py   # Compatibility bootstrap + существующая Telegram-логика
config.py                 # Runtime-конфигурация
application/
  callbacks/              # Callback catalog + audit
  state/                  # State machine / transitions
  use_cases/              # SearchMusic / DownloadTrack

domain/
  models.py               # Domain models
  errors.py               # Domain errors
  track_info.py           # Canonical track identity
providers/
  base.py                 # Единый provider contract
  adapters.py             # Provider adapters
storage/
  contracts.py            # Storage/session contracts
services/
  provider_router.py      # Failover + circuit breaker
  provider_health.py      # Состояние провайдеров
  metrics.py              # Метрики и latency
  download_queue.py       # Bounded async queue
  search_engine.py        # Ranking + dedup
  playlist_manager.py     # Playlist/album discovery
  security.py             # Проверки входных данных и путей
  structured_logging.py   # Safe structured events
scripts/
  preflight.py
  healthcheck.py
  release_audit.py
  release_artifact_audit.py
  callback_audit.py
  architecture_audit.py
  load_test_queue.py
  rollback_drill.py
  deploy_release.sh
  rollback_release.sh
  monitor.py
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

Deployment flow:

```text
backup
  ↓
preflight / release audit
  ↓
install / update
  ↓
systemd restart
  ↓
healthcheck
  ↓
SUCCESS
```

При ошибке deployment выполняется rollback к предыдущему рабочему release. Перед каждым release backup сохраняется до завершения проверки.

## Проверки

Локально или в CI рекомендуется выполнить:

```bash
python -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py application/use_cases/*.py domain/*.py providers/*.py storage/*.py
python -m pytest -q
python scripts/release_audit.py --ci
python scripts/callback_audit.py
python scripts/architecture_audit.py
python scripts/release_artifact_audit.py
python scripts/load_test_queue.py --jobs 100 --concurrency 10 --work-ms 20
python scripts/rollback_drill.py
```

## Безопасность

Секреты не хранятся в Git. Используйте production `.env` на сервере и `.env.example` как шаблон. Файл `.env` исключён из репозитория.

Не добавляйте Telegram token, API keys, Redis credentials или другие production secrets в issues, commits, logs или архивы релиза.

## Бесплатный сервис

VLMB полностью бесплатен. В проекте **нет монетизации, Premium, платежей или подписок**.

## Git Source of Truth

`master` является источником истины для production-кода. Production-релиз должен собираться из зафиксированного Git commit и проходить CI, release audit, preflight и healthcheck.

Текущий release candidate:

```text
VLMB 4.0.0-rc2
```

## Лицензия

MIT License
