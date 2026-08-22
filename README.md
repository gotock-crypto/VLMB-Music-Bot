# 🎵 VLMB Music Bot 3.0.6

**Асинхронный Telegram-бот для поиска и скачивания музыки** из Яндекс.Музыки, VK и YouTube.

VLMB ориентирован на стабильную production-работу: асинхронный поиск и загрузка, маршрутизация провайдеров с failover, кеширование, очередь загрузок, история и избранное, playlist/album discovery, метрики, healthcheck и безопасный деплой.

## Что нового в 3.0.6

- ❤️ Исправлена работа избранного для provider-prefixed UID (`vk:...`, `yt:...`, `ym:...`, `h:...`).
- ❤️ Кнопка избранного после скачивания работает через нативный Telegram callback.
- 🔁 После добавления в избранное кнопка меняется на «💔 Убрать из избранного».
- 🧩 Обработчик использует точный UID из истории/избранного и не преобразует его в другой hash UID.
- 🛡️ Сохранены legacy deep-link и pending-favorite fallback для совместимости.
- 🧪 Добавлены regression-тесты для VK-prefixed и hash UID.

## Основные возможности

- 🔎 Поиск по названию трека или исполнителю.
- 🎵 Источники: Яндекс.Музыка, VK и YouTube через `yt-dlp`.
- 🧠 Search Engine: нормализация, artist/title scoring и дедупликация.
- 🏥 Provider Router: классификация ошибок, circuit breaker и failover.
- ⚡ Redis + LRU cache и persistent search sessions.
- 📦 Bounded Download Queue: workers, retry, cancellation и concurrency limits.
- 📚 `/playlist` и `/album` для URL-based discovery с пакетной очередью.
- ❤️ История, избранное и повторная загрузка.
- ⚙️ `/settings` для выбора предпочтительного источника и качества.
- 📊 Метрики запросов, загрузок, состояния провайдеров и P50/P95/P99 latency.
- 🚨 Production health monitor с уведомлениями об ошибках и восстановлении.
- 🛡️ Secret scan, input/path safety и rate limits.
- 🚀 Preflight, healthcheck, release audit, backup и automatic rollback.
- 🎲 Подборки, чарты, похожие исполнители и групповые digest.

## Бесплатный сервис

VLMB полностью бесплатен. В проекте **нет монетизации, Premium, платежей или подписок**.

## Структура

```text
music_bot_user_mixes.py   # Основное приложение и существующая логика бота
config.py                 # Runtime-конфигурация
services/
  provider_router.py       # Failover + circuit breaker
  search_engine.py        # Ranking + dedup
  provider_health.py      # Состояние провайдеров
  metrics.py              # Метрики и latency
  download_queue.py       # Асинхронная очередь загрузок
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
- SQLite/Redis данные сохраняются при деплое
- Redis рекомендуется; локальный LRU fallback остаётся доступным

## Установка и запуск

```bash
git clone https://github.com/gotock-crypto/VLMB-Music-Bot.git
cd VLMB-Music-Bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python music_bot_user_mixes.py
```

## Production deployment

Для продакшена используйте `README_DEPLOYMENT_QUICK.md` и `DEPLOYMENT.md`.

Deployment script выполняет preflight/release validation, создаёт backup, сохраняет `.env` и данные, обновляет приложение, перезапускает systemd-сервис, запускает healthcheck и при ошибке выполняет rollback.

## Проверки

```bash
python -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py
python -m pytest -q
python scripts/release_audit.py --ci
```

Для версии 3.0.6 добавлены отдельные regression-тесты для callback/pending-favorite логики и provider-prefixed UID.

## Безопасность

Секреты не хранятся в Git. Используйте `.env` на сервере и `.env.example` как шаблон. Файл `.env` исключён из репозитория.

## Лицензия

MIT License
