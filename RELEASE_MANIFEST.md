# VLMB Music Bot 3.0.6

Native Telegram favorite callback UID fix on top of 3.0.5-fixed.

The downloaded-audio favorite action now uses a native callback query instead of a `t.me/...start=fav_...` URL. This avoids Telegram Desktop opening the bot with the deep-link text merely prefilled in the compose box.

## Included
- Search results remain clean: no per-track favorite symbols/buttons.
- Downloaded audio keeps a direct `❤️ Добавить в избранное` link to the bot.
- Standard Telegram `fav_<uid>` deep-link handling remains supported.
- Added a short-lived per-user pending-favorite fallback for Telegram clients that open the bot but emit plain `/start` without the deep-link payload.
- The fallback resolves only the user's own most recent downloaded track and is consumed once.
- Existing `/favorite` and `/favorites` commands remain supported.
- Provider Router, Search Engine 2.0, metrics, queue, playlist/album, settings, CI/CD, monitoring and security are preserved.

## Validation
- py_compile: PASS
- release audit: PASS
- secret scan: PASS
- favorite callback/pending-store regression tests: PASS in static validation; full pytest must be run in the project venv/server environment

## Policy
VLMB is free. No monetization, premium plans, payments or subscriptions are included.

## Verification

- Native downloaded-audio favorite action uses Telegram callback queries.
- No `t.me/...start=fav_...` URL is attached to downloaded audio.
- Regression suite contains 28 tests; the build environment used here does not include the bot's third-party runtime dependencies, so full pytest execution is delegated to the project's configured CI/server environment.
