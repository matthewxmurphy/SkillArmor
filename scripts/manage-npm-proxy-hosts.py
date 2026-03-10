#!/usr/bin/env python3
"""Upsert Nginx Proxy Manager hosts from JSON config and optionally wire local wildcard DNS."""

from __future__ import annotations

import argparse
import json
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "data" / "npm-proxy-manager-config.json"
DEFAULT_OUT = ROOT / "data" / "npm-proxy-last-sync.json"
VERSION = "0.5.0"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_api_base(url: str) -> str:
    cleaned = (url or "").strip().rstrip("/")
    if not cleaned:
        raise ValueError("npm.baseUrl is required")
    if cleaned.endswith("/api"):
        return cleaned
    return cleaned + "/api"


def req_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None,
    token: str | None,
    timeout: int,
    verify_tls: bool,
) -> dict[str, Any] | list[Any]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = Request(url=url, data=body, headers=headers, method=method)
    ctx = None
    if url.startswith("https://") and not verify_tls:
        ctx = ssl._create_unverified_context()

    try:
        with urlopen(req, timeout=timeout, context=ctx) as res:
            raw = res.read().decode("utf-8")
    except HTTPError as exc:
        msg = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed ({exc.code}): {msg[:400]}") from exc
    except URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc}") from exc

    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{method} {url} returned non-JSON response") from exc


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_secret(env_name: str) -> str:
    import os

    value = os.environ.get(env_name, "").strip()
    if not value:
        raise ValueError(f"Missing environment secret: {env_name}")
    return value


def fqdn_for_host(row: dict[str, Any], suffix: str) -> str:
    domain = str(row.get("domain", "")).strip().lower()
    if domain:
        return domain
    subdomain = str(row.get("subdomain", "")).strip().lower()
    if not subdomain:
        raise ValueError("host row requires domain or subdomain")
    if not suffix:
        raise ValueError("localDns.domainSuffix is required when using subdomain entries")
    return f"{subdomain}.{suffix}"


def build_payload(row: dict[str, Any], defaults: dict[str, Any], domain_suffix: str) -> dict[str, Any]:
    fqdn = fqdn_for_host(row, domain_suffix)
    forward_host = str(row.get("forwardHost", "")).strip()
    if not forward_host:
        raise ValueError(f"{fqdn}: forwardHost is required")

    try:
        forward_port = int(row.get("forwardPort"))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{fqdn}: forwardPort must be an integer") from exc

    if forward_port < 1 or forward_port > 65535:
        raise ValueError(f"{fqdn}: forwardPort out of range")

    payload = {
        "domain_names": [fqdn],
        "forward_scheme": str(row.get("scheme") or defaults.get("scheme") or "http").strip().lower(),
        "forward_host": forward_host,
        "forward_port": forward_port,
        "access_list_id": int(row.get("accessListId", defaults.get("accessListId", 0)) or 0),
        "certificate_id": int(row.get("certificateId", defaults.get("certificateId", 0)) or 0),
        "ssl_forced": as_bool(row.get("sslForced", defaults.get("sslForced", False))),
        "http2_support": as_bool(row.get("http2Support", defaults.get("http2Support", False))),
        "hsts_enabled": as_bool(row.get("hstsEnabled", defaults.get("hstsEnabled", False))),
        "hsts_subdomains": as_bool(row.get("hstsSubdomains", defaults.get("hstsSubdomains", False))),
        "block_exploits": as_bool(row.get("blockExploits", defaults.get("blockExploits", True)), default=True),
        "caching_enabled": as_bool(row.get("cacheAssets", defaults.get("cacheAssets", False))),
        "allow_websocket_upgrade": as_bool(
            row.get("websocketSupport", defaults.get("websocketSupport", True)),
            default=True,
        ),
        "advanced_config": str(row.get("advancedConfig", "") or ""),
        "meta": {
            "letsencrypt_agree": False,
            "dns_challenge": False,
        },
        "locations": [],
        "enabled": as_bool(row.get("enabled", True), default=True),
    }
    return payload


def apply_dns_wildcard(local_dns: dict[str, Any]) -> dict[str, str]:
    suffix = str(local_dns.get("domainSuffix", "")).strip()
    target_ip = str(local_dns.get("targetIp", "")).strip()
    dnsmasq_cfg = Path(str(local_dns.get("dnsmasqConfigPath", "/opt/homebrew/etc/dnsmasq.d/m1-local.conf")))
    resolver_dir = Path(str(local_dns.get("resolverDir", "/etc/resolver")))
    resolver_file_name = str(local_dns.get("resolverFile", suffix or "m1.local")).strip()
    if not suffix:
        raise ValueError("localDns.domainSuffix is required")
    if not target_ip:
        raise ValueError("localDns.targetIp is required")
    if not resolver_file_name:
        raise ValueError("localDns.resolverFile is required")

    dnsmasq_cfg.parent.mkdir(parents=True, exist_ok=True)
    resolver_dir.mkdir(parents=True, exist_ok=True)
    resolver_file = resolver_dir / resolver_file_name

    dnsmasq_cfg.write_text(
        (
            "# Generated by manage-npm-proxy-hosts.py\n"
            f"# {now_iso()}\n"
            f"address=/.{suffix}/{target_ip}\n"
        ),
        encoding="utf-8",
    )
    resolver_file.write_text(
        (
            "# Generated by manage-npm-proxy-hosts.py\n"
            f"# {now_iso()}\n"
            "nameserver 127.0.0.1\n"
        ),
        encoding="utf-8",
    )
    return {
        "dnsmasqConfigPath": str(dnsmasq_cfg),
        "resolverFile": str(resolver_file),
        "notes": "Run `brew services restart dnsmasq` on macOS after changes.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    parser.add_argument("--apply-dns", action="store_true")
    args = parser.parse_args()

    cfg = load_json(Path(args.config))
    npm_cfg = cfg.get("npm", {})
    local_dns = cfg.get("localDns", {})
    defaults = cfg.get("defaults", {})
    hosts = cfg.get("hosts", [])
    timeout = int(cfg.get("scan", {}).get("timeoutSeconds", 25))
    verify_tls = as_bool(npm_cfg.get("verifyTls", True), default=True)

    api_base = normalize_api_base(str(npm_cfg.get("baseUrl", "")))
    identity = str(npm_cfg.get("identity", "")).strip()
    secret_env = str(npm_cfg.get("secretEnv", "NPM_API_PASSWORD")).strip()
    domain_suffix = str(local_dns.get("domainSuffix", "m1.local")).strip().lower()
    if not identity:
        raise ValueError("npm.identity is required")
    if not isinstance(hosts, list):
        raise ValueError("hosts must be a list")

    token_resp = req_json(
        "POST",
        f"{api_base}/tokens",
        payload={"identity": identity, "secret": read_secret(secret_env)},
        token=None,
        timeout=timeout,
        verify_tls=verify_tls,
    )
    token = str((token_resp or {}).get("token", "")).strip()
    if not token:
        raise RuntimeError("NPM auth succeeded but no token was returned")

    existing_raw = req_json(
        "GET",
        f"{api_base}/nginx/proxy-hosts",
        payload=None,
        token=token,
        timeout=timeout,
        verify_tls=verify_tls,
    )
    existing_rows = existing_raw if isinstance(existing_raw, list) else []
    existing_by_domain: dict[str, dict[str, Any]] = {}
    for row in existing_rows:
        for domain in row.get("domain_names", []) or []:
            existing_by_domain[str(domain).strip().lower()] = row

    actions: list[dict[str, Any]] = []
    for row in hosts:
        payload = build_payload(row, defaults, domain_suffix)
        fqdn = payload["domain_names"][0]
        current = existing_by_domain.get(fqdn)
        if current:
            host_id = int(current.get("id"))
            req_json(
                "PUT",
                f"{api_base}/nginx/proxy-hosts/{host_id}",
                payload=payload,
                token=token,
                timeout=timeout,
                verify_tls=verify_tls,
            )
            actions.append({"domain": fqdn, "action": "updated", "id": host_id})
        else:
            created = req_json(
                "POST",
                f"{api_base}/nginx/proxy-hosts",
                payload=payload,
                token=token,
                timeout=timeout,
                verify_tls=verify_tls,
            )
            actions.append({"domain": fqdn, "action": "created", "id": created.get("id")})

    dns_result: dict[str, str] | None = None
    if args.apply_dns:
        dns_result = apply_dns_wildcard(local_dns)

    out = {
        "generatedAt": now_iso(),
        "version": VERSION,
        "apiBase": api_base,
        "domainSuffix": domain_suffix,
        "appliedDns": bool(args.apply_dns),
        "dnsResult": dns_result,
        "count": len(actions),
        "actions": actions,
    }
    write_json(Path(args.output), out)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
