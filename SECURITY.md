# VLMB Security Controls

- Production secrets remain outside Git in `.env`.
- User-controlled URLs are validated before network access.
- User-controlled filenames are sanitized before filesystem writes.
- Download queue size, worker count and retry count are bounded.
- Disk-space checks protect large media writes.
- Callback namespaces are catalogued and audited.
- State transitions are explicit and invalid transitions are tested.
- Production SQLite databases are data, not release artifacts.
- Schema changes require backup and an explicit migration plan.
- Structured events redact common credential-bearing fields.
- Dependency changes require compatibility testing and security review.

Security-relevant fixes require a regression test and safe operational signal.
