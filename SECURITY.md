# VLMB Security Controls

## Secrets

- Production secrets live outside Git in `.env`.
- Bot/provider tokens must never be logged or committed.
- CI checks repository content for obvious secret exposure.

## Input and URL handling

- Validate user-controlled URLs before network access.
- Allow only explicitly supported media hosts where a direct host allowlist is required.
- Never construct filesystem paths directly from user-controlled filenames.
- Sanitize filenames before writing downloaded media.

## Resource exhaustion

- Bound download queue size.
- Bound worker count.
- Bound retry count and retry delay.
- Check available disk space before large writes.
- Do not perform unbounded in-memory buffering of provider results.

## Callback safety

- Callback namespaces are catalogued.
- Unknown callback prefixes fail the callback audit.
- State transitions are explicit and invalid transitions are tested.
- Extracted handlers must preserve existing callback semantics.

## Persistence

- Production SQLite databases are data, not release artifacts.
- Ordinary code deployment must not delete or overwrite production databases.
- Schema changes require an explicit migration plan and backup.

## Dependencies

Dependency upgrades require compatibility testing and security review. Do not upgrade the working dependency stack merely for version freshness.

## Incident handling

A security-relevant failure must be classified, logged without secrets, surfaced through an operational signal where appropriate, and covered by a regression test before the corresponding fix is considered complete.
