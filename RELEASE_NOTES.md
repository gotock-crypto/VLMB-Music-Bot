## RC3 PostgreSQL compatibility correction

- PostgreSQL adapter now preserves explicit write transaction boundaries: DML remains pending until `commit()`, `rollback()`, or connection close; uncommitted writes are rolled back on close.
- Added offline regression tests for commit and rollback behavior.
- Live PostgreSQL integration and production migration remain unverified and are required before deployment.

# VLMB 4.0.0-rc2-postgresql — Release Notes

## PostgreSQL migration hardening

- Widened SQLite `INTEGER` declarations to PostgreSQL `BIGINT` in the runtime compatibility adapter, preserving Telegram IDs and counters.
- Fixed generated-ID retrieval for `group_digest_subscriptions` inserts.
- Made placeholder conversion safe around quoted strings and SQL comments.
- Applied generic `ON CONFLICT DO NOTHING` translation for SQLite `INSERT OR IGNORE`.
- Fail closed for unsupported `INSERT OR REPLACE` tables rather than silently changing semantics.
- Avoided sequence-reset errors for tables whose `id` column is not sequence-backed.
- Added offline adapter regression tests.

## Validation status

- Python syntax checks passed.
- Focused PostgreSQL adapter and migration unit tests passed.
- SQLite migration dry-run passed against both source database files extracted from the supplied archive.
- Live PostgreSQL migration, data-count comparison on the production databases, and Telegram end-to-end smoke tests have not been run. Do not cut over until PostgreSQL is installed/configured and those checks pass.

## Favorite callback UID fix

- Fixed the native favorite callback for provider-prefixed track IDs.
- Callback data now preserves the exact stored UID (`vk:...`, `yt:...`, `ym:...`, or `h:...`) instead of stripping `:` and accidentally converting it into a different hash UID.
- The callback handler now looks up and removes favorites using the exact UID stored in `user_history`/`user_favorites`.
- Added regression coverage for VK-prefixed and hash UIDs.

# VLMB 3.0.6 Release Notes

## Favorite action fix

- Replaced the downloaded-audio `t.me` favorite deep-link button with a native Telegram callback button.
- Clicking **❤️ Добавить в избранное** now sends a callback directly to the bot; no compose box, `/start`, or manual sending is involved.
- After adding, the button changes to **💔 Убрать из избранного**.
- Uses the user's existing download history to resolve the exact track.
- Kept `/favorite`, `/favorites`, and the legacy deep-link/pending-favorite fallback for compatibility.


## Favorites link reliability
- Kept the clean search-result UI without per-track favorite buttons.
- Kept `❤️ Добавить в избранное` as a link on downloaded audio.
- Added a short-lived SQLite-backed pending favorite record when an audio file is successfully delivered.
- If Telegram preserves `?start=fav_<uid>`, the bot uses the exact track UID from the user's history.
- If Telegram Desktop/client opens the bot but sends plain `/start`, the bot consumes the pending favorite created immediately before the link was opened.
- Pending favorites expire after 5 minutes and are consumed once.
- Existing `/favorite` and `/favorites` commands remain unchanged.

## Stability
- No secrets or track metadata are placed into the URL.
- Existing provider router, search engine, queue, playlist/album, metrics, security, deployment and monitoring are preserved.

## Free-service policy
VLMB remains fully free. No monetization, premium plans, payments or subscriptions are included.
