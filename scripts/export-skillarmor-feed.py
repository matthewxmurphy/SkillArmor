#!/usr/bin/env python3
"""Export public SkillArmor feed from local audit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SIGNAL_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
RISK_RANK = {"low": 1, "review_needed": 2, "medium": 3, "high_operational": 4, "high": 5}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "you",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "via",
    "use",
    "using",
    "skill",
    "skills",
    "agent",
    "openclaw",
    "clawhub",
    "data",
    "code",
    "tool",
    "tools",
}

CODE_EXTS = {".js", ".ts", ".py", ".sh", ".go", ".rs", ".php", ".rb", ".java", ".c", ".cpp"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def docs_present(finding: dict[str, Any]) -> bool:
    evidence = finding.get("evidence") or []
    return any(str(path).endswith("/SKILL.md") for path in evidence)


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]{3,}", str(text).lower())
    return [t for t in tokens if t not in STOPWORDS]


def summary_token_set(finding: dict[str, Any]) -> set[str]:
    text = " ".join(
        [
            str(finding.get("slug", "")),
            str(finding.get("displayName", "")),
            str(finding.get("reasonCode", "")),
            str(finding.get("summary", "")),
        ]
    )
    return set(tokenize(text))


def signature_key(finding: dict[str, Any]) -> str:
    tokens = sorted(summary_token_set(finding))
    core = "|".join(tokens[:8])
    reason = str(finding.get("reasonCode", "unknown"))
    risk = str(finding.get("risk", "review_needed"))
    return f"{reason}|{risk}|{core}"


def file_signature(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()[:16]


def extract_code_signatures(finding: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in finding.get("evidence") or []:
        p = str(raw)
        if p.startswith("public_api:"):
            continue
        path = Path(p)
        if not path.exists() or not path.is_file():
            continue
        if path.suffix.lower() not in CODE_EXTS:
            continue
        sig = file_signature(path)
        if sig:
            result[path.name] = sig
    return result


def compute_cluster_code_diff(members: list[dict[str, Any]]) -> dict[str, Any]:
    per_skill: dict[str, dict[str, str]] = {}
    for m in members:
        slug = str(m.get("slug", "unknown"))
        per_skill[slug] = extract_code_signatures(m)

    non_empty = {k: v for k, v in per_skill.items() if v}
    if len(non_empty) < 2:
        return {
            "mode": "unknown_code_unavailable",
            "sharedFiles": [],
            "differentFiles": [],
            "note": "Insufficient local code evidence to compare signatures.",
        }

    all_file_sets = [set(v.keys()) for v in non_empty.values()]
    shared_files = sorted(set.intersection(*all_file_sets)) if all_file_sets else []
    different_files = sorted(set.union(*all_file_sets) - set(shared_files)) if all_file_sets else []

    signatures = [tuple(sorted(v.items())) for v in non_empty.values()]
    same = len(set(signatures)) == 1
    return {
        "mode": "likely_same_code" if same else "different_code_signatures",
        "sharedFiles": shared_files,
        "differentFiles": different_files,
        "note": (
            "Compared local evidence file hashes."
            if non_empty
            else "No local evidence files to compare."
        ),
    }


def legitimacy_notes(finding: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    owner = str(finding.get("owner", {}).get("handle", "unknown"))
    owner_flags = {str(x) for x in (finding.get("ownerSignals") or [])}
    profile = finding.get("ownerProfile") if isinstance(finding.get("ownerProfile"), dict) else {}

    if owner == "unknown":
        notes.append("Owner handle missing in public source.")
    else:
        notes.append(f"Owner handle: {owner}.")
    notes.append("No public ClawHub author bio field in this source record.")

    if "github_profile_not_found" in owner_flags:
        notes.append("GitHub profile not found.")
    elif "github_profile_unreachable" in owner_flags:
        notes.append("GitHub profile unreachable during check.")
    elif "github_profile_rate_limited" in owner_flags:
        notes.append("GitHub profile lookup rate-limited.")
    else:
        notes.append("GitHub profile lookup completed.")

    if "no_public_repos" in owner_flags:
        notes.append("No public repos visible.")
    if "no_followers" in owner_flags:
        notes.append("No public followers visible.")
    if "sparse_public_profile" in owner_flags or "partial_public_profile" in owner_flags:
        notes.append("Sparse public profile metadata (bio/name/location/blog).")
    if isinstance(profile, dict):
        if profile.get("bioPresent") is False:
            notes.append("GitHub bio missing.")
        if profile.get("namePresent") is False:
            notes.append("GitHub display name missing.")

    versions = int((finding.get("metrics") or {}).get("versions") or 0)
    notes.append(f"Versions observed: {versions}.")
    notes.append(f"SKILL.md evidence {'present' if docs_present(finding) else 'missing'}.")
    return notes


def to_public_skill(finding: dict[str, Any]) -> dict[str, Any]:
    metrics = finding.get("metrics") if isinstance(finding.get("metrics"), dict) else {}
    owner = finding.get("owner") if isinstance(finding.get("owner"), dict) else {}
    evidence = [str(x) for x in (finding.get("evidence") or [])]
    evidence_public = [x for x in evidence if x.startswith("public_api:")]

    return {
        "slug": str(finding.get("slug", "")),
        "displayName": str(finding.get("displayName", "")),
        "owner": str(owner.get("handle", "unknown")),
        "risk": str(finding.get("risk", "review_needed")),
        "signalLevel": str(finding.get("signalLevel", "none")),
        "reasonCode": str(finding.get("reasonCode", "")),
        "summary": str(finding.get("summary", "")),
        "suggestedAction": str(finding.get("suggestedAction", "")),
        "metrics": {
            "stars": int(metrics.get("stars", 0) or 0),
            "installsAllTime": int(metrics.get("installsAllTime", 0) or 0),
            "downloads": int(metrics.get("downloads", 0) or 0),
            "versions": int(metrics.get("versions", 0) or 0),
        },
        "docsPresent": docs_present(finding),
        "ownerSignals": [str(x) for x in (finding.get("ownerSignals") or [])],
        "signalReasons": [str(x) for x in (finding.get("signalReasons") or [])],
        "legitimacyNotes": legitimacy_notes(finding),
        "evidence": evidence_public,
    }


def build_duplicate_clusters(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        buckets[signature_key(finding)].append(finding)

    clusters: list[dict[str, Any]] = []
    for key, members in buckets.items():
        if len(members) < 2:
            continue
        reason = str(members[0].get("reasonCode", "unknown"))
        risk = str(members[0].get("risk", "review_needed"))
        code_diff = compute_cluster_code_diff(members)
        cluster_id = hashlib.md5(key.encode("utf-8")).hexdigest()[:10]

        member_rows = []
        for m in members:
            metrics = m.get("metrics") if isinstance(m.get("metrics"), dict) else {}
            member_rows.append(
                {
                    "slug": str(m.get("slug", "")),
                    "owner": str((m.get("owner") or {}).get("handle", "unknown")),
                    "signalLevel": str(m.get("signalLevel", "none")),
                    "versions": int(metrics.get("versions", 0) or 0),
                    "docsPresent": docs_present(m),
                }
            )

        clusters.append(
            {
                "clusterId": cluster_id,
                "reasonCode": reason,
                "risk": risk,
                "memberCount": len(members),
                "authors": sorted({str((m.get("owner") or {}).get("handle", "unknown")) for m in members}),
                "codeComparison": code_diff,
                "members": sorted(
                    member_rows,
                    key=lambda row: (
                        -SIGNAL_RANK.get(row["signalLevel"], 0),
                        row["slug"],
                    ),
                ),
            }
        )

    clusters.sort(
        key=lambda c: (
            -int(c.get("memberCount", 0)),
            -RISK_RANK.get(str(c.get("risk", "review_needed")), 0),
            c.get("clusterId", ""),
        )
    )
    return clusters


def top_findings(findings: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    ordered = sorted(
        findings,
        key=lambda f: (
            -SIGNAL_RANK.get(str(f.get("signalLevel", "none")), 0),
            -RISK_RANK.get(str(f.get("risk", "review_needed")), 0),
            -int(((f.get("metrics") or {}).get("downloads", 0) or 0)),
            str(f.get("slug", "")),
        ),
    )
    return ordered[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SkillArmor public feed JSON.")
    parser.add_argument("--audit", default="data/audit-findings.json")
    parser.add_argument("--comments-queue", default="data/comment-post-queue.json")
    parser.add_argument("--out", default="../skillarmor-site/data/skillarmor-feed.json")
    parser.add_argument("--top-limit", type=int, default=300)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    audit_path = root / args.audit
    queue_path = root / args.comments_queue
    out_path = (root / args.out).resolve()

    audit = load_json(audit_path, {})
    findings = audit.get("findings", []) if isinstance(audit.get("findings"), list) else []
    queue = load_json(queue_path, {})
    queued_items = queue.get("items", []) if isinstance(queue.get("items"), list) else []
    queued_open = [x for x in queued_items if isinstance(x, dict) and str(x.get("status", "queued")) != "posted"]

    top = top_findings([f for f in findings if isinstance(f, dict)], max(1, args.top_limit))
    clusters = build_duplicate_clusters([f for f in findings if isinstance(f, dict)])
    public_skills = [to_public_skill(f) for f in top]

    authors = {row["owner"] for row in public_skills}
    flagged_authors = {
        row["owner"]
        for row in public_skills
        if row["signalLevel"] in {"high", "critical"}
        or any(flag in {"no_public_repos", "github_profile_not_found", "sparse_public_profile"} for flag in row["ownerSignals"])
    }

    runtime = audit.get("runtime", {}) if isinstance(audit.get("runtime"), dict) else {}
    payload = {
        "generatedAt": now_iso(),
        "sourceAuditGeneratedAt": audit.get("generatedAt"),
        "brand": {
            "name": "SkillArmor",
            "tagline": "Community skill trust board",
            "siteUrl": "https://skillarmor.org",
        },
        "stats": {
            "totalFindings": len(findings),
            "publishedSkills": len(public_skills),
            "duplicateClusters": len(clusters),
            "queuedComments": len(queued_open),
            "authorsTracked": len(authors),
            "authorsFlagged": len(flagged_authors),
            "criticalFindings": sum(1 for f in findings if str(f.get("signalLevel", "none")) == "critical"),
            "highFindings": sum(1 for f in findings if str(f.get("signalLevel", "none")) == "high"),
        },
        "runtime": {
            "healthy": bool(runtime.get("healthy")),
            "source": runtime.get("source"),
            "engine": runtime.get("engine", {}),
            "signals": runtime.get("signals", []),
        },
        "duplicateClusters": clusters,
        "skills": public_skills,
        "queueSummary": {
            "openItems": len(queued_open),
            "totalItems": len(queued_items),
            "lastProcessedAt": queue.get("processedAt"),
            "postedThisRun": ((queue.get("postStats") or {}).get("postedThisRun") if isinstance(queue.get("postStats"), dict) else 0),
        },
    }

    save_json(out_path, payload)
    print(f"Wrote SkillArmor feed: {out_path}")


if __name__ == "__main__":
    main()
