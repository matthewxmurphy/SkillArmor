#!/usr/bin/env python3
"""Build a vhost migration plan ranked by OCI monthly cost and IPv6 readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = PROJECT_ROOT / "data" / "cto-ops-snapshot.json"
DEFAULT_VHOST_PLAN = PROJECT_ROOT / "data" / "vhost-projects.json"
DEFAULT_TARGETS = PROJECT_ROOT / "data" / "vhost-migration-targets.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "vhost-migration-plan.json"
VERSION = "0.5.0"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def to_float(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_target(entry: dict[str, Any], idx: int) -> dict[str, Any]:
    target_id = str(entry.get("id") or f"target-{idx + 1}").strip()
    label = str(entry.get("label") or target_id).strip() or target_id
    return {
        "id": target_id,
        "label": label,
        "ociProfile": str(entry.get("ociProfile") or "").strip(),
        "region": str(entry.get("region") or "").strip(),
        "host": str(entry.get("host") or "").strip(),
        "ipv4": str(entry.get("ipv4") or "").strip(),
        "ipv6": str(entry.get("ipv6") or "").strip(),
        "sshUser": str(entry.get("sshUser") or "ubuntu").strip() or "ubuntu",
        "sshPort": int(entry.get("sshPort") or 22),
        "sshKeyPath": str(entry.get("sshKeyPath") or "").strip(),
        "enabled": as_bool(entry.get("enabled", True), default=True),
        "monthlyCostUsdOverride": to_float(entry.get("monthlyCostUsdOverride")),
        "notes": str(entry.get("notes") or "").strip(),
    }


def load_targets(path: Path, snapshot_profiles: list[dict[str, Any]]) -> dict[str, Any]:
    if path.exists():
        cfg = read_json(path)
    else:
        cfg = {"version": VERSION, "policy": {}, "targets": []}

    policy_raw = cfg.get("policy", {}) if isinstance(cfg.get("policy"), dict) else {}
    policy = {
        "requireIpv6": as_bool(policy_raw.get("requireIpv6", True), default=True),
        "preferLowestCost": as_bool(policy_raw.get("preferLowestCost", True), default=True),
        "maxMonthlyCostUsd": to_float(policy_raw.get("maxMonthlyCostUsd"), default=None),
        "freeTierThresholdUsd": to_float(policy_raw.get("freeTierThresholdUsd", 0.50), default=0.50),
    }

    items = cfg.get("targets")
    targets: list[dict[str, Any]] = []
    if isinstance(items, list) and items:
        for idx, raw in enumerate(items):
            if isinstance(raw, dict):
                targets.append(normalize_target(raw, idx))
    else:
        for idx, profile in enumerate(snapshot_profiles):
            name = str(profile.get("profile") or f"profile-{idx + 1}")
            targets.append(
                normalize_target(
                    {
                        "id": f"{name.lower()}-target",
                        "label": str(profile.get("label") or name),
                        "ociProfile": name,
                        "region": str(profile.get("region") or ""),
                        "enabled": True,
                    },
                    idx,
                )
            )

    return {"policy": policy, "targets": targets}


def profile_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in snapshot.get("ociProfiles", []):
        if not isinstance(row, dict):
            continue
        key = str(row.get("profile") or "").strip()
        if key:
            out[key] = row
    return out


def target_score(item: dict[str, Any]) -> tuple[int, float, int, str]:
    ready_penalty = 0 if item.get("migrationReady") else 1
    cost = item.get("effectiveMonthlyCostUsd")
    cost_value = float(cost) if isinstance(cost, (int, float)) else 1e9
    auth_penalty = 0 if item.get("ociAuthOk") else 1
    return (ready_penalty, cost_value, auth_penalty, str(item.get("id")))


def build_plan(
    *,
    snapshot: dict[str, Any],
    vhost_plan: dict[str, Any],
    targets_cfg: dict[str, Any],
) -> dict[str, Any]:
    pmap = profile_map(snapshot)
    policy = targets_cfg["policy"]
    require_ipv6 = policy["requireIpv6"]
    max_cost = policy["maxMonthlyCostUsd"]
    free_threshold = policy["freeTierThresholdUsd"]

    evaluated: list[dict[str, Any]] = []
    for target in targets_cfg["targets"]:
        if not target.get("enabled", True):
            continue
        profile = pmap.get(target["ociProfile"], {})
        profile_cost = to_float(
            (
                (profile.get("cost") or {}).get("totalCost")
                if isinstance(profile.get("cost"), dict)
                else None
            )
        )
        effective_cost = target["monthlyCostUsdOverride"]
        if effective_cost is None:
            effective_cost = profile_cost

        has_ipv6 = bool(target.get("ipv6"))
        has_host = bool(target.get("host") or target.get("ipv4") or target.get("ipv6"))
        oci_auth_ok = bool(profile.get("authOk")) if profile else False

        blockers: list[str] = []
        if require_ipv6 and not has_ipv6:
            blockers.append("missing_ipv6")
        if max_cost is not None and effective_cost is not None and effective_cost > max_cost:
            blockers.append("over_cost_policy")
        if target.get("ociProfile") and profile and not oci_auth_ok:
            blockers.append("oci_profile_auth_failed")
        if not has_host:
            blockers.append("missing_host_or_ip")
        if target.get("sshKeyPath") and not str(target.get("sshKeyPath")).startswith("/Projects/"):
            blockers.append("ssh_key_not_in_projects_root")

        evaluated_item = {
            "id": target["id"],
            "label": target["label"],
            "ociProfile": target["ociProfile"],
            "region": target["region"] or str(profile.get("region") or ""),
            "host": target["host"],
            "ipv4": target["ipv4"],
            "ipv6": target["ipv6"],
            "ipv6Ready": has_ipv6,
            "hostReady": has_host,
            "ociAuthOk": oci_auth_ok,
            "profileKnown": bool(profile),
            "effectiveMonthlyCostUsd": effective_cost,
            "freeOrNearFree": (effective_cost is not None and effective_cost <= free_threshold),
            "sshUser": target["sshUser"],
            "sshPort": target["sshPort"],
            "sshKeyPath": target["sshKeyPath"],
            "notes": target["notes"],
            "blockers": blockers,
            "migrationReady": len(blockers) == 0,
        }
        evaluated.append(evaluated_item)

    ranked = sorted(evaluated, key=target_score)
    best = ranked[0] if ranked else None

    enabled_projects = []
    for row in vhost_plan.get("projects", []):
        if isinstance(row, dict) and row.get("enabled", True):
            enabled_projects.append(row)

    per_project: list[dict[str, Any]] = []
    for project in enabled_projects:
        domain = str(project.get("domain") or "")
        project_id = str(project.get("id") or domain or "project")
        target_host = (best or {}).get("host") or (best or {}).get("ipv4") or (best or {}).get("ipv6") or "<target-host>"
        target_user = (best or {}).get("sshUser") or "ubuntu"
        target_port = int((best or {}).get("sshPort") or 22)
        target_root = str(project.get("root") or f"/var/www/{project_id}")
        per_project.append(
            {
                "id": project_id,
                "domain": domain,
                "recommendedTargetId": (best or {}).get("id"),
                "recommendedTargetLabel": (best or {}).get("label"),
                "targetRoot": target_root,
                "commands": {
                    "syncContentRsync": (
                        f"rsync -az --delete -e 'ssh -p {target_port}' "
                        f"<LOCAL_SITE_DIR>/ {target_user}@{target_host}:{target_root}/"
                    ),
                    "remoteNginxTestReload": (
                        f"ssh -p {target_port} {target_user}@{target_host} "
                        "'sudo nginx -t && sudo systemctl reload nginx'"
                    ),
                },
            }
        )

    ipv6_targets = [x for x in ranked if x.get("ipv6Ready")]

    return {
        "version": VERSION,
        "generatedAt": now_iso(),
        "inputs": {
            "snapshotGeneratedAt": snapshot.get("generatedAt"),
            "vhostPlanVersion": vhost_plan.get("version"),
        },
        "policy": policy,
        "summary": {
            "targetCount": len(ranked),
            "ipv6ReadyCount": len(ipv6_targets),
            "migrationReadyCount": len([x for x in ranked if x.get("migrationReady")]),
            "cheapestKnownMonthlyCostUsd": min(
                (x["effectiveMonthlyCostUsd"] for x in ranked if x["effectiveMonthlyCostUsd"] is not None),
                default=None,
            ),
        },
        "recommendedTarget": best,
        "rankedTargets": ranked,
        "ipv6Targets": ipv6_targets,
        "projects": per_project,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--vhost-plan", type=Path, default=DEFAULT_VHOST_PLAN)
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.snapshot.exists():
        raise SystemExit(f"Missing snapshot: {args.snapshot}")
    if not args.vhost_plan.exists():
        raise SystemExit(f"Missing vhost plan: {args.vhost_plan}")

    snapshot = read_json(args.snapshot)
    vhost_plan = read_json(args.vhost_plan)
    targets_cfg = load_targets(
        args.targets,
        snapshot_profiles=[x for x in snapshot.get("ociProfiles", []) if isinstance(x, dict)],
    )
    plan = build_plan(snapshot=snapshot, vhost_plan=vhost_plan, targets_cfg=targets_cfg)
    write_json(args.output, plan)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
