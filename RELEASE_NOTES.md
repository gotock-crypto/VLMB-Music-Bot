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
