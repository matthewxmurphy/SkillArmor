#!/usr/bin/env python3
"""Generate a CTO infrastructure snapshot for OCI/network/security/email health."""

from __future__ import annotations

import argparse
import configparser
import json
import os
import platform
import shlex
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "data" / "cto-ops-config.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "cto-ops-snapshot.json"
DEFAULT_VERSION = "0.5.0"
PUBLIC_SOURCES = {"0.0.0.0/0", "::/0"}


@dataclass
class CmdResult:
    ok: bool
    command: list[str]
    code: int
    stdout: str
    stderr: str
    error: str = ""

    @property
    def output(self) -> str:
        return self.stdout if self.stdout.strip() else self.stderr


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_cmd(command: list[str], timeout: int = 30) -> CmdResult:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return CmdResult(
            ok=False,
            command=command,
            code=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            error=f"timeout after {timeout}s",
        )
    except FileNotFoundError:
        return CmdResult(
            ok=False,
            command=command,
            code=127,
            stdout="",
            stderr="",
            error=f"command not found: {command[0]}",
        )
    return CmdResult(
        ok=(proc.returncode == 0),
        command=command,
        code=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        error="",
    )


def run_json_cmd(command: list[str], timeout: int = 30) -> tuple[CmdResult, dict[str, Any] | None]:
    result = run_cmd(command, timeout=timeout)
    if not result.ok:
        return result, None
    try:
        return result, json.loads(result.stdout)
    except json.JSONDecodeError:
        return result, None


def maybe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def oci_config_path() -> Path:
    env_path = os.environ.get("OCI_CLI_CONFIG_FILE", "").strip()
    if env_path:
        return Path(env_path).expanduser()
    return Path.home() / ".oci" / "config"


def load_oci_sections(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    parser = configparser.ConfigParser()
    parser.read(path)
    if parser.defaults():
        out["DEFAULT"] = {k: v for k, v in parser.defaults().items()}
    for section in parser.sections():
        out[section] = {k: v for k, v in parser[section].items()}
    return out


def oci_profile_names(config: dict[str, Any], oci_sections: dict[str, dict[str, str]]) -> list[str]:
    listed = config.get("ociProfiles")
    if isinstance(listed, list) and listed:
        return [str(x).strip() for x in listed if str(x).strip()]
    return sorted(oci_sections.keys())


def normalize_oci_profile_entries(config: dict[str, Any]) -> list[dict[str, Any]]:
    raw = config.get("ociProfiles")
    entries: list[dict[str, Any]] = []
    if isinstance(raw, list) and raw:
        for item in raw:
            if isinstance(item, str):
                name = item.strip()
                if not name:
                    continue
                entries.append(
                    {
                        "profile": name,
                        "label": name,
                        "owner": "",
                        "environment": "",
                        "enabled": True,
                    }
                )
                continue
            if isinstance(item, dict):
                name = str(item.get("profile") or "").strip()
                if not name:
                    continue
                entries.append(
                    {
                        "profile": name,
                        "label": str(item.get("label") or name).strip() or name,
                        "owner": str(item.get("owner") or "").strip(),
                        "environment": str(item.get("environment") or "").strip(),
                        "enabled": bool(item.get("enabled", True)),
                    }
                )
    return entries


def command_preview(command: list[str]) -> str:
    return shlex.join(command)


def parse_port_range(rule: dict[str, Any]) -> tuple[int, int]:
    tcp = (
        rule.get("tcp-options")
        or rule.get("tcpOptions")
        or {}
    )
    pr = tcp.get("destination-port-range") or tcp.get("destinationPortRange")
    if not isinstance(pr, dict):
        return (1, 65535)
    minimum = maybe_int(pr.get("min"), 1)
    maximum = maybe_int(pr.get("max"), 65535)
    if maximum < minimum:
        minimum, maximum = maximum, minimum
    return (minimum, maximum)


def normalize_protocol(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"6", "tcp"}:
        return "tcp"
    if text in {"all", "-1", "any"}:
        return "all"
    return text or "unknown"


def is_public_ingress(rule: dict[str, Any]) -> tuple[bool, str]:
    source = str(rule.get("source") or rule.get("source-network") or "").strip()
    if not source:
        source = str(rule.get("sourceType") or rule.get("source-type") or "").strip()
    return (source in PUBLIC_SOURCES, source)


def evaluate_ingress_rule(
    *,
    profile: str,
    compartment_id: str,
    vcn_name: str,
    parent_name: str,
    rule: dict[str, Any],
    allowed_ports: set[int],
) -> dict[str, Any] | None:
    direction = str(rule.get("direction", "INGRESS")).upper()
    if direction and direction != "INGRESS":
        return None
    public, source = is_public_ingress(rule)
    if not public:
        return None

    protocol = normalize_protocol(rule.get("protocol"))
    port_min, port_max = parse_port_range(rule)
    port_label = f"{port_min}" if port_min == port_max else f"{port_min}-{port_max}"

    unexpected = False
    if protocol in {"all", "unknown"}:
        unexpected = True
    elif protocol == "tcp":
        if not (port_min == port_max and port_min in allowed_ports):
            unexpected = True

    return {
        "profile": profile,
        "compartmentId": compartment_id,
        "vcn": vcn_name,
        "securityObject": parent_name,
        "source": source,
        "protocol": protocol,
        "portRange": [port_min, port_max],
        "portLabel": port_label,
        "unexpected": unexpected,
    }


def get_profile_cost(
    *,
    profile: str,
    tenancy_id: str,
    days: int,
    timeout: int,
) -> dict[str, Any]:
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=max(days, 1))

    cmd = [
        "oci",
        "--profile",
        profile,
        "usage-api",
        "usage-summary",
        "request-summarized-usages",
        "--tenant-id",
        tenancy_id,
        "--time-usage-started",
        start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "--time-usage-ended",
        end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "--granularity",
        "MONTHLY",
        "--query-type",
        "COST",
        "--group-by",
        '["service"]',
        "--is-aggregate-by-time",
        "true",
        "--output",
        "json",
    ]
    result, payload = run_json_cmd(cmd, timeout=timeout)
    if not result.ok or payload is None:
        return {
            "ok": False,
            "command": command_preview(cmd),
            "error": (result.error or result.output).strip(),
            "totalCost": None,
            "services": [],
        }

    items = payload.get("data", {}).get("items", [])
    services: list[dict[str, Any]] = []
    total = 0.0
    for item in items if isinstance(items, list) else []:
        service_name = (
            item.get("service")
            or item.get("service-name")
            or item.get("serviceName")
            or "unknown"
        )
        amount = None
        for key in (
            "computed-amount",
            "computedAmount",
            "cost",
            "amount",
            "total",
        ):
            if key in item:
                try:
                    amount = float(item[key])
                    break
                except (TypeError, ValueError):
                    pass
        if amount is None:
            continue
        total += amount
        services.append({"service": str(service_name), "cost": round(amount, 6)})

    services.sort(key=lambda x: x["cost"], reverse=True)
    return {
        "ok": True,
        "command": command_preview(cmd),
        "periodDays": days,
        "totalCost": round(total, 6),
        "services": services[:20],
    }


def get_compartments(profile: str, tenancy_id: str, timeout: int) -> list[dict[str, str]]:
    cmd = [
        "oci",
        "--profile",
        profile,
        "iam",
        "compartment",
        "list",
        "--all",
        "--access-level",
        "ACCESSIBLE",
        "--compartment-id",
        tenancy_id,
        "--compartment-id-in-subtree",
        "true",
        "--output",
        "json",
    ]
    result, payload = run_json_cmd(cmd, timeout=timeout)
    compartments: list[dict[str, str]] = [{"id": tenancy_id, "name": "tenancy-root"}]
    if not result.ok or payload is None:
        return compartments
    for item in payload.get("data", []) if isinstance(payload.get("data"), list) else []:
        lifecycle = str(item.get("lifecycle-state") or item.get("lifecycleState") or "")
        if lifecycle and lifecycle.upper() != "ACTIVE":
            continue
        cid = str(item.get("id") or "")
        if not cid:
            continue
        name = str(item.get("name") or cid)
        compartments.append({"id": cid, "name": name})
    return compartments


def get_firewall_findings(
    *,
    profile: str,
    tenancy_id: str,
    allowed_ports: set[int],
    timeout: int,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    command_count = 0
    compartments = get_compartments(profile, tenancy_id, timeout)

    for comp in compartments:
        comp_id = comp["id"]
        vcn_cmd = [
            "oci",
            "--profile",
            profile,
            "network",
            "vcn",
            "list",
            "--all",
            "--compartment-id",
            comp_id,
            "--output",
            "json",
        ]
        vcn_result, vcn_payload = run_json_cmd(vcn_cmd, timeout=timeout)
        command_count += 1
        if not vcn_result.ok or vcn_payload is None:
            continue

        for vcn in vcn_payload.get("data", []) if isinstance(vcn_payload.get("data"), list) else []:
            vcn_id = str(vcn.get("id") or "")
            vcn_name = str(vcn.get("display-name") or vcn.get("displayName") or vcn_id)
            if not vcn_id:
                continue

            sl_cmd = [
                "oci",
                "--profile",
                profile,
                "network",
                "security-list",
                "list",
                "--all",
                "--compartment-id",
                comp_id,
                "--vcn-id",
                vcn_id,
                "--output",
                "json",
            ]
            sl_result, sl_payload = run_json_cmd(sl_cmd, timeout=timeout)
            command_count += 1
            if sl_result.ok and sl_payload is not None:
                for sl in sl_payload.get("data", []) if isinstance(sl_payload.get("data"), list) else []:
                    parent = str(sl.get("display-name") or sl.get("displayName") or sl.get("id") or "security-list")
                    rules = sl.get("ingress-security-rules") or sl.get("ingressSecurityRules") or []
                    for rule in rules if isinstance(rules, list) else []:
                        finding = evaluate_ingress_rule(
                            profile=profile,
                            compartment_id=comp_id,
                            vcn_name=vcn_name,
                            parent_name=parent,
                            rule=rule,
                            allowed_ports=allowed_ports,
                        )
                        if finding:
                            findings.append(finding)

            nsg_cmd = [
                "oci",
                "--profile",
                profile,
                "network",
                "nsg",
                "list",
                "--all",
                "--compartment-id",
                comp_id,
                "--vcn-id",
                vcn_id,
                "--output",
                "json",
            ]
            nsg_result, nsg_payload = run_json_cmd(nsg_cmd, timeout=timeout)
            command_count += 1
            if not nsg_result.ok or nsg_payload is None:
                continue

            for nsg in nsg_payload.get("data", []) if isinstance(nsg_payload.get("data"), list) else []:
                nsg_id = str(nsg.get("id") or "")
                nsg_name = str(nsg.get("display-name") or nsg.get("displayName") or nsg_id or "nsg")
                if not nsg_id:
                    continue
                rules_cmd = [
                    "oci",
                    "--profile",
                    profile,
                    "network",
                    "nsg",
                    "rules",
                    "list",
                    "--all",
                    "--nsg-id",
                    nsg_id,
                    "--output",
                    "json",
                ]
                rules_result, rules_payload = run_json_cmd(rules_cmd, timeout=timeout)
                command_count += 1
                if not rules_result.ok or rules_payload is None:
                    continue
                for rule in rules_payload.get("data", []) if isinstance(rules_payload.get("data"), list) else []:
                    finding = evaluate_ingress_rule(
                        profile=profile,
                        compartment_id=comp_id,
                        vcn_name=vcn_name,
                        parent_name=nsg_name,
                        rule=rule,
                        allowed_ports=allowed_ports,
                    )
                    if finding:
                        findings.append(finding)

    unexpected = [f for f in findings if f["unexpected"]]
    return {
        "ok": True,
        "commandsRun": command_count,
        "publicIngressRuleCount": len(findings),
        "unexpectedPublicIngressCount": len(unexpected),
        "findings": findings,
    }


def scan_oci(
    config: dict[str, Any],
    timeout: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    oci_sections = load_oci_sections(oci_config_path())
    profile_entries = normalize_oci_profile_entries(config)
    if not profile_entries:
        profile_entries = [
            {
                "profile": p,
                "label": p,
                "owner": "",
                "environment": "",
                "enabled": True,
            }
            for p in oci_profile_names(config, oci_sections)
        ]
    allowed_ports = {
        maybe_int(x, -1)
        for x in (config.get("scan", {}).get("allowedPublicInboundTcpPorts") or [22, 80, 443])
    }
    allowed_ports = {x for x in allowed_ports if x > 0}
    days = maybe_int(config.get("scan", {}).get("ociCostDays"), 30)

    profile_rows: list[dict[str, Any]] = []
    all_firewall_findings: list[dict[str, Any]] = []

    for entry in profile_entries:
        profile = entry["profile"]
        section = oci_sections.get(profile, {})
        tenancy_id = str(section.get("tenancy", "")).strip()
        region = str(section.get("region", "")).strip()
        user_id = str(section.get("user", "")).strip()
        enabled = bool(entry.get("enabled", True))

        auth_cmd = [
            "oci",
            "--profile",
            profile,
            "iam",
            "region",
            "list",
            "--output",
            "json",
        ]
        if enabled:
            auth_result, _ = run_json_cmd(auth_cmd, timeout=timeout)
        else:
            auth_result = CmdResult(
                ok=False,
                command=auth_cmd,
                code=1,
                stdout="",
                stderr="",
                error="profile_disabled_in_config",
            )

        if enabled and not section:
            auth_result = CmdResult(
                ok=False,
                command=auth_cmd,
                code=1,
                stdout="",
                stderr="",
                error=f"profile_not_found_in_oci_config:{profile}",
            )

        row: dict[str, Any] = {
            "profile": profile,
            "label": str(entry.get("label") or profile),
            "owner": str(entry.get("owner") or ""),
            "environment": str(entry.get("environment") or ""),
            "enabled": enabled,
            "region": region,
            "user": user_id,
            "tenancy": tenancy_id,
            "authOk": auth_result.ok,
            "authError": "" if auth_result.ok else (auth_result.error or auth_result.output).strip(),
            "cost": {"ok": False, "totalCost": None, "services": []},
            "firewall": {"ok": False, "publicIngressRuleCount": 0, "unexpectedPublicIngressCount": 0},
        }

        if auth_result.ok and tenancy_id:
            cost = get_profile_cost(
                profile=profile,
                tenancy_id=tenancy_id,
                days=days,
                timeout=timeout,
            )
            row["cost"] = cost
            fw = get_firewall_findings(
                profile=profile,
                tenancy_id=tenancy_id,
                allowed_ports=allowed_ports,
                timeout=timeout,
            )
            row["firewall"] = {
                "ok": fw["ok"],
                "commandsRun": fw["commandsRun"],
                "publicIngressRuleCount": fw["publicIngressRuleCount"],
                "unexpectedPublicIngressCount": fw["unexpectedPublicIngressCount"],
            }
            all_firewall_findings.extend(fw["findings"])

        profile_rows.append(row)
    return profile_rows, all_firewall_findings


def run_ssh_probe(target: dict[str, Any], timeout: int) -> dict[str, Any]:
    name = str(target.get("name") or target.get("host") or "target")
    host = str(target.get("host") or "").strip()
    user = str(target.get("user") or "ubuntu").strip()
    port = maybe_int(target.get("port"), 22)
    key_path = str(target.get("sshKeyPath") or "").strip()
    enabled = bool(target.get("enabled", True))
    if not enabled or not host:
        return {
            "name": name,
            "host": host,
            "enabled": enabled,
            "ok": False,
            "error": "disabled_or_missing_host",
        }

    ssh_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=8",
        "-p",
        str(port),
    ]
    if key_path:
        ssh_cmd.extend(["-i", key_path])
    ssh_cmd.append(f"{user}@{host}")
    ssh_cmd.append(
        "set -e; "
        "if command -v crowdsec >/dev/null 2>&1; then echo crowdsec_installed=yes; else echo crowdsec_installed=no; fi; "
        "if command -v systemctl >/dev/null 2>&1; then echo crowdsec_active=$(systemctl is-active crowdsec 2>/dev/null || true); else echo crowdsec_active=unknown; fi; "
        "if command -v cscli >/dev/null 2>&1; then echo cscli=$(cscli version 2>/dev/null | head -n1); fi; "
        "if command -v ss >/dev/null 2>&1; then echo listening_ports=$(ss -ltnH | awk '{print $4}' | sed 's/.*://g' | sort -n | uniq | tr '\\n' ',' ); fi"
    )
    result = run_cmd(ssh_cmd, timeout=timeout)
    if not result.ok:
        return {
            "name": name,
            "host": host,
            "enabled": enabled,
            "ok": False,
            "error": (result.error or result.output).strip(),
            "command": command_preview(ssh_cmd),
        }

    values: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip()

    return {
        "name": name,
        "host": host,
        "enabled": enabled,
        "ok": True,
        "crowdsecInstalled": values.get("crowdsec_installed") == "yes",
        "crowdsecActive": values.get("crowdsec_active", "unknown"),
        "cscliVersion": values.get("cscli", ""),
        "listeningPortsRaw": values.get("listening_ports", ""),
    }


def scan_ssh_targets(config: dict[str, Any], timeout: int) -> list[dict[str, Any]]:
    targets = config.get("sshTargets")
    if not isinstance(targets, list):
        return []
    return [run_ssh_probe(t, timeout) for t in targets if isinstance(t, dict)]


def http_json(url: str, headers: dict[str, str] | None = None, timeout: int = 12) -> tuple[bool, int, dict[str, Any] | None, str]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = int(resp.getcode())
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return False, int(exc.code), None, raw
    except Exception as exc:  # noqa: BLE001
        return False, 0, None, str(exc)
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = None
    return (200 <= code < 300), code, payload, body


def scan_heartbeat(config: dict[str, Any], timeout: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    endpoints = config.get("heartbeatEndpoints")
    if not isinstance(endpoints, list):
        return rows
    for item in endpoints:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "heartbeat")
        url = str(item.get("url") or "").strip()
        enabled = bool(item.get("enabled", True))
        expects = [str(x).lower() for x in (item.get("expectModelContains") or [])]
        if not enabled or not url:
            rows.append({"name": name, "url": url, "enabled": enabled, "ok": False, "error": "disabled_or_missing_url"})
            continue
        ok, code, payload, raw = http_json(url, timeout=timeout)
        models: list[str] = []
        if isinstance(payload, dict):
            if isinstance(payload.get("data"), list):
                for model in payload["data"]:
                    if isinstance(model, dict):
                        mid = model.get("id")
                        if mid:
                            models.append(str(mid))
            if isinstance(payload.get("models"), list):
                models.extend(str(x) for x in payload["models"])
        model_text = " ".join(models).lower()
        expected_match = any(x in model_text for x in expects) if expects else True
        rows.append(
            {
                "name": name,
                "url": url,
                "enabled": enabled,
                "ok": ok and expected_match,
                "httpStatus": code,
                "models": models,
                "expectedMatch": expected_match,
                "error": "" if (ok and expected_match) else (raw[:400] if raw else "model_expectation_not_met"),
            }
        )
    return rows


def dig_records(record_type: str, name: str, timeout: int) -> list[str]:
    cmd = ["dig", "+short", record_type, name]
    result = run_cmd(cmd, timeout=timeout)
    if not result.ok:
        return []
    lines = [line.strip().strip('"') for line in result.stdout.splitlines() if line.strip()]
    return lines


def scan_ses_dns(config: dict[str, Any], timeout: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    domains = config.get("sesDomains")
    if not isinstance(domains, list):
        return rows
    for item in domains:
        if not isinstance(item, dict):
            continue
        enabled = bool(item.get("enabled", True))
        domain = str(item.get("domain") or "").strip().lower()
        if not enabled or not domain:
            rows.append({"domain": domain, "enabled": enabled, "ok": False, "error": "disabled_or_missing_domain"})
            continue

        txt_root = dig_records("TXT", domain, timeout)
        txt_dmarc = dig_records("TXT", f"_dmarc.{domain}", timeout)
        dkim_selectors = [str(x).strip() for x in (item.get("dkimSelectors") or []) if str(x).strip()]
        dkim_rows: list[dict[str, Any]] = []
        for selector in dkim_selectors:
            cname = dig_records("CNAME", f"{selector}._domainkey.{domain}", timeout)
            dkim_rows.append({"selector": selector, "ok": bool(cname), "records": cname})

        spf_includes = [str(x).strip().lower() for x in (item.get("spfIncludes") or []) if str(x).strip()]
        spf_blob = " ".join(txt_root).lower()
        missing_spf = [x for x in spf_includes if x not in spf_blob]
        dmarc_required = bool(item.get("requireDmarc", True))
        has_dmarc = any("v=dmarc1" in x.lower() for x in txt_dmarc)

        ok = (not missing_spf) and ((not dmarc_required) or has_dmarc) and all(x["ok"] for x in dkim_rows or [])
        rows.append(
            {
                "domain": domain,
                "enabled": enabled,
                "ok": ok,
                "rootTxt": txt_root,
                "dmarcTxt": txt_dmarc,
                "dkim": dkim_rows,
                "missingSpfIncludes": missing_spf,
                "hasDmarc": has_dmarc,
            }
        )
    return rows


def enhance_request(base_url: str, token: str, path: str, timeout: int) -> tuple[bool, int, Any, str]:
    url = base_url.rstrip("/") + path
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = int(resp.getcode())
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return False, int(exc.code), None, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return False, 0, None, str(exc)
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = body
    return True, code, payload, body


def scan_enhance(config: dict[str, Any], timeout: int) -> dict[str, Any]:
    enhance = config.get("enhance", {})
    if not isinstance(enhance, dict):
        return {"enabled": False}

    enabled = bool(enhance.get("enabled", False))
    base_url = str(enhance.get("baseUrl") or "https://api.enhance.com").strip()
    token_env = str(enhance.get("bearerTokenEnv") or "ENHANCE_BEARER_TOKEN").strip()
    token = os.environ.get(token_env, "").strip()

    report: dict[str, Any] = {
        "enabled": enabled,
        "baseUrl": base_url,
        "tokenEnv": token_env,
        "authOk": False,
        "orgs": [],
        "dnsTargets": [],
        "errors": [],
    }
    if not enabled:
        return report
    if not token:
        report["errors"].append(f"missing_token_env:{token_env}")
        return report

    org_ids = [str(x).strip() for x in (enhance.get("orgIds") or []) if str(x).strip()]
    dns_targets = [x for x in (enhance.get("dnsRecordTargets") or []) if isinstance(x, dict)]

    auth_ok, auth_code, auth_payload, auth_raw = enhance_request(base_url, token, "/settings", timeout)
    report["authOk"] = auth_ok
    report["authStatus"] = auth_code
    if not auth_ok:
        report["errors"].append((auth_raw or "enhance_auth_failed")[:400])
        return report

    for org_id in org_ids:
        ok, code, payload, raw = enhance_request(base_url, token, f"/orgs/{org_id}/domains?limit=200&offset=0", timeout)
        if not ok:
            report["orgs"].append(
                {"orgId": org_id, "ok": False, "httpStatus": code, "error": (raw or "")[:300]}
            )
            continue
        domains = []
        if isinstance(payload, dict):
            for key in ("items", "domains", "data"):
                if isinstance(payload.get(key), list):
                    domains = payload.get(key)
                    break
        report["orgs"].append({"orgId": org_id, "ok": True, "httpStatus": code, "domainCount": len(domains)})

    for target in dns_targets:
        org_id = str(target.get("orgId") or "").strip()
        website_id = str(target.get("websiteId") or "").strip()
        domain_id = str(target.get("domainId") or "").strip()
        domain_name = str(target.get("domain") or "").strip()
        if not org_id or not website_id or not domain_id:
            report["dnsTargets"].append(
                {
                    "orgId": org_id,
                    "websiteId": website_id,
                    "domainId": domain_id,
                    "domain": domain_name,
                    "ok": False,
                    "error": "missing_org_website_domain_id",
                }
            )
            continue
        path = f"/orgs/{org_id}/websites/{website_id}/domains/{domain_id}/dns-zone/records"
        ok, code, payload, raw = enhance_request(base_url, token, path, timeout)
        if not ok:
            report["dnsTargets"].append(
                {
                    "orgId": org_id,
                    "websiteId": website_id,
                    "domainId": domain_id,
                    "domain": domain_name,
                    "ok": False,
                    "httpStatus": code,
                    "error": (raw or "")[:300],
                }
            )
            continue
        records = []
        if isinstance(payload, dict):
            for key in ("items", "records", "data"):
                if isinstance(payload.get(key), list):
                    records = payload.get(key)
                    break
        report["dnsTargets"].append(
            {
                "orgId": org_id,
                "websiteId": website_id,
                "domainId": domain_id,
                "domain": domain_name,
                "ok": True,
                "httpStatus": code,
                "recordCount": len(records),
            }
        )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CTO ops scan and emit a JSON snapshot.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help=f"Config path (default: {DEFAULT_CONFIG})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Output JSON path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--timeout", type=int, default=0, help="Command timeout override in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.config.exists():
        print(f"Missing config: {args.config}", file=sys.stderr)
        return 1

    config = read_json(args.config)
    timeout = args.timeout if args.timeout > 0 else maybe_int(config.get("scan", {}).get("timeoutSeconds"), 25)

    profiles, firewall_findings = scan_oci(config, timeout)
    ssh_rows = scan_ssh_targets(config, timeout)
    heartbeat_rows = scan_heartbeat(config, timeout)
    ses_rows = scan_ses_dns(config, timeout)
    enhance = scan_enhance(config, timeout)

    total_cost = 0.0
    for row in profiles:
        cost = row.get("cost", {})
        if isinstance(cost, dict) and isinstance(cost.get("totalCost"), (int, float)):
            total_cost += float(cost["totalCost"])

    payload = {
        "generatedAt": now_iso(),
        "version": str(config.get("version", DEFAULT_VERSION)),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "summary": {
            "ociProfileCount": len(profiles),
            "ociAuthOkCount": sum(1 for p in profiles if p.get("authOk")),
            "estimatedMonthlyCost": round(total_cost, 6),
            "firewallUnexpectedPublicIngressCount": sum(1 for f in firewall_findings if f.get("unexpected")),
            "crowdsecMissingCount": sum(1 for h in ssh_rows if h.get("enabled") and h.get("ok") and not h.get("crowdsecInstalled")),
            "heartbeatFailures": sum(1 for h in heartbeat_rows if not h.get("ok")),
            "sesDomainFailures": sum(1 for d in ses_rows if not d.get("ok")),
        },
        "ociProfiles": profiles,
        "firewallFindings": firewall_findings,
        "sshHosts": ssh_rows,
        "heartbeat": heartbeat_rows,
        "sesDns": ses_rows,
        "enhance": enhance,
    }
    write_json(args.output, payload)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
