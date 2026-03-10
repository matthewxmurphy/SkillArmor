# Nginx Proxy Manager + `*.m1.local` Runbook

This adds API-driven proxy host creation so project handoffs can get stable local subdomains.

## Files

- Config:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/npm-proxy-manager-config.json`
- Script:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/scripts/manage-npm-proxy-hosts.py`
- Last sync output:
  - `/Volumes/MacHome/Users/mmurphy/openclaw-ops/clawhub-analytizer/data/npm-proxy-last-sync.json`

## 1) Set NPM API Secret

```bash
export NPM_API_PASSWORD='replace-me'
```

`NPM_API_PASSWORD` must match the Nginx Proxy Manager admin user configured in `npm.identity`.

## 2) Edit Hosts

Update `hosts` in `npm-proxy-manager-config.json`:

```json
{
  "subdomain": "project-a",
  "forwardHost": "127.0.0.1",
  "forwardPort": 3000,
  "enabled": true
}
```

This will map to:

- `project-a.m1.local`

## 3) Apply to NPM

```bash
cd /Volumes/MacHome/Users/mmurphy/openclaw-ops
python3 clawhub-analytizer/scripts/manage-npm-proxy-hosts.py
```

## 4) Optional Local Wildcard DNS

On the Mac running NPM, enable wildcard DNS routing to that host:

```bash
cd /Volumes/MacHome/Users/mmurphy/openclaw-ops
sudo python3 clawhub-analytizer/scripts/manage-npm-proxy-hosts.py --apply-dns
brew services restart dnsmasq
```

This writes:

- `/opt/homebrew/etc/dnsmasq.d/m1-local.conf`
- `/etc/resolver/m1.local`

## Notes

- `.local` is multicast DNS territory. If you hit resolver collisions on other clients, move to `m1.home.arpa` or another private suffix in config.
- Script is idempotent for configured hostnames: existing domains are updated, missing ones are created.
