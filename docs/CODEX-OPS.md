# Codex Ops Memory

This file is the compact memory for future OpenClaw work in this directory.

## Mission

Use Codex on the OpenClaw project to make the Linux gateway, Mac nodes, skills, and publishing workflow work together cleanly and repeatably.

## Stable Assumptions

- Shared gateway remains on the Ryzen host.
- Mac nodes are helpers, not replacement gateways.
- Publish reusable skills instead of patching OpenClaw core whenever possible.
- Prefer Linux gateway + Mac node bridge patterns over pretending Linux directly owns macOS tooling.
- New public projects should start at `0.5.0`.
- For public skill releases, small updates should use minor bumps rather than patch bumps.

## Current Important Paths

- Workspace root: `/Volumes/openclaw`
- Local ops root:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops`
- SkillArmor static site root:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/skillarmor-site`
- Skill source folders:
  - `/Volumes/openclaw/workspace/skills/mac-dev-staging`
  - `/Volumes/openclaw/workspace/skills/mac-multi-user-agents`
  - `/Volumes/openclaw/workspace/skills/linux-to-mac-bridge`
  - `/Volumes/openclaw/workspace/skills/macos-bridge`
  - `/Volumes/openclaw/workspace/skills/homebrew-bridge`
  - `/Volumes/openclaw/workspace/skills/mac-node-bridge`
  - `/Volumes/openclaw/workspace/skills/openclaw-agent-orchestrator`
  - `/Volumes/openclaw/workspace/skills/wordpress-rest-api`
  - `/Volumes/openclaw/workspace/skills/wordpress-wp-cli-admin`
  - `/Volumes/openclaw/workspace/skills/wordpress-wp-cli-internal-api`
- ClawHub upload pack:
  - `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish`
- GitHub repo pack:
  - `/Volumes/MacHome/Users/mmurphy/Desktop/github-publish`
- Local-only token env:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/.local-secrets/clawhub.env`

## Current Cluster Summary

- Gateway:
  - host: Ryzen Ubuntu
  - URL: `http://192.168.88.11:18789`
- Control machine:
  - `Mac mini M4 Pro`
  - browser/dashboard only under the primary user
  - do not treat it as a node
  - if local OpenClaw is ever needed later, use a separate macOS user
- Intended nodes:
  - `Mac mini M1 16GB`
  - `MacBook Pro M3 Max`
- Managed browser path is the correct path for unattended agent work on the Macs.
- Extension relay problems are secondary; do not confuse them with managed browser readiness.

## Current Runtime Status

As of March 4, 2026:

- Gateway port `18789` is bound and reachable.
- Gateway health now returns `ok: true`.
- The gateway is currently running as the Docker container `openclaw-openclaw-gateway-1`, not as a local systemd gateway service.
- The heartbeat model was changed from the blocked local Phi 3.5 profile to `openrouter/auto`.
- The M4 control machine should not be part of the runtime under the primary user.
- `node.list` currently shows both intended macOS nodes as paired and connected:
  - `Mac mini M1 16GB` (`displayName: M1`)
  - `MacBook Pro M3 Max` (`displayName: MacBook Pro`)

Current operational notes:

1. The old `openclaw.local` hostname was not resolvable from the Mac and was one root cause of the false unhealthy state.
2. The gateway required both the live gateway token and device pairing; fixing only one of those was not enough.
3. The stale `openclaw-node.service` on the Ryzen is not the active gateway path for port `18789`.
4. Gateway health is green now, but the Docker-backed gateway layout should be treated as the source of truth for future changes.
5. Do not install or run OpenClaw under the primary user on the `Mac mini M4 Pro`; keep that machine as the control center only.
6. Browser/dashboard token mismatches are a separate control UI problem and should not be treated as node outages when `node.list` is green.

## ClawHub Analytizer Status (March 4, 2026)

- Dashboard path:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/dashboard/browser.html`
- Latest behavior:
  - Left icon rail uses Font Awesome 52x icons with live counters.
  - Theme selector supports `auto`, `dark`, `light` (auto follows system theme).
  - Owner rows use live GitHub AJAX lookups plus local findings summary.
  - Threat banner is runtime-stateful:
    - `Healthy` only when runtime is healthy with no high/critical runtime signals.
    - `Degraded` when fallback is active.
    - `Blocked` when runtime health is false.

### Runtime Signal Semantics

- `api_access_blocked`:
  - upstream Cloudflare/WAF blocked request (HTTP 403 / error 1010), not a bad API key by itself.
- `api_permission_denied`:
  - API key scope/permissions denied (HTTP 403 without Cloudflare/WAF markers).
- `api_auth_failed`:
  - invalid/unauthorized credentials (HTTP 401).
- `fallback_ryzen_gpu_used`:
  - primary API failed and local Ryzen fallback model completed.
- `fallback_connection_error`:
  - fallback endpoint unreachable (current observed state when Ryzen model service is down).

### Runtime Display Policy

- Dashboard should prioritize one clear line: active engine + model.
- Runtime alerts should be action-focused:
  - show only blocking/high/critical issues in the Runtime panel
  - suppress informational noise (for example local-primary or coverage-ingested notices)
- If Ryzen local scan is healthy, upstream Big-Pickel API blocking should not be treated as a blocking runtime alert.

## Comment Queue Policy

- Use two write-up POVs per queued skill:
  1. safety/runtime POV
  2. maintainer/quality POV
- Include legitimacy checks explicitly in POV 2:
  - GitHub profile resolution
  - public repo/follower/public activity signals
  - profile completeness (bio/name/etc.)
  - SKILL.md evidence presence
  - visible version count
- Queue file:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/comment-post-queue.json`
- Markdown output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/docs/COMMENTS.md`
- Slow posting cadence:
  - process at most one queued item per run unless explicitly increased
  - default schedule: every 30 minutes via cron runner

### Fallback Runtime

- Scanner script now auto-attempts Ryzen fallback on primary API failure:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/run-big-pickel-scan.py`
- Default fallback config:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/big-pickel-search-config.json`
  - provider: `auto`
  - endpoint auto-discovery across Ryzen ports
  - current endpoint: `http://192.168.88.11:1234/v1/chat/completions`
  - current model: `Phi-3.5-mini-instruct.Q8_0.gguf`

### Coverage Source

- Analytizer now merges three sources:
  - local cached audit findings
  - Big-Pickel/fallback findings
  - direct ClawHub public index pagination (`/api/v1/skills`)
- Coverage can scale into the thousands even when Big-Pickel is blocked by Cloudflare.

## Skill Intent

- `mac-dev-staging`
  - Mac local dev/staging stack
  - Apache + PHP 8.5 + MariaDB + SFTP + npm tooling
  - optional nginx
  - local dev controller/gateway coexistence

- `mac-multi-user-agents`
  - use one powerful Mac as a multi-user agent host
  - recommend safe agent count from hardware
  - create agent users with repeatable commands

- `linux-to-mac-bridge`
  - Linux gateway wrappers for Mac-backed business tools
  - publishable readiness pattern without patching core

- `macos-bridge`
  - Linux gateway wrappers for macOS-owned tools like `imsg` and `remindctl`
  - same-LAN bridge skill for Mac-native capabilities

- `homebrew-bridge`
  - Linux gateway access to a Mac node's Homebrew toolchain
  - publishable wrapper skill for `/opt/homebrew/bin` tools

- `mac-node-bridge`
  - generic Linux-to-macOS bridge pattern
  - stable SSH wrapper base when a gateway needs a Mac node

- `openclaw-agent-orchestrator`
  - verified durable-agent creation and runtime repair
  - use `openclaw agents add`, not `sessions_spawn`, for durable subagents

- `wordpress-rest-api`
  - WordPress `/wp-json` route discovery, auth, and live endpoint inspection
  - publishable API-context skill for OpenClaw and ClawHub

- `wordpress-wp-cli-admin`
  - WordPress shell-side admin, maintenance, and content workflows via `wp`
  - publishable admin-context skill for OpenClaw and ClawHub

- `wordpress-wp-cli-internal-api`
  - WP-CLI custom command and package development against the stable internal API
  - publishable developer-context skill for OpenClaw and ClawHub

## Rules For Future Changes

- Keep secrets out of skill folders and repo packs.
- Keep release metadata in the Desktop publish packs.
- If a skill changes publicly, update the ClawHub and GitHub packs together.
- Do not count `ai-persona-os` as Matthew's skill inventory; it is third-party.
- Do not route ClawHub publish work through Taylor by default.
- If Taylor says ClawHub CLI is unavailable, treat that as a runtime limitation for Taylor, not as a token failure.
- Stage missing skills into `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish/uploads` and update `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish/RELEASES.md` before attempting live publish.
- Do not guess publish/install commands for ClawHub. Verify the current official surface first.
- Use `0.x.0` style minor progression for new public releases until a project earns `1.0.0`; after `1.0.2`, the next small `linux-to-mac-bridge` release should still be `1.1.0`.
- If future community authority matters, prefer clean naming and examples over one-off hacks.
- Do not treat "port reachable" as equivalent to "paired and runtime healthy".
- Do not assume the Ryzen gateway is managed by systemd just because `openclaw gateway status` is available; check Docker first.

## Unified Exec Cap Handling

If the runtime reports:

- `The maximum number of unified exec processes ... currently have N processes open`

Use this sequence:

1. Stop obvious runaway shell tasks first (for example long-lived `grep -R` scans).
2. Avoid creating fresh background loops from chat turns; reuse existing runners/sessions.
3. Run session maintenance:
   - `openclaw sessions cleanup`
4. If warnings continue, restart only the gateway container:
   - `docker restart openclaw-openclaw-gateway-1`
5. Re-check health:
   - `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1 openclaw health --json`

Notes:

- This warning is usually in-memory runtime pressure, not `sessions.json` size.
- Keep heartbeat enabled only where needed; avoid layered cron/loop automations that duplicate each other.

## SkillArmor Publish Cadence

- Feed exporter:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/export-skillarmor-feed.py`
- Feed output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/skillarmor-site/data/skillarmor-feed.json`
- Remote publish script:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/publish-skillarmor-feed.sh`
- Twice-daily cron:
  - `0 */12 * * * /bin/bash "/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/skillarmor-publish-cron.sh"`

## Vhost Manager

- Project plan:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/vhost-projects.json`
- Remote deploy config:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/vhost-deploy-config.json`
- Generator/deployer script:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/manage-vhosts.py`
- Generated nginx output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/output/vhosts/nginx`
- Dashboard UI section:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/dashboard/browser.html` (`Vhost Manager`)

## CTO Ops Dashboard

- Config:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/cto-ops-config.json`
- Snapshot output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/cto-ops-snapshot.json`
- Scan runner:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/cto-ops-scan.py`
- Dashboard:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/dashboard/cto-dashboard.html`
- Hourly cron:
  - `0 * * * * /bin/bash "/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/cto-ops-cron.sh"`

Current known blocker:

- OCI profile `DEFAULT` still returns `NotAuthenticated (401)` even though local key/fingerprint match.
- This indicates the API key must be re-authorized/rotated in OCI user settings before live provisioning can proceed.
