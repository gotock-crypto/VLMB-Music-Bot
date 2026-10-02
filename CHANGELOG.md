# Changelog

## 3.0.4 — favorite deep-link reliability

- kept the clean search-result UI without per-track favorite buttons;
- kept `❤️ Добавить в избранное` as a direct link on downloaded audio;
- added a short-lived SQLite-backed pending favorite for Telegram clients that deliver plain `/start` after opening the bot link;
- pending favorite is tied to the same user, expires after 5 minutes and is consumed once;
- standard `fav_<uid>` deep-link payload remains supported;
- added regression tests for pending-favorite storage/expiry.

**VLMB remains fully free. No monetization, premium, payments or subscriptions are included.**

## 3.0.0 — complete service release

- added Provider Router with classified failures and circuit-breaker cooldowns;
- upgraded search ranking to relevance scoring, artist/title matching and cross-provider deduplication;
- added application metrics with search/provider latency P50/P95/P99;
- added bounded Download Queue with workers, retries and cancellation;
- added playlist/album URL discovery and batch queueing through yt-dlp;
- added `/settings` and user-selectable provider preference;
- expanded private-chat navigation with History, Favorites and Settings;
- added security helpers for filenames, paths and media URLs;
- expanded regression suite to 18 tests;
- deployment now installs/enables the recurring health monitor automatically.

**VLMB remains fully free. No monetization, premium, payments or subscriptions are included.**


## Production safety/refactor release

- Removed hard-coded Telegram/Yandex/Last.fm secrets from `config.py`; runtime secrets are environment-only.
- Added `.env.example`, `.gitignore`, and a systemd unit using `EnvironmentFile`.
- Disabled propagation of `httpx`/`httpcore` request logs so Telegram bot tokens cannot appear in normal HTTP logs.
- Added provider search/download health metrics without changing provider fallback behavior.
- Extracted the existing artist-first ranking rule into `services/search_scoring.py` with regression tests.
- Added read-only `preflight.py` and `healthcheck.py` for production validation.
- Added rollback-safe deployment instructions that explicitly preserve SQLite/Redis data.
- Added regression tests for ranking, provider metrics, source syntax, and secret hygiene.

No database schema migration or destructive data operation is introduced by this release.

## 2026-08-22 — deployment reliability fix

- fixed preflight to read required environment variables from an explicit production `.env` without printing secret values;
- fixed automatic rollback so it no longer deletes the production virtualenv that is intentionally excluded from backups;
- fixed rollback to restore only the backed-up application tree while preserving production `.env`, SQLite databases, logs and `venv`;
- deployment now validates the release before stopping the running bot;
- deployment updates Python dependencies before the cutover;
- deployment now performs automatic rollback after cutover failures and verifies a single running bot process;
- added regression tests for deployment/rollback safety.

## 2026-08-22 — full-service foundation

- added GitHub Actions CI for compile, regression and release/security audit checks;
- added deterministic `scripts/release_audit.py`;
- added production `scripts/monitor.py` with failure/recovery Telegram notifications;
- added systemd healthcheck service/timer for recurring production monitoring;
- documented the release manifest and explicit no-monetization policy;
- retained existing provider fallback, Redis/local cache fallback, rate limiting, bounded download workers, user history/repeat and group mix/digest functionality.

## 3.0.2 - 2026-08-22
- UX polish for search result keyboards and compact favorite actions.
- Default search page reduced to 8 tracks.
- Cleaner action grouping and result header.

## 3.0.3

- Убраны кнопки избранного из списка результатов поиска.
- После успешного скачивания аудио добавляется кнопка-ссылка «❤️ Добавить в избранное» на deep link бота.
- Deep link `fav_<uid>` добавляет скачанный трек из истории пользователя в избранное.
- Навигация избранного не зависит от callback-кнопок в поисковой выдаче.
