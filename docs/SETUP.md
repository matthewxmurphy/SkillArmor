# OpenClaw Setup

This file is the local runbook for the current OpenClaw cluster and publishing workflow.

## Release Versioning Policy

- Use major/minor progression for public skill releases.
- Start new public projects at `0.5.0`, not `1.0.0`.
- Treat any small public update as a minor bump, not a patch bump.
- Example early progression: `0.5.0` -> `0.6.0` -> `0.7.0`.
- Use `1.0.0` only once the project feels like a real milestone release.
- Use the next major version only when the skill crosses a larger milestone, packaging reset, or intentionally breaking public change.
- The currently published `linux-to-mac-bridge` release is `1.0.2`; under this policy, the next small update should be `1.1.0`.

## Current Cluster

- Primary shared gateway: `http://192.168.88.11:18789`
- Gateway host: Ryzen Ubuntu box
- Gateway auth token: stored locally, see `/.local-secrets/clawhub.env` for ClawHub token only and the gateway runtime config on the Ryzen for the gateway token
- Control machine:
  - `Mac mini M4 Pro`
  - browser/dashboard only under the primary user
  - not a node
  - if local OpenClaw is ever needed later, use a separate macOS user
- Intended macOS nodes:
  - `Mac mini M1 16GB`
  - `MacBook Pro M3 Max`

## Current Gateway Runtime Status

Status as of March 4, 2026:

- Gateway port `18789` is bound and reachable.
- Gateway health returns `ok: true`.
- The live gateway on the Ryzen is the Docker container `openclaw-openclaw-gateway-1`.
- The heartbeat model is now `openrouter/auto` instead of the blocked local Phi 3.5 configuration.
- The `Mac mini M4 Pro` should not participate in OpenClaw runtime work under the primary user.
- `node.list` on the Ryzen currently shows both intended nodes as paired and online.

Current repair notes:

1. The old `ws://openclaw.local:18789` client target was stale and caused tunnel and probe failures.
2. The gateway required the live gateway token plus device pairing approval.
3. The gateway on port `18789` was healthy in Docker even while `openclaw gateway status` on the host looked stale or inactive.
4. Keep the M4 primary user free of OpenClaw runtime state; if local automation is needed later, create a dedicated macOS user instead.

## Current Node Roles

- `Mac mini M1 16GB`
  - intended always-on macOS node
  - fresh OS / fresh dedicated account
  - managed OpenClaw browser works
  - iMessage relay host for the gateway
  - intended home for always-on Mac-native tools
  - currently online in the Ryzen node list

- `MacBook Pro M3 Max`
  - intended heavier macOS node
  - use a separate agent user, not the personal daily-use account
  - managed OpenClaw browser works
  - shared Homebrew/OpenClaw path standardized to `/opt/homebrew/bin`
  - intended home for heavier browser, terminal, and staging work
  - currently online in the Ryzen node list

- `Mac mini M4 Pro`
  - control center only
  - use it to view/control dashboards and other systems
  - do not run OpenClaw runtime work under the primary user

## Current Skill Projects

Workspace skill source folders:

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

Do not count `ai-persona-os` as Matthew's skill. It is a third-party skill in the workspace, not part of Matthew's publish inventory.

These are the active publishable skills built in this project.

## Current Publish Packs On The M4 Desktop

ClawHub upload pack:

- `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish`

GitHub repo pack:

- `/Volumes/MacHome/Users/mmurphy/Desktop/github-publish`

Release sheets:

- `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish/RELEASES.md`
- `/Volumes/MacHome/Users/mmurphy/Desktop/github-publish/GITHUB-REPOS.md`

## Current Publish Metadata

### 1. Mac Dev Staging

- slug: `mac-dev-staging`
- display name: `Mac Dev Staging`
- version: `1.0.0`

### 2. Mac Multi User Agents

- slug: `mac-multi-user-agents`
- display name: `Mac Multi User Agents`
- version: `1.0.0`

### 3. Linux to Mac Bridge

- slug: `linux-to-mac-bridge`
- display name: `Linux to Mac Bridge`
- version: `1.1.0`

### 4. macOS Bridge

- slug: `macos-bridge`
- display name: `macOS Bridge`
- version: `0.5.0`

### 5. Homebrew Bridge

- slug: `homebrew-bridge`
- display name: `Homebrew Bridge`
- version: `0.5.0`

### 6. Mac Node Bridge

- slug: `mac-node-bridge`
- display name: `Mac Node Bridge`
- version: `0.5.0`

### 7. OpenClaw Agent Orchestrator

- slug: `openclaw-agent-orchestrator`
- display name: `OpenClaw Agent Orchestrator`
- version: `0.5.0`

### 8. WordPress REST API

- slug: `wordpress-rest-api`
- display name: `WordPress REST API`
- version: `0.5.0`

### 9. WordPress WP-CLI Admin

- slug: `wordpress-wp-cli-admin`
- display name: `WordPress WP-CLI Admin`
- version: `0.5.0`

### 10. WordPress WP-CLI Internal API

- slug: `wordpress-wp-cli-internal-api`
- display name: `WordPress WP-CLI Internal API`
- version: `0.5.0`

## Local Ops Files

- Local ops root:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops`
- Local runbook:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/SETUP.md`
- Local Codex memory:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/CODEX-OPS.md`

## ClawHub

- A local ClawHub CLI token has been saved in:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/.local-secrets/clawhub.env`
- Treat that file as local-only.
- Do not commit it, upload it, screenshot it, or copy it into skills.
- Because the token was exposed in chat, rotate it after you finish the immediate publish work.

## ClawHub Publish Rules

- Do not route ClawHub publishing through Taylor by default.
- Taylor's runtime may not have the ClawHub CLI or the right local publish environment; that is a runtime limitation, not proof the token is bad.
- Stage publishable skills in:
  - `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish/uploads`
- Track released and queued versions in:
  - `/Volumes/MacHome/Users/mmurphy/Desktop/clawhub-publish/RELEASES.md`
- If publish tooling is unavailable in the current runtime, sync the upload pack and changelog locally first instead of guessing commands.
- Do not guess the publish command or invent install instructions. Verify the current ClawHub/OpenClaw publish surface first.

## Notes For Future Sessions

- The mixed Linux/macOS pattern should be solved with publishable skills, not OpenClaw core patching.
- `linux-to-mac-bridge` is the reusable answer for Linux gateway to Mac tool readiness.
- `mac-dev-staging` is the reusable answer for a Mac staging/server-like local dev box.
- `mac-multi-user-agents` is the reusable answer for one powerful Mac hosting several isolated agent users.
- `macos-bridge`, `homebrew-bridge`, `mac-node-bridge`, and `openclaw-agent-orchestrator` are part of Matthew's publish inventory and should be kept in the ClawHub upload pack.
- The `MacBook Pro M3 Max` is the correct target for the multi-user agent pattern.
- The `Mac mini M4 Pro` is the control center and should stay browser-only under the primary user.
- The WordPress skill set is now split into REST API, WP-CLI admin, and WP-CLI internal API packages for ClawHub.
- The Desktop ClawHub upload pack should contain all of Matthew's publishable skills, not just the three already live skills.
- New public projects should begin at `0.5.0`, and small public changes after that should keep using minor-only bumps instead of patch bumps.
- Do not confuse gateway reachability with successful pairing; earlier this was the root cause, but pairing is now repaired.
- On the Ryzen box, treat Docker as the active gateway control plane before touching systemd user units.
- If the router issue is still unresolved, do not reset MikroTik in the middle of cluster work.

## ClawHub Analytizer UI + Runtime Notes

- Dashboard:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/dashboard/browser.html`
- Current UI features:
  - left icon rail with Font Awesome `52x52` icons and live counters.
  - theme mode selector: `auto` / `dark` / `light`.
  - larger owner visuals with emoji + avatar.
  - owner line enrichment via GitHub AJAX + local finding summary.
  - runtime-state banner that shows `Healthy`, `Degraded`, or `Blocked` instead of static "active".

### Scan Runtime Fallback

- Scanner:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/run-big-pickel-scan.py`
- If primary Big-Pickel API fails, scanner auto-attempts Ryzen fallback model.
- Fallback config:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/big-pickel-search-config.json`
  - provider `auto` (endpoint auto-discovery)
  - host `http://192.168.88.11`
  - current endpoint `http://192.168.88.11:1234/v1/chat/completions`
  - model `Phi-3.5-mini-instruct.Q8_0.gguf`
- Scan policy mode (`scanMode`):
  - `prefer_local` (default): local Ryzen first, API skipped when local works
  - `local_only`: no API calls, fail if local unavailable
  - `api_first`: legacy behavior (API then local fallback)
- Current observed runtime (March 4, 2026):
  - primary API blocked by Cloudflare/WAF (`api_access_blocked`)
  - fallback auto-repaired to Ryzen OpenAI-compatible endpoint (`fallback_ryzen_gpu_used`)
  - active fallback endpoint: `http://192.168.88.11:1234/v1/chat/completions`

### Coverage Expansion (ClawHub Public Index)

- Analytizer now ingests the direct public skill index with pagination:
  - `https://wry-manatee-359.convex.site/api/v1/skills`
- This is independent of Big-Pickel API and allows large-scale coverage even when Big-Pickel is blocked.
- Default pipeline behavior:
  - includes public index ingestion unless `--no-public-index` is used
  - default page size `100`
  - default max pages `25`
- Example high-coverage run:
  - `python3 clawhub-analytizer/scripts/clawhub-analytizer.py --public-max-pages 20 --public-limit 100`

## Next Useful Moves

1. Fix the stale Control UI token state on the Ubuntu dashboard and any LAN browser clients that still hit `token_mismatch`.
2. Verify sub-agent spawn works now that the intended nodes are back online.
3. Confirm the posting flow and Oracle QA gating behave normally again.
4. Publish the WordPress skills and the earlier Mac/OpenClaw skills to ClawHub.
5. Publish the matching GitHub repos.
6. Rotate the ClawHub token after the immediate publish work.
7. Keep future operational notes in `CODEX-OPS.md`.
