# SkillArmor

Alpha release `0.0.1-alpha`.

ClawHub analytizer workspace for trust scanning, evidence ranking, queue generation, and dashboard review.

## Structure

- `data/` scan configuration and findings JSON
- `docs/` reports and operator queue markdown
- `scripts/` automation pipeline and API runner
- `dashboard/` static review UI (`browser.html`, generated `browser-data.js`)

## Local Config

Copy the example config first:

```bash
cp data/big-pickel-search-config.example.json data/big-pickel-search-config.json
```

Then set your key in `data/big-pickel-search-config.json` at `api.apiKey`.

Local fallback (when primary API fails):

- configure `fallback` in `data/big-pickel-search-config.json`
- default provider: `auto` (endpoint auto-discovery)
- default host: `http://127.0.0.1`
- discovered endpoint: environment-dependent
- default model pin: `Phi-3.5-mini-instruct.Q8_0.gguf`

Scan policy:

- set `scanMode` in `data/big-pickel-search-config.json`
- `prefer_local` (default): use local GPU first, skip Big-Pickel if local succeeds
- `local_only`: require local GPU and never call Big-Pickel
- `api_first`: call Big-Pickel first, fallback to local only on failure

## Commands

Build dashboard data bundle:

```bash
cd /path/to/SkillArmor
python3 scripts/build-browser-data.py
```

Run local merge/update pipeline:

```bash
cd /path/to/SkillArmor
python3 scripts/clawhub-analytizer.py
```

Run pipeline with live scan first:

```bash
cd /path/to/SkillArmor
python3 scripts/clawhub-analytizer.py --run-scan
```

High-coverage public index ingestion (recommended):

```bash
cd /path/to/SkillArmor
python3 scripts/clawhub-analytizer.py --public-max-pages 20 --public-limit 100
```

Build SkillArmor public feed JSON:

```bash
cd /path/to/SkillArmor
python3 scripts/export-skillarmor-feed.py --out ../skillarmor-site/data/skillarmor-feed.json
```

Feed output:

- `../skillarmor-site/data/skillarmor-feed.json`

Generate two-POV comment write-ups + queue:

```bash
cd /path/to/SkillArmor
python3 scripts/process-comment-queue.py
```

Process queue slowly (max one post attempt per run by default):

```bash
cd /path/to/SkillArmor
python3 scripts/process-comment-queue.py --process --max-posts 1 --post-command "<your_command_template>"
```

Install local 30-minute cron for queue processing:

```bash
cd /path/to/SkillArmor
bash scripts/install-comment-queue-cron.sh
```

Cron runner config:

- `data/comment-post-config.json`
  - `enabled`: when `true`, queue worker will attempt slow posting
  - `maxPostsPerRun`: throttle count per run
  - `postCommandTemplate`: your posting command template

Queue outputs:

- `data/comment-post-queue.json`
- `docs/COMMENTS.md`

Publish feed/site to remote host (SSH/SCP/rsync):

```bash
cd /path/to/SkillArmor
SKILLARMOR_SITE_ROOT=/path/to/skillarmor-site bash scripts/publish-skillarmor-feed.sh
```

Deploy config:

- `data/skillarmor-deploy-config.json`

Install twice-daily publish cron:

```bash
cd /path/to/SkillArmor
bash scripts/install-skillarmor-publish-cron.sh
```

Generate nginx vhost configs from local project plan:

```bash
cd /path/to/SkillArmor
python3 scripts/manage-vhosts.py
```

Every run auto-writes a copy/paste Codex handoff JSON:

- `data/codex-vhost-handoff.json`

Build vhost migration ranking (cheapest OCI + IPv6-ready targets):

```bash
cd /path/to/SkillArmor
python3 scripts/build-vhost-migration-plan.py
```

Migration inputs/outputs:

- `data/vhost-migration-targets.json`
- `data/vhost-migration-plan.json`

Vhost deploy key policy:

- deploy key must live under `/Projects` (not personal `~/.ssh/*` keys)
- default path in deploy config: `/Projects/vhost-m1/keys/m1_vhost_ed25519`

Create a dedicated deploy key:

```bash
PROJECT_SLUG=vhost-m1 KEY_PURPOSE=m1_vhost \
  /path/to/OpsCenter/scripts/create-project-keypair.sh
```

Deploy generated vhosts to remote server:

```bash
cd /path/to/SkillArmor
python3 scripts/manage-vhosts.py --deploy
```

Run CTO infra scan (OCI cost + firewall + CrowdSec + SES + Enhance):

```bash
cd /path/to/SkillArmor
python3 scripts/cto-ops-scan.py
python3 scripts/build-cto-dashboard-data.py
python3 scripts/build-need-md.py
```

Sync Nginx Proxy Manager hosts from JSON config:

```bash
cd /path/to/SkillArmor
export NPM_API_PASSWORD='replace-me'
python3 scripts/manage-npm-proxy-hosts.py
```

Apply local wildcard DNS for `*.m1.local` on the NPM host:

```bash
cd /path/to/SkillArmor
sudo python3 scripts/manage-npm-proxy-hosts.py --apply-dns
brew services restart dnsmasq
```

Install hourly CTO scan cron:

```bash
cd /path/to/SkillArmor
bash scripts/install-cto-ops-cron.sh
```

Vhost plan + deploy config:

- `data/vhost-projects.json`
- `data/vhost-deploy-config.json`
- `data/cto-ops-config.json`
  - supports labeled multi-tenancy OCI profiles (`profile`, `label`, `owner`, `environment`, `enabled`)

## Dashboard

- Direct open: `dashboard/browser.html`
- Server mode: `http://localhost:8787/dashboard/browser.html`
- Runbooks:
  - `docs/SETUP.md`
  - `docs/CODEX-OPS.md`
  - `docs/CTO-DASHBOARD.md`
  - `docs/NPM-LOCAL-SUBDOMAINS.md`
- Local UI includes a **Vhost Manager** section for plan import/export + deploy command copy.
- CTO dashboard:
  - `dashboard/cto-dashboard.html`
