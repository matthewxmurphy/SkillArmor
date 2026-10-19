# Changelog

## Unreleased — queue durability follow-up 2026-10-18

- Synchronize the queue parent directory after atomic replacement; abort before adapter execution if the claim durability barrier fails.
- Treat whitespace-only adapter receipt IDs as uncertain and preserve usable opaque IDs exactly.
- Add local ordering, injected sync-failure and blank-receipt regressions; no real posting or power-loss acceptance is claimed.

## Unreleased — queue identity maintenance 2026-10-18

- Select repeated source IDs once and apply the queue limit to unique findings.
- Reject duplicate or invalid durable identities before any claim or adapter
  execution, preserving conflicting attempts and receipts for owner reconciliation.
- Keep posting disabled by default; this source checkpoint performs no delivery,
  production change or version release.


## Unreleased — source security maintenance2026-10-16

- Fix APP-06; see docs/SECURITY-BOUNDARIES.md for configuration/compatibility and test limits.
- No production deployment or release-version change.

- Security follow-up: freeze adapter program/script/option positions; allow only named data fields and a private comment-file channel. Legacy free-form templates now fail closed.
