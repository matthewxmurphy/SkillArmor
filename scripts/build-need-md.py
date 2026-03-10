#!/usr/bin/env python3
"""Generate workspace NEED.md from CTO snapshot blockers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AN_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = AN_ROOT / "data" / "cto-ops-snapshot.json"
MIGRATION_PLAN = AN_ROOT / "data" / "vhost-migration-plan.json"
OUT = ROOT / "NEED.md"


def now_local_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def main() -> None:
    if not SNAPSHOT.exists():
        stamp = now_local_iso()
        OUT.write_text(
            "# NEED\n\n"
            f"Updated: {stamp}\n\n"
            f"- [ ] [{stamp}] Run `python3 clawhub-analytizer/scripts/cto-ops-scan.py` first so blockers can be detected.\n",
            encoding="utf-8",
        )
        print(f"Wrote {OUT}")
        return

    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    oci = data.get("ociProfiles", [])
    ssh_hosts = data.get("sshHosts", [])
    ses_dns = data.get("sesDns", [])
    enhance = data.get("enhance", {})
    migration = {}
    if MIGRATION_PLAN.exists():
        try:
            migration = json.loads(MIGRATION_PLAN.read_text(encoding="utf-8"))
        except Exception:
            migration = {}

    lines: list[str] = []
    item_stamp = str(data.get("generatedAt") or now_local_iso())

    def add_task(text: str, detail: str | None = None) -> None:
        lines.append(f"- [ ] [{item_stamp}] {text}")
        if detail:
            lines.append(f"  {detail}")

    lines.append("# NEED")
    lines.append("")
    lines.append(f"Updated: {now_local_iso()}")
    lines.append(f"Snapshot: {data.get('generatedAt', 'unknown')}")
    lines.append("")
    lines.append("## Immediate Blockers")
    lines.append("")

    blocker_count = 0
    for row in oci:
        label = row.get("label") or row.get("profile") or "OCI Profile"
        profile = row.get("profile") or "UNKNOWN"
        err = str(row.get("authError") or "").strip()
        if row.get("enabled", True) and not row.get("authOk"):
            blocker_count += 1
            if "profile_not_found_in_oci_config" in err:
                add_task(
                    f"Add OCI profile `{profile}` to `~/.oci/config` (`label: {label}`).",
                    "Run after add: `oci --profile " + profile + " iam region list --output json`",
                )
            elif "NotAuthenticated" in err:
                add_task(
                    f"Re-authorize/rotate OCI API key for `{profile}` (`label: {label}`) in OCI Console.",
                    "Verify: `oci --profile " + profile + " iam region list --output json`",
                )
            else:
                add_task(
                    f"Fix OCI auth for `{profile}` (`label: {label}`): `{err[:180]}`",
                    "Verify: `oci --profile " + profile + " iam region list --output json`",
                )

    for host in ssh_hosts:
        if host.get("enabled") and not host.get("ok"):
            blocker_count += 1
            name = host.get("name", "ssh-target")
            add_task(
                f"Fix SSH target `{name}` connectivity so CrowdSec checks can run (`{host.get('error', 'unknown')}`)."
            )

    for row in ses_dns:
        if not row.get("enabled", True):
            continue
        if not row.get("ok"):
            blocker_count += 1
            domain = row.get("domain", "domain")
            missing = row.get("missingSpfIncludes", [])
            if missing:
                add_task(f"Add SPF include(s) for `{domain}`: `{', '.join(missing)}`.")
            if not row.get("hasDmarc"):
                add_task(f"Add DMARC TXT record for `{domain}`.")
            dkim = [x.get("selector") for x in row.get("dkim", []) if not x.get("ok") and x.get("selector")]
            if dkim:
                add_task(f"Add/fix DKIM CNAME selector(s) for `{domain}`: `{', '.join(dkim)}`.")

    if enhance.get("enabled") and not enhance.get("authOk"):
        blocker_count += 1
        token_env = enhance.get("tokenEnv", "ENHANCE_BEARER_TOKEN")
        add_task(f"Set Enhance token env `{token_env}` and verify API auth.")

    if migration:
        summary = migration.get("summary", {}) if isinstance(migration.get("summary"), dict) else {}
        if int(summary.get("ipv6ReadyCount", 0) or 0) == 0:
            blocker_count += 1
            add_task(
                "Add IPv6 address(es) to at least one vhost migration target in `clawhub-analytizer/data/vhost-migration-targets.json`."
            )
        if int(summary.get("migrationReadyCount", 0) or 0) == 0:
            blocker_count += 1
            add_task(
                "No migration-ready OCI target found. Fix blockers in `clawhub-analytizer/data/vhost-migration-plan.json`."
            )

    if blocker_count == 0:
        lines.append("- [x] No immediate blockers from current snapshot.")

    lines.append("")
    lines.append("## Nice To Have")
    lines.append("")
    add_task("Add friendly labels/owners for every OCI profile in `clawhub-analytizer/data/cto-ops-config.json`.")
    add_task("Add all production SSH targets so CrowdSec coverage is complete.")
    add_task("Enable Enhance API section once bearer token and org/domain IDs are ready.")
    lines.append("")
    lines.append("## Runbook Commands")
    lines.append("")
    lines.append("- `python3 clawhub-analytizer/scripts/cto-ops-scan.py`")
    lines.append("- `python3 clawhub-analytizer/scripts/build-cto-dashboard-data.py`")
    lines.append("- `python3 clawhub-analytizer/scripts/build-need-md.py`")
    lines.append("- `open clawhub-analytizer/dashboard/cto-dashboard.html`")
    lines.append("")
    lines.append("## Snapshot Summary")
    lines.append("")
    lines.append(f"- OCI profiles: {summary.get('ociProfileCount', 0)}")
    lines.append(f"- OCI auth ok: {summary.get('ociAuthOkCount', 0)}")
    lines.append(f"- Estimated monthly cost: ${float(summary.get('estimatedMonthlyCost', 0.0)):.2f}")
    lines.append(f"- Unexpected public ingress rules: {summary.get('firewallUnexpectedPublicIngressCount', 0)}")
    lines.append(f"- CrowdSec missing hosts: {summary.get('crowdsecMissingCount', 0)}")
    lines.append(f"- Heartbeat failures: {summary.get('heartbeatFailures', 0)}")
    lines.append(f"- SES DNS failures: {summary.get('sesDomainFailures', 0)}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
