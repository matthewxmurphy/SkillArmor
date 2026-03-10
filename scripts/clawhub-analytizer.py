#!/usr/bin/env python3
"""ClawHub Analytizer pipeline.

This script can:
1) Optionally run the Big-Pickel scan API.
2) Normalize and merge findings into audit-findings.json.
3) Regenerate AUDIT.md summary.
4) Regenerate SKILLS-TODO.md action queue.
5) Refresh dashboard/browser-data.js for dashboard/browser.html.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


RISK_ORDER = {
    "high": 5,
    "high_operational": 4,
    "medium": 3,
    "review_needed": 2,
    "low": 1,
}

SIGNAL_LEVEL_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "none": 0,
}

AUTO_COMMENTS_DEFAULT = {
    "shell_passthrough_blacklist": (
        "I reviewed this skill locally. The implementation executes raw shell commands "
        "through tmux and relies on blacklist-only filtering for dangerous commands. "
        "That pattern is bypassable and risky for destructive execution. Please move "
        "to an allowlist or explicit per-command approval model before this should be considered trusted."
    ),
    "secret_in_argv": (
        "I reviewed this code and found a secret-handling risk: API keys are accepted "
        "in CLI arguments/examples. Secrets passed in argv can leak through shell history "
        "and process listings. Please enforce env-only secret input and avoid API key argv patterns."
    ),
    "high_stakes_finance": (
        "I do not see obvious malware behavior in this pass, but this skill can trigger "
        "high-stakes on-chain financial actions. It should be clearly labeled as financial-risk "
        "automation and include mandatory simulation/dry-run plus explicit confirmation before any live transaction."
    ),
}

PUBLIC_INDEX_BASE_URL = "https://wry-manatee-359.convex.site"
PUBLIC_INDEX_USER_AGENT = "OpenClaw-Analytizer/1.0"

OPERATIONAL_KEYWORDS = (
    "wallet",
    "onchain",
    "on-chain",
    "token",
    "swap",
    "bridge",
    "solana",
    "ethereum",
    "dex",
    "trade",
    "private key",
)
HIGH_EXEC_KEYWORDS = (
    "shell",
    "terminal",
    "tmux",
    "exec",
    "command execution",
    "bash",
    "sudo",
    "child_process",
)
MEDIUM_SECRET_KEYWORDS = (
    "api key",
    "secret",
    "oauth",
    "auth token",
    "bearer",
)
DEFENSIVE_KEYWORDS = (
    "security scanner",
    "hardening",
    "allowlist",
    "safe execution",
    "audit",
)

RUNTIME_INFO_SIGNAL_IDS = {
    "local_gpu_primary_used",
    "api_skipped_local_preferred",
    "public_index_ingested",
    "fallback_ryzen_gpu_used",
}


def now_ts() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "unknown-skill"


def uniq_str(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = str(value).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def normalize_risk(raw: Any) -> str:
    value = str(raw or "").strip().lower()
    if not value:
        return "review_needed"
    if value in {"critical", "very_high", "severe"}:
        return "high"
    if value in {"high", "high_risk", "danger"}:
        return "high"
    if value in {"high-operational", "high_operational", "operational", "financial"}:
        return "high_operational"
    if value in {"medium", "moderate", "med"}:
        return "medium"
    if value in {"review_needed", "review", "needs_review"}:
        return "review_needed"
    if value in {"low", "safe", "defensive", "info"}:
        return "low"
    return "review_needed"


def risk_rank(risk: str) -> int:
    return RISK_ORDER.get(risk, 0)


def default_action_for_risk(risk: str) -> str:
    if risk == "high":
        return "comment_and_rebuild_candidate"
    if risk == "high_operational":
        return "monitor_and_comment"
    if risk == "medium":
        return "comment_and_rebuild_candidate"
    if risk == "review_needed":
        return "deep_review_queue"
    return "monitor"


def signal_level_from_score(score: int) -> str:
    if score >= 8:
        return "critical"
    if score >= 6:
        return "high"
    if score >= 4:
        return "medium"
    if score >= 1:
        return "low"
    return "none"


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_days(iso_value: str | None) -> int | None:
    dt = parse_iso_datetime(iso_value)
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (now - dt).days)


def fetch_github_user(handle: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Return (profile, error). error is a dict when profile fetch failed."""
    url = f"https://api.github.com/users/{quote(handle, safe='')}"
    req = Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "OpenClaw-Analytizer/1.0",
        },
    )
    try:
        with urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
            return payload, None
    except HTTPError as exc:
        return None, {"httpStatus": exc.code, "message": f"GitHub API HTTP {exc.code}"}
    except URLError as exc:
        return None, {"httpStatus": None, "message": f"GitHub API connection error: {exc}"}
    except json.JSONDecodeError:
        return None, {"httpStatus": None, "message": "GitHub API returned invalid JSON"}


def load_owner_cache(path: Path) -> dict[str, Any]:
    default = {"generatedAt": now_iso(), "users": {}}
    if not path.exists():
        return default
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
    if not isinstance(payload, dict):
        return default
    users = payload.get("users")
    if not isinstance(users, dict):
        users = {}
    return {"generatedAt": payload.get("generatedAt", now_iso()), "users": users}


def save_owner_cache(path: Path, cache: dict[str, Any]) -> None:
    path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compute_owner_profile_signal(handle: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Compute owner signal from GitHub profile/cache entry."""
    flags: list[str] = []
    score = 0
    profile = entry.get("profile") if isinstance(entry, dict) else None
    status = str(entry.get("status", "error"))
    error = entry.get("error", {})

    if not handle or handle == "unknown":
        return {
            "signalLevel": "high",
            "signalScore": 5,
            "flags": ["owner_handle_missing"],
            "profile": {"exists": False},
        }

    if status != "ok" or not isinstance(profile, dict):
        http_status = safe_int(error.get("httpStatus"), default=0) if isinstance(error, dict) else 0
        if http_status == 404:
            score += 5
            flags.append("github_profile_not_found")
        elif http_status in {403, 429}:
            score += 3
            flags.append("github_profile_rate_limited")
        else:
            score += 2
            flags.append("github_profile_unreachable")
        return {
            "signalLevel": signal_level_from_score(score),
            "signalScore": score,
            "flags": flags,
            "profile": {"exists": False},
        }

    public_repos = safe_int(profile.get("public_repos"))
    followers = safe_int(profile.get("followers"))
    created_at = str(profile.get("created_at") or "")
    updated_at = str(profile.get("updated_at") or "")
    name = str(profile.get("name") or "").strip()
    bio = str(profile.get("bio") or "").strip()
    blog = str(profile.get("blog") or "").strip()
    location = str(profile.get("location") or "").strip()
    avatar_url = str(profile.get("avatar_url") or "")
    account_age = age_days(created_at)
    stale_age = age_days(updated_at)

    # Identity quality signals from public profile data.
    if account_age is not None and account_age < 30:
        score += 3
        flags.append("new_github_account")
    elif account_age is not None and account_age < 120:
        score += 1
        flags.append("young_github_account")

    if public_repos == 0:
        score += 3
        flags.append("no_public_repos")
    elif public_repos <= 2:
        score += 1
        flags.append("very_few_public_repos")

    if followers == 0:
        score += 1
        flags.append("no_followers")

    blank_fields = sum(1 for v in (name, bio, blog, location) if not v)
    if blank_fields >= 4:
        score += 2
        flags.append("sparse_public_profile")
    elif blank_fields >= 2:
        score += 1
        flags.append("partial_public_profile")

    if stale_age is not None and stale_age > 730 and public_repos < 5:
        score += 1
        flags.append("stale_profile_activity")

    # GitHub does not provide a direct "default avatar" flag; use a conservative heuristic.
    if (
        "avatars.githubusercontent.com/u/" in avatar_url
        and public_repos <= 1
        and not name
        and not bio
    ):
        score += 1
        flags.append("avatar_generic_possible")

    return {
        "signalLevel": signal_level_from_score(score),
        "signalScore": score,
        "flags": flags,
        "profile": {
            "exists": True,
            "publicRepos": public_repos,
            "followers": followers,
            "createdAt": created_at,
            "updatedAt": updated_at,
            "namePresent": bool(name),
            "bioPresent": bool(bio),
            "avatarUrl": avatar_url,
        },
    }


def enrich_findings_with_owner_signals(
    findings: list[dict[str, Any]], cache_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cache = load_owner_cache(cache_path)
    users = cache.get("users", {})
    if not isinstance(users, dict):
        users = {}
    cache_ttl_seconds = 86400
    now = datetime.now(timezone.utc)

    for finding in findings:
        handle = str(finding.get("owner", {}).get("handle", "unknown"))
        if bool(finding.get("ownerUnknownFromSource")) and handle == "unknown":
            finding["ownerSignals"] = []
            finding["ownerSignalLevel"] = "none"
            finding["ownerSignalScore"] = 0
            finding["ownerProfile"] = {"exists": False, "source": "public_index_no_owner"}
            continue
        cache_entry = users.get(handle)
        use_cache = False
        if isinstance(cache_entry, dict):
            fetched = parse_iso_datetime(str(cache_entry.get("fetchedAt") or ""))
            if fetched is not None:
                if fetched.tzinfo is None:
                    fetched = fetched.replace(tzinfo=timezone.utc)
                age = (now - fetched).total_seconds()
                use_cache = age <= cache_ttl_seconds

        if not use_cache:
            profile, error = fetch_github_user(handle)
            cache_entry = {
                "fetchedAt": now_iso(),
                "status": "ok" if profile is not None else "error",
                "profile": profile,
                "error": error,
            }
            users[handle] = cache_entry

        owner_signal = compute_owner_profile_signal(handle, cache_entry or {})
        finding["ownerSignals"] = owner_signal["flags"]
        finding["ownerSignalLevel"] = owner_signal["signalLevel"]
        finding["ownerSignalScore"] = owner_signal["signalScore"]
        finding["ownerProfile"] = owner_signal["profile"]

    cache["generatedAt"] = now_iso()
    cache["users"] = users
    save_owner_cache(cache_path, cache)
    return findings, cache


def compute_finding_signal(finding: dict[str, Any]) -> dict[str, Any]:
    score = risk_rank(str(finding.get("risk", "low")))
    reasons: list[str] = []
    reason_code = str(finding.get("reasonCode", ""))
    metrics = finding.get("metrics", {})
    versions = safe_int(metrics.get("versions"))
    evidence = finding.get("evidence") or []

    if reason_code == "shell_passthrough_blacklist":
        score += 2
        reasons.append("harmful_shell_passthrough_pattern")
    elif reason_code == "secret_in_argv":
        score += 1
        reasons.append("secret_exposure_pattern")
    elif reason_code == "high_stakes_finance":
        score += 1
        reasons.append("high_stakes_finance_automation")

    if versions <= 1:
        score += 1
        reasons.append("single_release_skill")

    if not any(str(path).endswith("/SKILL.md") for path in evidence):
        score += 1
        reasons.append("missing_skill_markdown_in_sample")

    owner_score = safe_int(finding.get("ownerSignalScore"))
    if owner_score:
        score += owner_score
        reasons.extend(str(x) for x in (finding.get("ownerSignals") or []))

    level = signal_level_from_score(score)
    return {"signalScore": score, "signalLevel": level, "signalReasons": uniq_str(reasons)}


def apply_finding_signals(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for finding in findings:
        computed = compute_finding_signal(finding)
        finding["signalScore"] = computed["signalScore"]
        finding["signalLevel"] = computed["signalLevel"]
        finding["signalReasons"] = computed["signalReasons"]

    findings.sort(
        key=lambda f: (
            -safe_int(f.get("signalScore")),
            -risk_rank(str(f.get("risk", ""))),
            -safe_int(f.get("metrics", {}).get("installsAllTime")),
            -safe_int(f.get("metrics", {}).get("downloads")),
            str(f.get("slug", "")),
        )
    )
    return findings


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch_public_skills_index(
    base_url: str,
    limit: int,
    max_pages: int,
    sort: str,
    direction: str,
    timeout: int = 20,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base = str(base_url or PUBLIC_INDEX_BASE_URL).rstrip("/")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor: str | None = None
    pages = 0
    error: str | None = None

    while pages < max_pages:
        params: dict[str, str | int] = {"limit": limit, "sort": sort, "dir": direction}
        if cursor:
            params["cursor"] = cursor
        url = f"{base}/api/v1/skills?{urlencode(params)}"
        req = Request(
            url=url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": PUBLIC_INDEX_USER_AGENT,
            },
        )
        try:
            with urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            error = f"public index fetch failed on page {pages + 1}: {exc}"
            break

        page_items = payload.get("items", []) if isinstance(payload, dict) else []
        if not isinstance(page_items, list):
            error = f"public index returned invalid items payload on page {pages + 1}"
            break

        added = 0
        for item in page_items:
            if not isinstance(item, dict):
                continue
            slug = slugify(str(item.get("slug") or item.get("id") or ""))
            if not slug or slug in seen:
                continue
            seen.add(slug)
            items.append(item)
            added += 1

        pages += 1
        next_cursor = payload.get("nextCursor") if isinstance(payload, dict) else None
        if not isinstance(next_cursor, str) or not next_cursor.strip():
            break
        if added == 0:
            break
        cursor = next_cursor

    meta = {
        "baseUrl": base,
        "pagesFetched": pages,
        "itemsFetched": len(items),
        "error": error,
    }
    return items, meta


def classify_public_risk(text: str) -> tuple[str, str]:
    t = str(text or "").lower()
    if any(k in t for k in OPERATIONAL_KEYWORDS):
        return "high_operational", "high_stakes_finance"
    if any(k in t for k in HIGH_EXEC_KEYWORDS):
        return "high", "shell_passthrough_blacklist"
    if any(k in t for k in MEDIUM_SECRET_KEYWORDS):
        return "medium", "secret_in_argv"
    if any(k in t for k in DEFENSIVE_KEYWORDS):
        return "low", "defensive_pattern"
    return "review_needed", "public_index_coverage"


def public_skill_to_finding(item: dict[str, Any]) -> dict[str, Any]:
    slug = slugify(str(item.get("slug") or item.get("id") or ""))
    display_name = str(item.get("displayName") or item.get("name") or slug)
    summary = str(item.get("summary") or "").strip()
    latest = item.get("latestVersion") if isinstance(item.get("latestVersion"), dict) else {}
    changelog = str(latest.get("changelog") or "").strip()
    risk, reason_code = classify_public_risk(" ".join([slug, display_name, summary, changelog]))
    stats = item.get("stats") if isinstance(item.get("stats"), dict) else {}

    return {
        "slug": slug,
        "displayName": display_name,
        "owner": {"handle": "unknown", "userId": ""},
        "ownerUnknownFromSource": True,
        "risk": risk,
        "reasonCode": reason_code,
        "summary": summary or "Imported from ClawHub public index for coverage expansion.",
        "evidence": [f"public_api:/api/v1/skills/{slug}"],
        "metrics": {
            "stars": safe_int(stats.get("stars")),
            "installsAllTime": safe_int(stats.get("installsAllTime")),
            "installsCurrent": safe_int(stats.get("installsCurrent")),
            "downloads": safe_int(stats.get("downloads")),
            "versions": safe_int(stats.get("versions")),
        },
        "suggestedAction": default_action_for_risk(risk),
    }

def pick_list_from_response(node: Any) -> list[dict[str, Any]]:
    """Find the most likely findings list inside unknown response JSON."""
    candidates: list[list[dict[str, Any]]] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for value in x.values():
                walk(value)
        elif isinstance(x, list):
            if x and all(isinstance(item, dict) for item in x):
                candidates.append(x)  # keep for scoring
            for item in x:
                walk(item)

    walk(node)

    if not candidates:
        return []

    keys_hint = {
        "slug",
        "name",
        "displayName",
        "title",
        "risk",
        "severity",
        "owner",
        "summary",
        "description",
    }

    def score(items: list[dict[str, Any]]) -> int:
        total = 0
        for item in items:
            present = sum(1 for key in keys_hint if key in item)
            if present:
                total += present
        return total

    candidates.sort(key=score, reverse=True)
    return candidates[0]


def flatten_str_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                for key in ("path", "file", "source", "value"):
                    if key in item and isinstance(item[key], str):
                        out.append(item[key])
                        break
        return out
    return []


def normalize_owner(item: dict[str, Any]) -> dict[str, str]:
    owner = item.get("owner")
    if isinstance(owner, dict):
        handle = (
            owner.get("handle")
            or owner.get("login")
            or owner.get("username")
            or owner.get("name")
            or "unknown"
        )
        uid = owner.get("userId") or owner.get("id") or ""
        return {"handle": str(handle), "userId": str(uid)}

    for key in ("ownerHandle", "author", "publisher", "maintainer", "user"):
        raw = item.get(key)
        if isinstance(raw, str) and raw.strip():
            return {"handle": raw.strip(), "userId": ""}
        if isinstance(raw, dict):
            handle = raw.get("handle") or raw.get("login") or raw.get("username")
            if handle:
                return {"handle": str(handle), "userId": str(raw.get("id", ""))}

    return {"handle": "unknown", "userId": ""}


def normalize_metrics(item: dict[str, Any]) -> dict[str, int]:
    metrics = item.get("metrics")
    data = metrics if isinstance(metrics, dict) else item
    return {
        "stars": safe_int(data.get("stars")),
        "installsAllTime": safe_int(
            data.get("installsAllTime", data.get("installs", data.get("installCount")))
        ),
        "installsCurrent": safe_int(data.get("installsCurrent")),
        "downloads": safe_int(data.get("downloads", data.get("downloadCount"))),
        "versions": safe_int(data.get("versions", data.get("versionCount"))),
    }


def normalize_finding(item: dict[str, Any]) -> dict[str, Any]:
    raw_slug = (
        item.get("slug")
        or item.get("id")
        or item.get("skillSlug")
        or item.get("name")
        or item.get("title")
    )
    slug = slugify(str(raw_slug or ""))
    display_name = str(item.get("displayName") or item.get("name") or item.get("title") or slug)
    risk = normalize_risk(item.get("risk") or item.get("severity") or item.get("level"))
    reason_code = str(item.get("reasonCode") or item.get("rule") or "imported_from_big_pickel")
    summary = str(item.get("summary") or item.get("description") or item.get("reason") or "").strip()

    evidence = []
    for key in ("evidence", "files", "paths", "sources"):
        evidence.extend(flatten_str_list(item.get(key)))

    owner = normalize_owner(item)
    metrics = normalize_metrics(item)
    suggested_action = str(item.get("suggestedAction") or default_action_for_risk(risk))

    return {
        "slug": slug,
        "displayName": display_name,
        "owner": owner,
        "ownerUnknownFromSource": bool(item.get("ownerUnknownFromSource", False)),
        "risk": risk,
        "reasonCode": reason_code,
        "summary": summary or "Imported from Big-Pickel scan.",
        "evidence": uniq_str(evidence),
        "metrics": metrics,
        "suggestedAction": suggested_action,
    }


def merge_findings(
    existing: list[dict[str, Any]], incoming: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_slug: dict[str, dict[str, Any]] = {f["slug"]: dict(f) for f in existing if f.get("slug")}

    for raw in incoming:
        candidate = normalize_finding(raw)
        slug = candidate["slug"]
        if slug not in by_slug:
            by_slug[slug] = candidate
            continue

        base = by_slug[slug]
        # Keep highest risk.
        if risk_rank(candidate["risk"]) > risk_rank(str(base.get("risk", ""))):
            base["risk"] = candidate["risk"]
            base["reasonCode"] = candidate["reasonCode"]
            base["summary"] = candidate["summary"]
            base["suggestedAction"] = candidate["suggestedAction"]

        # Fill sparse fields.
        if not base.get("displayName") or base["displayName"] == slug:
            base["displayName"] = candidate["displayName"]
        if base.get("owner", {}).get("handle", "unknown") == "unknown":
            base["owner"] = candidate["owner"]
        if candidate.get("ownerUnknownFromSource") and base.get("owner", {}).get("handle", "unknown") == "unknown":
            base["ownerUnknownFromSource"] = True
        if base.get("owner", {}).get("handle", "unknown") != "unknown":
            base["ownerUnknownFromSource"] = False
        if candidate.get("summary") and len(candidate["summary"]) > len(str(base.get("summary", ""))):
            base["summary"] = candidate["summary"]

        # Merge metrics by max.
        merged_metrics = dict(base.get("metrics", {}))
        for metric_key, metric_val in candidate.get("metrics", {}).items():
            merged_metrics[metric_key] = max(safe_int(merged_metrics.get(metric_key)), safe_int(metric_val))
        base["metrics"] = merged_metrics

        # Merge evidence.
        base["evidence"] = uniq_str(
            [*(base.get("evidence") or []), *(candidate.get("evidence") or [])]
        )

        by_slug[slug] = base

    merged = list(by_slug.values())
    merged.sort(
        key=lambda f: (
            -risk_rank(str(f.get("risk", ""))),
            -safe_int(f.get("metrics", {}).get("installsAllTime")),
            -safe_int(f.get("metrics", {}).get("downloads")),
            str(f.get("slug", "")),
        )
    )
    return merged


def build_patterns(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []

    # Cross-owner repeated reason code clusters.
    reason_groups: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"owners": set(), "members": [], "evidence": []}
    )
    for finding in findings:
        reason = str(finding.get("reasonCode", "unknown"))
        owner = str(finding.get("owner", {}).get("handle", "unknown"))
        reason_groups[reason]["owners"].add(owner)
        reason_groups[reason]["members"].append(str(finding.get("slug")))
        reason_groups[reason]["evidence"].extend(finding.get("evidence") or [])

    for reason, data in reason_groups.items():
        owners = data["owners"]
        members = uniq_str(data["members"])
        if reason not in {"unknown", "imported_from_big_pickel"} and len(owners) >= 2 and len(members) >= 2:
            patterns.append(
                {
                    "type": "cross_owner_clone_cluster",
                    "severity": "high" if "shell" in reason else "medium",
                    "description": (
                        f"Multiple owners share reasonCode `{reason}` across similar risky findings."
                    ),
                    "members": members,
                    "evidence": uniq_str(data["evidence"])[:10],
                }
            )

    # Same-owner repeat risk.
    owner_risk: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        if risk_rank(str(finding.get("risk"))) >= risk_rank("medium"):
            owner = str(finding.get("owner", {}).get("handle", "unknown"))
            owner_risk[owner].append(str(finding.get("slug")))

    repeaters = {owner: uniq_str(slugs) for owner, slugs in owner_risk.items() if len(set(slugs)) >= 2}
    if repeaters:
        for owner, slugs in sorted(repeaters.items()):
            patterns.append(
                {
                    "type": "same_owner_repeat_risk",
                    "severity": "high",
                    "description": (
                        f"Owner `{owner}` has multiple medium/high risk findings in current dataset."
                    ),
                    "members": slugs,
                }
            )
    else:
        patterns.append(
            {
                "type": "same_owner_repeat_risk",
                "severity": "unknown",
                "description": (
                    "No conclusive same-owner repeat-risk pattern in current dataset. Expand coverage for confidence."
                ),
                "members": [],
            }
        )

    return patterns


def load_scan_status(path: Path) -> dict[str, Any]:
    payload = load_json(path, {})
    if not isinstance(payload, dict):
        return {"healthy": False, "signals": []}
    signals = payload.get("signals")
    if not isinstance(signals, list):
        payload["signals"] = []
    return payload


def normalize_runtime_signals(
    scan_status: dict[str, Any], run_scan_error: str | None
) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    source = str(scan_status.get("source", "")).strip().lower()
    local_active = bool(scan_status.get("healthy")) and source in {"ryzen_gpu_primary", "ryzen_gpu_fallback"}

    raw_signals = scan_status.get("signals") if isinstance(scan_status, dict) else []
    if isinstance(raw_signals, list):
        for item in raw_signals:
            if not isinstance(item, dict):
                continue
            signal_id = str(item.get("id") or "scan_runtime_signal")
            level = str(item.get("level", "medium")).lower()
            if level not in SIGNAL_LEVEL_ORDER:
                level = "medium"
            # Keep runtime output action-focused: suppress informational noise.
            if signal_id in RUNTIME_INFO_SIGNAL_IDS:
                continue
            if level == "low":
                continue
            # If local model is already active/healthy, remote API failures are non-blocking.
            if local_active and signal_id.startswith("api_"):
                continue
            signals.append(
                {
                    "id": signal_id,
                    "level": level,
                    "message": str(item.get("message") or "Runtime signal reported by scan runner."),
                }
            )

    if run_scan_error:
        signals.append(
            {
                "id": "scan_subprocess_failed",
                "level": "high",
                "message": f"Scan subprocess failed: {run_scan_error}",
            }
        )

    return signals


def extract_runtime_engine(scan_status: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(scan_status, dict):
        return {"source": "unknown", "label": "Unknown engine", "model": "", "provider": "", "endpoint": ""}

    source = str(scan_status.get("source", "unknown") or "unknown")
    fallback = scan_status.get("fallback") if isinstance(scan_status.get("fallback"), dict) else {}
    provider = str(fallback.get("provider") or "")
    model = str(fallback.get("model") or scan_status.get("model") or "")
    endpoint = str(fallback.get("url") or scan_status.get("url") or "")

    if source == "ryzen_gpu_primary":
        label = "Ryzen GPU (Primary)"
    elif source == "ryzen_gpu_fallback":
        label = "Ryzen GPU (Fallback)"
    elif source == "big_pickel_api":
        label = "Big-Pickel API"
    else:
        label = source.replace("_", " ").title() if source else "Unknown engine"

    return {
        "source": source,
        "label": label,
        "provider": provider,
        "model": model,
        "endpoint": endpoint,
    }


def build_next_actions(
    findings: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    runtime_signals: list[dict[str, str]],
) -> list[str]:
    counts = Counter(f["risk"] for f in findings)
    actions: list[str] = []
    if any(s["id"] == "api_key_missing" for s in runtime_signals):
        actions.append("Set/fix Big-Pickel API key first; scan coverage is blocked until auth is healthy.")
    if any("rate_limit" in s["id"] for s in runtime_signals):
        actions.append("Reduce scan cadence or rotate API credentials; current rate limit is throttling signal quality.")
    if any(SIGNAL_LEVEL_ORDER.get(s["level"], 0) >= SIGNAL_LEVEL_ORDER["high"] for s in runtime_signals):
        actions.append("Resolve runtime/auth/rate-limit issues before trusting fresh scan outputs.")
    if counts.get("high", 0):
        actions.append("Post evidence-based comments on high-risk findings and queue safe replacements.")
    if counts.get("high_operational", 0):
        actions.append("Add mandatory simulation/confirmation guardrails to operational-risk skills.")
    if counts.get("medium", 0):
        actions.append("Patch medium-risk secret handling and enforce env-only token patterns.")
    if any(p.get("type") == "same_owner_repeat_risk" and p.get("members") for p in patterns):
        actions.append("Escalate repeat-risk owners into deeper review cycle.")
    actions.append("Re-run analytizer after each publish cycle and compare deltas.")
    return uniq_str(actions)


def docs_signal(finding: dict[str, Any]) -> str:
    evidence = finding.get("evidence") or []
    return "present" if any(str(p).endswith("/SKILL.md") for p in evidence) else "missing-in-sample"


def release_signal(versions: int) -> str:
    if versions >= 4:
        return "active-iteration"
    if versions >= 2:
        return "iterating"
    return "single-release"


def render_audit_md(audit: dict[str, Any]) -> str:
    findings = audit.get("findings", [])
    generated = audit.get("generatedAt", now_iso())
    counts = Counter(f.get("risk") for f in findings)
    signal_counts = Counter(f.get("signalLevel", "none") for f in findings)
    runtime_signals = (
        audit.get("runtime", {}).get("signals", [])
        if isinstance(audit.get("runtime"), dict)
        else []
    )
    lines = [
        "# ClawHub Trust Audit",
        "",
        f"Generated: {generated}",
        f"Scope: {audit.get('scope', {}).get('type', 'merged')} ({len(findings)} findings)",
        "",
        "## Findings Summary",
        "",
        f"- high: {counts.get('high', 0)}",
        f"- high_operational: {counts.get('high_operational', 0)}",
        f"- medium: {counts.get('medium', 0)}",
        f"- review_needed: {counts.get('review_needed', 0)}",
        f"- low: {counts.get('low', 0)}",
        f"- signal critical: {signal_counts.get('critical', 0)}",
        f"- signal high: {signal_counts.get('high', 0)}",
        f"- signal medium: {signal_counts.get('medium', 0)}",
        f"- signal low: {signal_counts.get('low', 0)}",
        "",
        "## Runtime Signals",
        "",
    ]

    if runtime_signals:
        for s in runtime_signals:
            if not isinstance(s, dict):
                continue
            lines.append(
                f"- `{s.get('level', 'medium')}` `{s.get('id', 'runtime_signal')}`: {s.get('message', '')}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Ranked Findings",
            "",
        ]
    )

    for idx, finding in enumerate(findings[:25], start=1):
        owner = finding.get("owner", {}).get("handle", "unknown")
        metrics = finding.get("metrics", {})
        versions = safe_int(metrics.get("versions"))
        signal_level = str(finding.get("signalLevel", "none"))
        owner_signal_level = str(finding.get("ownerSignalLevel", "none"))
        owner_flags = ", ".join(finding.get("ownerSignals") or []) or "none"
        lines.append(
            f"{idx}. `{finding.get('slug')}` | signal `{signal_level}` | risk `{finding.get('risk')}` | owner `{owner}` | "
            f"installs {safe_int(metrics.get('installsAllTime'))} | downloads {safe_int(metrics.get('downloads'))} | "
            f"docs {docs_signal(finding)} | releases {release_signal(versions)}"
        )
        lines.append(f"   - {finding.get('summary', '')}")
        lines.append(f"   - owner-signal `{owner_signal_level}` flags: {owner_flags}")

    lines.extend(
        [
            "",
            "## Developer Pattern Notes",
            "",
        ]
    )

    for pattern in audit.get("developerPatterns", []):
        lines.append(
            f"- `{pattern.get('type')}` `{pattern.get('severity')}`: {pattern.get('description')}"
        )

    lines.extend(["", "## Recommended Next Actions", ""])
    for idx, action in enumerate(audit.get("nextActions", []), start=1):
        lines.append(f"{idx}. {action}")

    return "\n".join(lines) + "\n"


def build_skills_todo(
    findings: list[dict[str, Any]],
    out_path: Path,
    runtime_signals: list[dict[str, str]],
    limit: int = 30,
) -> str:
    timestamp = now_ts()
    carry_rows = [
        row for row in parse_existing_status_rows(out_path) if row[1] in {"done", "ignore", "later"}
    ]

    queued: list[str] = []
    for signal in runtime_signals:
        level = str(signal.get("level", "low"))
        if SIGNAL_LEVEL_ORDER.get(level, 0) < SIGNAL_LEVEL_ORDER["high"]:
            continue
        queued.append(
            f"- [{timestamp}] `pending` Runtime `{level}`: {signal.get('message', 'scan/runtime issue')}"
        )

    for finding in findings:
        signal_level = str(finding.get("signalLevel", "low"))
        if SIGNAL_LEVEL_ORDER.get(signal_level, 0) < SIGNAL_LEVEL_ORDER["medium"]:
            continue
        risk = str(finding.get("risk"))
        slug = str(finding.get("slug"))
        owner = str(finding.get("owner", {}).get("handle", "unknown"))
        summary = str(finding.get("summary", "")).strip()
        owner_flags = ", ".join(finding.get("ownerSignals") or []) or "none"
        queued.append(
            f"- [{timestamp}] `pending` Review `{slug}` signal `{signal_level}` risk `{risk}` by `{owner}`. {summary}"
        )
        queued.append(
            f"- [{timestamp}] `pending` Owner-profile flags for `{slug}`: {owner_flags}."
        )
        reason_code = str(finding.get("reasonCode", "imported_from_big_pickel"))
        queued.append(
            f"- [{timestamp}] `pending` Draft/post comment template `{reason_code}` for `{slug}`."
        )
        if len(queued) >= limit:
            break

    if not queued:
        queued.append(f"- [{timestamp}] `pending` No medium/high signal findings in current dataset. Expand search scope.")

    lines = [
        "# SKILLS TODO",
        "",
        f"Last updated: {timestamp}",
        "Generated by: `clawhub-analytizer.py`",
        "",
        "## Pattern",
        "",
        "1. Run `python3 clawhub-analytizer/scripts/clawhub-analytizer.py --run-scan`.",
        "2. Fix runtime auth/rate-limit issues before trusting fresh scan coverage.",
        "3. Triage pending list top-down by signal level, then risk, then installs/downloads.",
        "4. Post evidence-based comments using template reasonCode.",
        "5. Publish safe replacement skills and mark completed rows.",
        "6. Re-run analytizer and compare deltas.",
        "",
        "## Pending Queue",
        "",
    ]
    lines.extend(queued)

    lines.extend(["", "## Carry Forward", ""])
    if carry_rows:
        for ts, status, text in carry_rows:
            lines.append(f"- [{ts}] `{status}` {text}")
    else:
        lines.append("- (none)")

    return "\n".join(lines) + "\n"


def parse_existing_status_rows(path: Path) -> list[tuple[str, str, str]]:
    if not path.exists():
        return []
    rows: list[tuple[str, str, str]] = []
    re_row = re.compile(r"^- \[(.*?)\] `([^`]+)` (.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re_row.match(line)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))
    return rows


def run_big_pickel(root: Path) -> tuple[bool, str | None]:
    script = root / "scripts" / "run-big-pickel-scan.py"
    if not script.exists():
        raise FileNotFoundError(f"Missing scan runner: {script}")
    proc = subprocess.run(
        ["python3", str(script)],
        check=False,
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return True, None
    error_text = (proc.stderr or proc.stdout or "").strip()
    return False, error_text[:1000]


def refresh_browser_data(root: Path) -> None:
    script = root / "scripts" / "build-browser-data.py"
    if script.exists():
        subprocess.run(["python3", str(script)], check=True, cwd=str(root))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ClawHub Analytizer pipeline.")
    parser.add_argument(
        "--run-scan",
        action="store_true",
        help="Run Big-Pickel API scan first via scripts/run-big-pickel-scan.py.",
    )
    parser.add_argument(
        "--response-file",
        default="data/big-pickel-last-response.json",
        help="Path to Big-Pickel JSON response file (default: data/big-pickel-last-response.json).",
    )
    parser.add_argument(
        "--no-public-index",
        action="store_true",
        help="Skip direct ClawHub public index ingestion.",
    )
    parser.add_argument(
        "--public-base-url",
        default=PUBLIC_INDEX_BASE_URL,
        help=f"ClawHub public API base URL (default: {PUBLIC_INDEX_BASE_URL}).",
    )
    parser.add_argument(
        "--public-limit",
        type=int,
        default=100,
        help="Page size for public index fetch (default: 100).",
    )
    parser.add_argument(
        "--public-max-pages",
        type=int,
        default=25,
        help="Maximum pages to ingest from public index (default: 25).",
    )
    parser.add_argument(
        "--public-sort",
        default="newest",
        help="Sort for public index fetch (default: newest).",
    )
    parser.add_argument(
        "--public-dir",
        default="desc",
        help="Direction for public index fetch (default: desc).",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    audit_path = root / "data" / "audit-findings.json"
    audit_md_path = root / "docs" / "AUDIT.md"
    skills_todo_path = root / "docs" / "SKILLS-TODO.md"
    response_path = root / args.response_file
    scan_status_path = root / "data" / "big-pickel-scan-status.json"
    owner_cache_path = root / "data" / "github-owner-cache.json"

    run_scan_error = None
    if args.run_scan:
        ok, run_scan_error = run_big_pickel(root)
        if not ok:
            print(f"WARN: scan subprocess failed, continuing with cached data. {run_scan_error}")

    existing = load_json(audit_path, {})
    existing_findings = existing.get("findings", []) if isinstance(existing, dict) else []

    incoming_items: list[dict[str, Any]] = []
    if response_path.exists():
        response_payload = load_json(response_path, {})
        if isinstance(response_payload, dict):
            if isinstance(response_payload.get("findings"), list):
                incoming_items = response_payload["findings"]
            else:
                incoming_items = pick_list_from_response(response_payload)
        elif isinstance(response_payload, list):
            incoming_items = [x for x in response_payload if isinstance(x, dict)]

    public_runtime_signals: list[dict[str, str]] = []
    public_meta_data: dict[str, Any] = {}
    public_source = None
    if not args.no_public_index:
        public_items, public_meta = fetch_public_skills_index(
            base_url=args.public_base_url,
            limit=max(1, int(args.public_limit)),
            max_pages=max(1, int(args.public_max_pages)),
            sort=str(args.public_sort or "newest"),
            direction=str(args.public_dir or "desc"),
        )
        public_meta_data = public_meta
        incoming_items.extend(public_skill_to_finding(item) for item in public_items if isinstance(item, dict))
        public_source = f"{args.public_base_url.rstrip('/')}/api/v1/skills"
        if public_meta.get("error"):
            public_runtime_signals.append(
                {
                    "id": "public_index_fetch_failed",
                    "level": "high",
                    "message": str(public_meta["error"]),
                }
            )
        elif public_meta.get("itemsFetched", 0) <= 0:
            public_runtime_signals.append(
                {
                    "id": "public_index_empty",
                    "level": "medium",
                    "message": "ClawHub public index returned no items; coverage may be incomplete.",
                }
            )

    merged_findings = merge_findings(existing_findings, incoming_items)
    merged_findings, _owner_cache = enrich_findings_with_owner_signals(merged_findings, owner_cache_path)
    merged_findings = apply_finding_signals(merged_findings)
    patterns = build_patterns(merged_findings)
    scan_status = load_scan_status(scan_status_path)
    runtime_engine = extract_runtime_engine(scan_status)
    runtime_signals = normalize_runtime_signals(scan_status, run_scan_error) + public_runtime_signals
    runtime_blocking = [
        s
        for s in runtime_signals
        if SIGNAL_LEVEL_ORDER.get(str(s.get("level", "low")).lower(), 0) >= SIGNAL_LEVEL_ORDER["high"]
    ]
    next_actions = build_next_actions(merged_findings, patterns, runtime_signals)

    source_files = [str(audit_path), str(response_path)]
    if public_source:
        source_files.append(public_source)

    audit_payload = {
        "generatedAt": now_iso(),
        "auditVersion": datetime.now().strftime("%Y.%m.analytizer2"),
        "scope": {
            "type": "merged_local_big_pickel_public_index",
            "skillsAudited": len(merged_findings),
            "sourceFiles": source_files,
        },
        "runtime": {
            "scanStatusPath": str(scan_status_path),
            "healthy": bool(scan_status.get("healthy")),
            "degraded": bool(scan_status.get("degraded")),
            "source": str(scan_status.get("source") or runtime_engine.get("source") or "unknown"),
            "engine": runtime_engine,
            "coverage": {
                "publicSkillsIngested": safe_int(public_meta_data.get("itemsFetched")),
                "publicPagesFetched": safe_int(public_meta_data.get("pagesFetched")),
            },
            "signals": runtime_signals,
            "blockingSignals": runtime_blocking,
        },
        "metrics": existing.get("metrics", {}),
        "autoComments": {
            **AUTO_COMMENTS_DEFAULT,
            **(existing.get("autoComments", {}) if isinstance(existing, dict) else {}),
        },
        "findings": merged_findings,
        "developerPatterns": patterns,
        "nextActions": next_actions,
    }

    save_json(audit_path, audit_payload)
    audit_md_path.write_text(render_audit_md(audit_payload), encoding="utf-8")
    skills_todo_path.write_text(
        build_skills_todo(merged_findings, skills_todo_path, runtime_signals),
        encoding="utf-8",
    )
    refresh_browser_data(root)

    print(f"Updated: {audit_path}")
    print(f"Updated: {audit_md_path}")
    print(f"Updated: {skills_todo_path}")
    print(f"Updated: {owner_cache_path}")
    print(f"Refreshed: {root / 'dashboard' / 'browser-data.js'}")


if __name__ == "__main__":
    main()
