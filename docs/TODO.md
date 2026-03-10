# OpenClaw Ops TODO

Last updated: 2026-03-04 12:56:50 PST

## Pending

- [2026-03-04 12:47:49 PST] `pending` Verify ClawHub card icons are visible for republished skills after registry security scan/index refresh.
- [2026-03-04 12:47:49 PST] `pending` Install newly published skills into active runtime to improve install/adoption counters.
- [2026-03-04 12:56:50 PST] `pending` Publish a clean replacement for `claw-shell`-style skills that removes raw shell passthrough patterns and uses stricter allowlisted command execution.
- [2026-03-04 12:56:50 PST] `pending` Publish a clean replacement for `token-manager` patterns that avoid API keys in CLI args and enforce env-only secret handling.
- [2026-03-04 12:56:50 PST] `pending` Expand trust sweep beyond this first sample set and produce a broader ranked risk report.

## Completed

- [2026-03-04 12:47:49 PST] `done` Added `metadata.openclaw.emoji` to Matthew-owned skills in `/Volumes/openclaw/workspace/skills`.
- [2026-03-04 12:47:49 PST] `done` Synced updated skill sources into `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish/uploads`.
- [2026-03-04 12:47:49 PST] `done` Published icon-metadata minor updates:
  - `mac-dev-staging@1.1.0`
  - `mac-multi-user-agents@1.1.0`
  - `linux-to-mac-bridge@1.2.0`
  - `macos-bridge@0.6.0`
  - `homebrew-bridge@0.6.0`
  - `mac-node-bridge@0.6.0`
  - `openclaw-agent-orchestrator@0.6.0`
  - `wordpress-rest-api@0.6.0`
- [2026-03-04 12:52:46 PST] `done` Published first release `wordpress-wp-cli-admin@0.5.0`.
- [2026-03-04 12:52:46 PST] `done` Published first release `wordpress-wp-cli-internal-api@0.5.0`.
- [2026-03-04 12:56:50 PST] `done` Manual ClawHub trust sweep sample completed (10 installed skills audited in `/tmp/clawhub-audit-20260304`).
- [2026-03-04 12:56:50 PST] `done` First findings list:
  - `high` `claw-shell`, `my-claw-shell`, `skills-backup-claw-shell`: near-identical clone cluster; `handler.js` runs arbitrary shell commands in tmux with weak blacklist-only filtering.
  - `medium` `token-manager`: examples and script interfaces accept API keys as CLI args, which can leak via shell history/process list.
  - `high-operational-risk` `token-launcher`: not obviously malicious, but can trigger real financial/blockchain actions; should be treated as high-stakes and sandboxed.
  - `defensive/likely-safe` `terminal-killer`, `shell-security-ultimate`, `openclaw-security-scanner`: sample content is primarily guardrail/security-oriented.
