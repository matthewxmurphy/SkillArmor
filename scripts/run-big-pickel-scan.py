#!/usr/bin/env python3
"""Run Big-Pickel trust-growth scan using local JSON config."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_status(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def header_int(headers: dict, key: str) -> int | None:
    raw = headers.get(key)
    if raw is None:
        want = key.lower()
        for header_key, header_value in headers.items():
            if str(header_key).lower() == want:
                raw = header_value
                break
    if raw is None:
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


def parse_json_loose(text: str) -> object | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", raw, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def coerce_findings(payload: object) -> list[dict]:
    if isinstance(payload, list) and payload and all(isinstance(x, dict) for x in payload):
        return payload
    if isinstance(payload, dict):
        for key in ("findings", "results", "items", "skills"):
            value = payload.get(key)
            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                return value
    return []


def default_fallback_prompt(request_payload: dict) -> str:
    return (
        "You are a local ClawHub risk auditor.\n"
        "Return JSON only with this exact schema:\n"
        '{"findings":[{"slug":"", "displayName":"", "owner":{"handle":""}, '
        '"risk":"high|high_operational|medium|review_needed|low", '
        '"reasonCode":"", "summary":"", "evidence":[], '
        '"metrics":{"stars":0,"installsAllTime":0,"downloads":0,"versions":1}, '
        '"suggestedAction":"monitor"}]}\n\n'
        "If uncertain, return an empty findings array.\n"
        "Audit request JSON follows:\n"
        f"{json.dumps(request_payload, ensure_ascii=False)}"
    )


def normalize_base_url(url: str, default_scheme: str = "http") -> str:
    raw = str(url or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        raw = f"{default_scheme}://{raw}"
    return raw.rstrip("/")


def parse_host_from_url(url: str) -> tuple[str, str, int | None]:
    parsed = urlparse(normalize_base_url(url))
    scheme = parsed.scheme or "http"
    host = parsed.hostname or ""
    port = parsed.port
    return scheme, host, port


def extract_model_names(payload: object) -> list[str]:
    names: list[str] = []
    if isinstance(payload, dict):
        for key in ("data", "models"):
            value = payload.get(key)
            if not isinstance(value, list):
                continue
            for item in value:
                if not isinstance(item, dict):
                    continue
                candidate = item.get("id") or item.get("name") or item.get("model")
                if isinstance(candidate, str) and candidate.strip():
                    names.append(candidate.strip())
    out: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def choose_preferred_model(models: list[str], preferred: list[str]) -> str | None:
    available = [str(m).strip() for m in models if isinstance(m, str) and str(m).strip()]
    if not available:
        return None
    wanted = [str(p).strip() for p in preferred if isinstance(p, str) and str(p).strip()]
    if not wanted:
        return None

    available_lower = {name.lower(): name for name in available}
    for pref in wanted:
        exact = available_lower.get(pref.lower())
        if exact:
            return exact

    for pref in wanted:
        pref_l = pref.lower()
        for name in available:
            if pref_l in name.lower():
                return name

    return None


def get_json(url: str, timeout: int) -> tuple[bool, object, int | None, str | None]:
    req = Request(
        url=url,
        method="GET",
        headers={"Accept": "application/json"},
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            payload = parse_json_loose(text)
            if payload is None:
                payload = text
            return True, payload, response.getcode(), None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, body, exc.code, f"HTTP {exc.code}"
    except URLError as exc:
        return False, str(exc), None, f"URLError: {exc}"


def post_json(url: str, payload: dict, timeout: int) -> tuple[bool, object, int | None, str | None]:
    req = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            parsed = parse_json_loose(text)
            if parsed is None:
                parsed = text
            return True, parsed, response.getcode(), None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, body, exc.code, f"HTTP {exc.code}"
    except URLError as exc:
        return False, str(exc), None, f"URLError: {exc}"


def probe_model_endpoint(base_url: str, timeout: int) -> dict | None:
    root = normalize_base_url(base_url)
    if not root:
        return None

    # Prefer OpenAI-compatible endpoints when both are exposed.
    ok, payload, status_code, _ = get_json(f"{root}/v1/models", timeout)
    if ok:
        names = extract_model_names(payload)
        if names:
            return {
                "provider": "openai",
                "baseUrl": root,
                "endpoint": "/v1/chat/completions",
                "model": names[0],
                "models": names,
                "statusCode": status_code,
            }

    ok, payload, status_code, _ = get_json(f"{root}/api/tags", timeout)
    if ok:
        names = extract_model_names(payload)
        if names:
            return {
                "provider": "ollama",
                "baseUrl": root,
                "endpoint": "/api/generate",
                "model": names[0],
                "models": names,
                "statusCode": status_code,
            }

    return None


def discover_model_endpoint(base_url: str, ports: list[int], timeout: int) -> dict | None:
    root = normalize_base_url(base_url)
    if not root:
        return None

    first = probe_model_endpoint(root, timeout)
    if first:
        first["discovered"] = False
        return first

    scheme, host, current_port = parse_host_from_url(root)
    if not host:
        return None

    tried: set[str] = {root}
    for port in ports:
        if port == current_port:
            continue
        candidate = f"{scheme}://{host}:{port}"
        if candidate in tried:
            continue
        tried.add(candidate)
        found = probe_model_endpoint(candidate, timeout)
        if found:
            found["discovered"] = True
            return found

    return None


def extract_model_text(provider: str, payload: object) -> str:
    if provider == "openai" and isinstance(payload, dict):
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message")
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str):
                        return content
                text = first.get("text")
                if isinstance(text, str):
                    return text
    if provider == "ollama" and isinstance(payload, dict):
        response = payload.get("response")
        if isinstance(response, str):
            return response
        message = payload.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
        if isinstance(message, str):
            return message

    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False)


def run_model_request(
    provider: str,
    base_url: str,
    endpoint: str,
    model: str,
    prompt: str,
    timeout: int,
    max_tokens: int,
) -> dict:
    url = f"{normalize_base_url(base_url)}{endpoint}"
    if provider == "openai":
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": max_tokens,
        }
    elif provider == "ollama":
        body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    else:
        return {
            "ok": False,
            "errorType": "unsupported",
            "signal": {
                "id": "fallback_provider_unsupported",
                "level": "high",
                "message": f"Unsupported fallback provider '{provider}'.",
            },
            "url": url,
            "model": model,
        }

    ok, payload, status_code, err = post_json(url, body, timeout)
    if not ok:
        error_type = "connection"
        if isinstance(status_code, int):
            error_type = "http"
        signal_id = "fallback_connection_error" if error_type == "connection" else "fallback_http_error"
        return {
            "ok": False,
            "errorType": error_type,
            "statusCode": status_code,
            "url": url,
            "model": model,
            "provider": provider,
            "errorBody": str(payload)[:5000],
            "signal": {
                "id": signal_id,
                "level": "high",
                "message": (
                    f"Ryzen GPU fallback connection error: {err}"
                    if error_type == "connection"
                    else f"Ryzen GPU fallback returned HTTP {status_code}."
                ),
            },
        }

    model_text = extract_model_text(provider, payload)
    parsed_model = parse_json_loose(model_text)
    findings = coerce_findings(parsed_model)
    return {
        "ok": True,
        "statusCode": status_code,
        "url": url,
        "model": model,
        "provider": provider,
        "rawResponse": payload,
        "modelText": model_text,
        "findings": findings,
    }


def try_ryzen_gpu_fallback(config: dict, request_payload: dict, output_path: Path) -> dict:
    fallback_cfg = config.get("fallback") if isinstance(config, dict) else None
    if not isinstance(fallback_cfg, dict):
        fallback_cfg = {}

    enabled = bool(fallback_cfg.get("enabled", True))
    if not enabled:
        return {"ok": False, "signal": {"id": "fallback_disabled", "level": "high", "message": "Ryzen GPU fallback is disabled in config."}}

    provider = str(fallback_cfg.get("provider", "auto")).strip().lower() or "auto"
    base_url = normalize_base_url(str(fallback_cfg.get("baseUrl", "http://192.168.88.11")))
    endpoint = str(fallback_cfg.get("endpoint", "")).strip()
    timeout = int(fallback_cfg.get("timeoutSeconds", 180))
    max_tokens = int(fallback_cfg.get("maxTokens", 2800))
    configured_model = str(fallback_cfg.get("model", "")).strip()
    model_preferences = fallback_cfg.get("modelPreferences")
    if not isinstance(model_preferences, list):
        model_preferences = []
    preferred_models = [configured_model, *[str(x) for x in model_preferences]]
    discovery_ports = fallback_cfg.get("discoveryPorts")
    if not isinstance(discovery_ports, list):
        discovery_ports = [1234, 11434, 8080]
    normalized_ports = [int(p) for p in discovery_ports if str(p).isdigit()]
    auto_repair = bool(fallback_cfg.get("autoRepair", True))
    prompt = str(fallback_cfg.get("prompt", "")).strip() or default_fallback_prompt(request_payload)

    target: dict | None = None
    if provider == "auto":
        target = discover_model_endpoint(base_url, normalized_ports, timeout)
        if not target:
            return {
                "ok": False,
                "signal": {
                    "id": "fallback_discovery_failed",
                    "level": "high",
                    "message": "Ryzen fallback could not find a live local model API endpoint.",
                },
            }
    else:
        target = {
            "provider": provider,
            "baseUrl": base_url,
            "endpoint": endpoint or ("/v1/chat/completions" if provider == "openai" else "/api/generate"),
            "model": configured_model,
            "discovered": False,
        }

    discovered_models = target.get("models") if isinstance(target, dict) else None
    if isinstance(discovered_models, list):
        preferred = choose_preferred_model(discovered_models, preferred_models)
        if preferred:
            target["model"] = preferred

    if not target.get("model"):
        discovered = discover_model_endpoint(str(target.get("baseUrl")), normalized_ports, timeout)
        if discovered and discovered.get("model"):
            discovered_models = discovered.get("models")
            chosen = discovered.get("model")
            if isinstance(discovered_models, list):
                preferred = choose_preferred_model(discovered_models, preferred_models)
                if preferred:
                    chosen = preferred
            target["model"] = discovered.get("model")
            if not target.get("endpoint"):
                target["endpoint"] = discovered.get("endpoint")
            if provider == "auto":
                target["provider"] = discovered.get("provider")
            target["model"] = chosen

    first = run_model_request(
        provider=str(target.get("provider", provider)),
        base_url=str(target.get("baseUrl", base_url)),
        endpoint=str(target.get("endpoint") or ("/v1/chat/completions" if provider == "openai" else "/api/generate")),
        model=str(target.get("model") or configured_model),
        prompt=prompt,
        timeout=timeout,
        max_tokens=max_tokens,
    )

    repaired = False
    repair_note = ""
    result = first
    if (
        not first.get("ok")
        and first.get("errorType") == "connection"
        and auto_repair
    ):
        discovered = discover_model_endpoint(base_url, normalized_ports, timeout)
        if discovered:
            changed = (
                str(discovered.get("baseUrl")) != str(target.get("baseUrl"))
                or str(discovered.get("provider")) != str(target.get("provider"))
            )
            if changed:
                second = run_model_request(
                    provider=str(discovered.get("provider", "openai")),
                    base_url=str(discovered.get("baseUrl", base_url)),
                    endpoint=str(discovered.get("endpoint") or "/v1/chat/completions"),
                    model=str(discovered.get("model") or configured_model),
                    prompt=prompt,
                    timeout=timeout,
                    max_tokens=max_tokens,
                )
                if second.get("ok"):
                    repaired = True
                    repair_note = (
                        f"Auto-repaired fallback endpoint to {discovered.get('baseUrl')}"
                        f" ({discovered.get('provider')})."
                    )
                    result = second

    if not result.get("ok"):
        return result

    fallback_payload = {
        "source": "ryzen_gpu_fallback",
        "generatedAt": now_iso(),
        "provider": str(result.get("provider")),
        "model": str(result.get("model")),
        "url": str(result.get("url")),
        "statusCode": result.get("statusCode"),
        "findings": result.get("findings", []),
    }
    if repaired:
        fallback_payload["autoRepair"] = repair_note
    if not fallback_payload["findings"]:
        fallback_payload["rawModelOutput"] = str(result.get("modelText", ""))[:5000]

    output_path.write_text(json.dumps(fallback_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {
        "ok": True,
        "statusCode": result.get("statusCode"),
        "url": str(result.get("url")),
        "model": str(result.get("model")),
        "provider": str(result.get("provider")),
        "findingsCount": len(fallback_payload["findings"]),
    }
    if repaired:
        out["autoRepaired"] = True
        out["repairNote"] = repair_note
    return out


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    config_path = data_dir / "big-pickel-search-config.json"
    output_path = data_dir / "big-pickel-last-response.json"
    status_path = data_dir / "big-pickel-scan-status.json"

    if not config_path.exists():
        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "signals": [
                    {
                        "id": "scan_config_missing",
                        "level": "critical",
                        "message": f"Missing config file: {config_path}",
                    }
                ],
            },
        )
        fail(f"Missing config file: {config_path}")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "signals": [
                    {
                        "id": "scan_config_invalid_json",
                        "level": "critical",
                        "message": f"Invalid JSON in {config_path}: {exc}",
                    }
                ],
            },
        )
        fail(f"Invalid JSON in {config_path}: {exc}")

    api = config.get("api", {})
    request_payload = config.get("request")
    base_url = str(api.get("baseUrl", "")).rstrip("/")
    endpoint = str(api.get("endpoint", "")).strip()
    api_key = str(api.get("apiKey", "")).strip()
    scan_mode = str(config.get("scanMode", "prefer_local")).strip().lower()
    if scan_mode not in {"prefer_local", "local_only", "api_first"}:
        scan_mode = "prefer_local"
    pre_api_signals: list[dict] = []
    local_attempted = False

    if not request_payload:
        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "signals": [
                    {
                        "id": "scan_request_missing",
                        "level": "critical",
                        "message": "Config requires request payload.",
                    }
                ],
            },
        )
        fail("Config requires request payload.")

    if scan_mode in {"prefer_local", "local_only"}:
        local_attempted = True
        local = try_ryzen_gpu_fallback(config, request_payload, output_path)
        if local.get("ok"):
            local_msg = (
                f"Used local Ryzen GPU model '{local.get('model')}' via {local.get('provider')} as primary scan engine."
            )
            if local.get("autoRepaired"):
                local_msg += f" {local.get('repairNote', '')}"
            signals = [
                {
                    "id": "local_gpu_primary_used",
                    "level": "low",
                    "message": local_msg.strip(),
                }
            ]
            if scan_mode == "prefer_local":
                signals.append(
                    {
                        "id": "api_skipped_local_preferred",
                        "level": "low",
                        "message": "Primary API skipped because local GPU mode is preferred.",
                    }
                )
            write_status(
                status_path,
                {
                    "generatedAt": now_iso(),
                    "healthy": True,
                    "degraded": False,
                    "source": "ryzen_gpu_primary",
                    "signals": signals,
                    "fallback": {
                        "url": local.get("url"),
                        "model": local.get("model"),
                        "provider": local.get("provider"),
                        "statusCode": local.get("statusCode"),
                        "findingsCount": local.get("findingsCount"),
                    },
                },
            )
            print(f"Used local GPU primary model {local.get('model')}; Big-Pickel API skipped.")
            print(f"Saved local response: {output_path}")
            print(f"Saved scan status: {status_path}")
            return

        if local.get("signal"):
            pre_api_signals.append(local["signal"])

        if scan_mode == "local_only":
            write_status(
                status_path,
                {
                    "generatedAt": now_iso(),
                    "healthy": False,
                    "source": "local_only",
                    "signals": pre_api_signals
                    + [
                        {
                            "id": "api_skipped_local_only",
                            "level": "high",
                            "message": "API scan skipped because scanMode=local_only and local GPU was unavailable.",
                        }
                    ],
                },
            )
            fail(f"Local-only mode failed (details stored in {status_path})", code=4)

    if not base_url or not endpoint:
        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "signals": pre_api_signals
                + [
                    {
                        "id": "scan_endpoint_missing",
                        "level": "critical",
                        "message": "Config requires api.baseUrl and api.endpoint.",
                    }
                ],
            },
        )
        fail("Config requires api.baseUrl and api.endpoint.")
    if not api_key or api_key == "PASTE_KEY_HERE":
        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "signals": pre_api_signals
                + [
                    {
                        "id": "api_key_missing",
                        "level": "critical",
                        "message": "Set api.apiKey in data/big-pickel-search-config.json before running.",
                    }
                ],
            },
        )
        fail("Set api.apiKey in data/big-pickel-search-config.json before running.")

    url = f"{base_url}{endpoint}"
    body = json.dumps(request_payload).encode("utf-8")
    req = Request(
        url=url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=180) as response:
            response_text = response.read().decode("utf-8", errors="replace")
            status_code = response.getcode()
            headers = dict(response.headers.items())
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        error_body_lc = error_body.lower()
        headers = dict(exc.headers.items()) if exc.headers else {}
        signals = []
        if exc.code == 401:
            signals.append(
                {
                    "id": "api_auth_failed",
                    "level": "critical",
                    "message": "Big-Pickel API rejected credentials (HTTP 401). Check API key.",
                }
            )
        if exc.code == 403:
            if "cloudflare" in error_body_lc or "error 1010" in error_body_lc or "access denied" in error_body_lc:
                signals.append(
                    {
                        "id": "api_access_blocked",
                        "level": "critical",
                        "message": "Big-Pickel API request blocked by upstream access controls (Cloudflare/WAF).",
                    }
                )
            else:
                signals.append(
                    {
                        "id": "api_permission_denied",
                        "level": "critical",
                        "message": "Big-Pickel API denied request (HTTP 403). Check key scope/permissions.",
                    }
                )
        if exc.code == 429:
            signals.append(
                {
                    "id": "api_rate_limited",
                    "level": "high",
                    "message": "Big-Pickel API rate limited (HTTP 429).",
                }
            )
        remaining = header_int(headers, "x-ratelimit-remaining")
        if remaining is not None and remaining <= 0:
            signals.append(
                {
                    "id": "api_rate_limit_exhausted",
                    "level": "high",
                    "message": "Big-Pickel API rate limit remaining is 0.",
                }
            )
        if not signals:
            signals.append(
                {
                    "id": "api_http_error",
                    "level": "high",
                    "message": f"Big-Pickel API returned HTTP {exc.code}.",
                }
            )

        fallback = {}
        if not local_attempted:
            fallback = try_ryzen_gpu_fallback(config, request_payload, output_path)
        if fallback.get("ok"):
            fallback_msg = (
                f"Primary API failed; fallback used Ryzen GPU model '{fallback.get('model')}'"
                f" via {fallback.get('provider')}."
            )
            if fallback.get("autoRepaired"):
                fallback_msg += f" {fallback.get('repairNote', '')}"
            signals.append(
                {
                    "id": "fallback_ryzen_gpu_used",
                    "level": "medium",
                    "message": fallback_msg.strip(),
                }
            )
            write_status(
                status_path,
                {
                    "generatedAt": now_iso(),
                    "healthy": True,
                    "degraded": True,
                    "source": "ryzen_gpu_fallback",
                    "url": url,
                    "statusCode": exc.code,
                    "rateLimitRemaining": remaining,
                    "rateLimitReset": header_int(headers, "x-ratelimit-reset"),
                    "retryAfterSeconds": header_int(headers, "retry-after"),
                    "signals": signals,
                    "fallback": {
                        "url": fallback.get("url"),
                        "model": fallback.get("model"),
                        "statusCode": fallback.get("statusCode"),
                        "findingsCount": fallback.get("findingsCount"),
                    },
                },
            )
            print(f"Primary API failed (HTTP {exc.code}); used fallback model {fallback.get('model')}")
            print(f"Saved fallback response: {output_path}")
            print(f"Saved scan status: {status_path}")
            return
        if fallback.get("signal"):
            signals.append(fallback["signal"])
        if pre_api_signals:
            signals = [*pre_api_signals, *signals]

        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "url": url,
                "statusCode": exc.code,
                "rateLimitRemaining": remaining,
                "rateLimitReset": header_int(headers, "x-ratelimit-reset"),
                "retryAfterSeconds": header_int(headers, "retry-after"),
                "signals": signals,
                "errorBody": error_body[:5000],
                "fallbackErrorBody": fallback.get("errorBody"),
            },
        )
        fail(f"HTTP {exc.code} from {url} (details stored in {status_path})", code=2)
    except URLError as exc:
        fallback = {}
        if not local_attempted:
            fallback = try_ryzen_gpu_fallback(config, request_payload, output_path)
        if fallback.get("ok"):
            fallback_msg = (
                f"Used Ryzen GPU fallback model '{fallback.get('model')}'"
                f" via {fallback.get('provider')}."
            )
            if fallback.get("autoRepaired"):
                fallback_msg += f" {fallback.get('repairNote', '')}"
            signals = [
                {
                    "id": "api_connection_error",
                    "level": "high",
                    "message": f"Primary API connection error for {url}: {exc}",
                },
                {
                    "id": "fallback_ryzen_gpu_used",
                    "level": "medium",
                    "message": fallback_msg.strip(),
                },
            ]
            write_status(
                status_path,
                {
                    "generatedAt": now_iso(),
                    "healthy": True,
                    "degraded": True,
                    "source": "ryzen_gpu_fallback",
                    "url": url,
                    "signals": signals,
                    "fallback": {
                        "url": fallback.get("url"),
                        "model": fallback.get("model"),
                        "statusCode": fallback.get("statusCode"),
                        "findingsCount": fallback.get("findingsCount"),
                    },
                },
            )
            print(f"Primary API connection failed; used fallback model {fallback.get('model')}")
            print(f"Saved fallback response: {output_path}")
            print(f"Saved scan status: {status_path}")
            return

        failure_signals = [
            {
                "id": "api_connection_error",
                "level": "high",
                "message": f"Connection error for {url}: {exc}",
            }
        ]
        if fallback.get("signal"):
            failure_signals.append(fallback["signal"])
        if pre_api_signals:
            failure_signals = [*pre_api_signals, *failure_signals]
        write_status(
            status_path,
            {
                "generatedAt": now_iso(),
                "healthy": False,
                "url": url,
                "signals": failure_signals,
            },
        )
        fail(f"Connection error for {url}: {exc}", code=3)

    output_path.write_text(response_text, encoding="utf-8")
    remaining = header_int(headers, "x-ratelimit-remaining")
    status_signals = [*pre_api_signals]
    if remaining is not None and remaining <= 3:
        status_signals.append(
            {
                "id": "api_rate_limit_low",
                "level": "medium",
                "message": f"Big-Pickel API rate limit is low ({remaining} remaining).",
            }
        )
    write_status(
        status_path,
        {
            "generatedAt": now_iso(),
            "healthy": True,
            "degraded": bool(pre_api_signals),
            "source": "big_pickel_api",
            "url": url,
            "statusCode": status_code,
            "rateLimitRemaining": remaining,
            "rateLimitReset": header_int(headers, "x-ratelimit-reset"),
            "signals": status_signals,
        },
    )
    print(f"POST {url}")
    print(f"Status: {status_code}")
    print(f"Saved response: {output_path}")
    print(f"Saved scan status: {status_path}")


if __name__ == "__main__":
    main()
