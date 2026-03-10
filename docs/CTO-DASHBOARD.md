# CTO Dashboard Runbook

## Goal

One local dashboard for:

- OCI account auth + estimated cost
- IPv4/IPv6 public firewall exposure
- CrowdSec presence on servers
- heartbeat endpoint status (Phi/gpt-oss model API)
- Amazon SES DNS posture
- optional Enhance API domain/DNS checks

## Files

- Config:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/cto-ops-config.json`
- Snapshot output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/cto-ops-snapshot.json`
- Scanner:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/cto-ops-scan.py`
- File-open bundle:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/build-cto-dashboard-data.py`
- Migration planner:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/build-vhost-migration-plan.py`
- Dashboard:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/dashboard/cto-dashboard.html`
- Migration plan output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/vhost-migration-plan.json`

## Run

```bash
cd /Volumes/MacHome/Users/mmurphy/openclaw-ops
python3 clawhub-analytizer/scripts/cto-ops-scan.py
python3 clawhub-analytizer/scripts/build-cto-dashboard-data.py
python3 clawhub-analytizer/scripts/build-vhost-migration-plan.py
python3 clawhub-analytizer/scripts/build-need-md.py
```

Open:

- `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/dashboard/cto-dashboard.html`

Or serve locally:

```bash
cd /Volumes/MacHome/Users/mmurphy/openclaw-ops
python3 -m http.server 8787
```

Then:

- `http://localhost:8787/clawhub-analytizer/dashboard/cto-dashboard.html`

## Hourly Automation

```bash
cd /Volumes/MacHome/Users/mmurphy/openclaw-ops
bash clawhub-analytizer/scripts/install-cto-ops-cron.sh
```

This hourly run now also refreshes:

- `/Volumes/MacHome/Users/mmurphy/openclaw-ops/NEED.md`

## OCI 401 Fix

If profile shows `NotAuthenticated`:

1. Keep `.oci/key.pem` + fingerprint synced (already true in this workspace).
2. In OCI console, open the API user in the matching tenancy.
3. Ensure the current public key is uploaded and active for that user.
4. Ensure the `user`, `tenancy`, `fingerprint`, and `region` in `~/.oci/config` belong to the same tenancy.

Validation:

```bash
oci --profile DEFAULT iam region list --output json
```

## Multi-Tenancy Labels

`cto-ops-config.json` supports labeled OCI entries:

```json
"ociProfiles": [
  {
    "profile": "DEFAULT",
    "label": "Net30 Main",
    "owner": "Matthew Murphy",
    "environment": "prod",
    "enabled": true
  },
  {
    "profile": "rick74",
    "label": "Rick74 Tenancy",
    "owner": "rick@circle...",
    "environment": "prod",
    "enabled": true
  }
]
```

If a profile exists in config but not in `~/.oci/config`, the dashboard flags it with `profile_not_found_in_oci_config`.

## Enhance API

`cto-ops-scan.py` supports bearer token auth against Enhance API.

Config keys in `cto-ops-config.json`:

- `enhance.enabled`
- `enhance.baseUrl`
- `enhance.bearerTokenEnv`
- `enhance.orgIds`
- `enhance.dnsRecordTargets`

Export your token:

```bash
export ENHANCE_BEARER_TOKEN='...'
```

## M1 Intranet Stack

Bootstrap script:

- `/Volumes/MacHome/Users/mmurphy/openclaw-ops/OpsCenter/scripts/setup-m1-ci47-intranet.sh`

This installs/starts:

- `php@8.5`
- `mariadb`
- `nginx`
- CodeIgniter `4.7` app starter
