#!/usr/bin/env python3
"""Generate and process queued ClawHub comment write-ups."""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SIGNAL_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    if dt is None:
        dt = now_utc()
    return dt.isoformat(timespec="seconds")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def docs_present(finding: dict[str, Any]) -> bool:
    evidence = finding.get("evidence") or []
    return any(str(path).endswith("/SKILL.md") for path in evidence)


def owner_activity_sentence(finding: dict[str, Any]) -> str:
    owner = str(finding.get("owner", {}).get("handle", "unknown"))
    flags = {str(x) for x in (finding.get("ownerSignals") or [])}
    profile = finding.get("ownerProfile") if isinstance(finding.get("ownerProfile"), dict) else {}

    if owner == "unknown":
        return "Author identity is unknown in this source record."
    if "github_profile_not_found" in flags:
        return f"Author handle `{owner}` does not resolve to a public GitHub profile."
    if "github_profile_unreachable" in flags:
        return f"GitHub profile lookup for `{owner}` is currently unreachable."
    if "no_public_repos" in flags and "no_followers" in flags:
        return f"Author `{owner}` appears to have no public repos and little/no public GitHub activity."

    repos = profile.get("publicRepos")
    followers = profile.get("followers")
    if isinstance(repos, int) and isinstance(followers, int):
        return f"Author `{owner}` public profile currently shows {repos} repos and {followers} followers."
    return f"Author `{owner}` has a public GitHub profile with limited metadata."


def legitimacy_checks(finding: dict[str, Any]) -> list[str]:
    owner = str(finding.get("owner", {}).get("handle", "unknown"))
    flags = {str(x) for x in (finding.get("ownerSignals") or [])}
    profile = finding.get("ownerProfile") if isinstance(finding.get("ownerProfile"), dict) else {}
    checks: list[str] = []

    if owner == "unknown":
        checks.append("ClawHub source did not provide a stable owner handle.")
    else:
        checks.append(f"Owner handle reviewed: `{owner}`.")
    checks.append("No public ClawHub author bio field was present in this record.")

    if "github_profile_not_found" in flags:
        checks.append("GitHub handle did not resolve to a public profile.")
    elif "github_profile_unreachable" in flags:
        checks.append("GitHub profile check was unreachable during this run.")
    elif "github_profile_rate_limited" in flags:
        checks.append("GitHub profile lookup hit rate-limit/permission constraints.")
    else:
        checks.append("GitHub profile lookup completed.")

    if "no_public_repos" in flags:
        checks.append("No public repositories observed on GitHub profile.")
    if "no_followers" in flags:
        checks.append("No public follower activity observed.")
    if "sparse_public_profile" in flags or "partial_public_profile" in flags:
        checks.append("Profile metadata is sparse (bio/name/location/blog fields mostly empty).")
    if isinstance(profile, dict):
        if profile.get("bioPresent") is False:
            checks.append("GitHub bio appears missing.")
        if profile.get("namePresent") is False:
            checks.append("GitHub display name appears missing.")

    if not docs_present(finding):
        checks.append("SKILL.md evidence missing in sampled artifacts.")
    versions = int((finding.get("metrics") or {}).get("versions") or 0)
    if versions <= 1:
        checks.append("Only one visible release/version in current metadata.")
    else:
        checks.append(f"{versions} versions observed in current metadata.")

    return checks


def behavior_sentence(finding: dict[str, Any]) -> str:
    summary = str(finding.get("summary", "")).strip()
    reason = str(finding.get("reasonCode", "unknown_reason")).strip()
    if summary:
        return f"Observed behavior: {summary}"
    return f"Observed behavior aligns with reason code `{reason}`."


def build_comment_texts(finding: dict[str, Any], template: str) -> dict[str, str]:
    slug = str(finding.get("slug", "unknown-skill"))
    owner = str(finding.get("owner", {}).get("handle", "unknown"))
    risk = str(finding.get("risk", "review_needed"))
    signal = str(finding.get("signalLevel", "none"))
    versions = int((finding.get("metrics") or {}).get("versions") or 0)
    markdown_state = "present" if docs_present(finding) else "missing"
    owner_line = owner_activity_sentence(finding)
    legit_checks = legitimacy_checks(finding)
    legit_block = "\n".join(f"- {line}" for line in legit_checks)
    behavior = behavior_sentence(finding)
    template_line = template.strip() if template.strip() else "No default template matched; manual review comment generated."

    pov_risk = (
        f"[POV 1: Safety / Runtime]\n"
        f"Skill `{slug}` by `{owner}` is currently `{risk}` risk with `{signal}` signal.\n"
        f"{behavior}\n"
        f"Template guidance: {template_line}"
    )

    pov_quality = (
        f"[POV 2: Maintainer / Quality]\n"
        f"{owner_line}\n"
        f"Legitimacy checks used:\n{legit_block}\n"
        f"Version history observed: {versions} release(s).\n"
        f"SKILL.md evidence: {markdown_state}.\n"
        f"Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope."
    )

    combined = f"{pov_risk}\n\n{pov_quality}"
    return {"pov_risk": pov_risk, "pov_quality": pov_quality, "combined": combined}


def queue_item_id(finding: dict[str, Any]) -> str:
    slug = str(finding.get("slug", "unknown"))
    reason = str(finding.get("reasonCode", "unknown"))
    signal = str(finding.get("signalLevel", "none"))
    return f"{slug}::{reason}::{signal}"


def should_include(finding: dict[str, Any], min_signal: str) -> bool:
    signal = str(finding.get("signalLevel", "none")).lower()
    return SIGNAL_RANK.get(signal, 0) >= SIGNAL_RANK.get(min_signal, 2)


def generate_queue(
    audit_payload: dict[str, Any],
    queue_path: Path,
    limit: int,
    min_signal: str,
) -> dict[str, Any]:
    existing = load_json(queue_path, {})
    old_items = existing.get("items", []) if isinstance(existing.get("items"), list) else []
    old_map = {
        str(item.get("id")): item for item in old_items if isinstance(item, dict) and item.get("id")
    }

    templates = audit_payload.get("autoComments", {}) if isinstance(audit_payload.get("autoComments"), dict) else {}
    findings = audit_payload.get("findings", []) if isinstance(audit_payload.get("findings"), list) else []

    selected = [f for f in findings if isinstance(f, dict) and should_include(f, min_signal)][:limit]

    now = now_utc()
    items: list[dict[str, Any]] = []
    for finding in selected:
        item_id = queue_item_id(finding)
        prior = old_map.get(item_id, {})
        reason = str(finding.get("reasonCode", ""))
        template = str(templates.get(reason, ""))
        texts = build_comment_texts(finding, template)
        next_attempt = prior.get("nextAttemptAt") or iso(now)
        status = str(prior.get("status", "queued"))
        attempts = int(prior.get("attempts", 0) or 0)
        items.append(
            {
                "id": item_id,
                "slug": str(finding.get("slug", "")),
                "owner": str(finding.get("owner", {}).get("handle", "unknown")),
                "risk": str(finding.get("risk", "review_needed")),
                "signalLevel": str(finding.get("signalLevel", "none")),
                "reasonCode": reason,
                "versions": int((finding.get("metrics") or {}).get("versions") or 0),
                "markdownPresent": docs_present(finding),
                "ownerSignals": finding.get("ownerSignals", []),
                "signalReasons": finding.get("signalReasons", []),
                "summary": str(finding.get("summary", "")),
                "evidence": finding.get("evidence", []),
                "comment": texts,
                "status": status,
                "attempts": attempts,
                "createdAt": prior.get("createdAt", iso(now)),
                "updatedAt": iso(now),
                "nextAttemptAt": next_attempt,
                "lastError": prior.get("lastError"),
                "postedAt": prior.get("postedAt"),
            }
        )

    payload = {
        "generatedAt": iso(now),
        "sourceAuditGeneratedAt": audit_payload.get("generatedAt"),
        "queuePolicy": {
            "minSignal": min_signal,
            "limit": limit,
            "slowPosting": "max-posts-per-run",
        },
        "items": items,
    }
    save_json(queue_path, payload)
    return payload


def render_markdown(queue_payload: dict[str, Any]) -> str:
    lines = [
        "# ClawHub Comment Queue",
        "",
        f"Generated: {queue_payload.get('generatedAt', iso())}",
        "",
        "Each item includes two POV drafts:",
        "1. Safety/Runtime POV",
        "2. Maintainer/Quality POV",
        "",
    ]
    items = queue_payload.get("items", [])
    if not isinstance(items, list) or not items:
        lines.append("- No queued items.")
        return "\n".join(lines) + "\n"

    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        comment = item.get("comment", {}) if isinstance(item.get("comment"), dict) else {}
        lines.extend(
            [
                f"## {idx}. `{item.get('slug', 'unknown')}`",
                "",
                f"- status: `{item.get('status', 'queued')}`",
                f"- risk/signal: `{item.get('risk', 'review_needed')}` / `{item.get('signalLevel', 'none')}`",
                f"- owner: `{item.get('owner', 'unknown')}`",
                f"- versions: `{item.get('versions', 0)}`",
                f"- markdown present: `{item.get('markdownPresent', False)}`",
                "",
                "### POV 1",
                "",
                str(comment.get("pov_risk", "")),
                "",
                "### POV 2",
                "",
                str(comment.get("pov_quality", "")),
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def run_post_command(command_template: str, item: dict[str, Any]) -> tuple[bool, str]:
    comment = item.get("comment", {}) if isinstance(item.get("comment"), dict) else {}
    body = str(comment.get("combined", "")).strip()
    if not body:
        return False, "empty_comment_body"

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tf:
        tf.write(body + "\n")
        comment_file = tf.name

    expanded = command_template.format(
        slug=item.get("slug", ""),
        owner=item.get("owner", ""),
        comment_file=comment_file,
        comment_text=body.replace("\n", " "),
        comment_text_b64=base64.b64encode(body.encode("utf-8")).decode("ascii"),
    )
    result = subprocess.run(expanded, shell=True, text=True, capture_output=True, timeout=120)
    if result.returncode == 0:
        return True, (result.stdout or "posted").strip()
    err = (result.stderr or result.stdout or "").strip()
    return False, err or f"post_command_failed_exit_{result.returncode}"


def process_queue(queue_payload: dict[str, Any], queue_path: Path, max_posts: int, post_command: str) -> dict[str, Any]:
    items = queue_payload.get("items", [])
    if not isinstance(items, list):
        return queue_payload

    now = now_utc()
    posted = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        if posted >= max_posts:
            break
        if str(item.get("status", "queued")) == "posted":
            continue
        next_attempt = item.get("nextAttemptAt")
        if isinstance(next_attempt, str):
            try:
                due = datetime.fromisoformat(next_attempt.replace("Z", "+00:00"))
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                if due > now:
                    continue
            except ValueError:
                pass

        if not post_command.strip():
            # Queue stays ready if posting command is not configured yet.
            item["status"] = "queued"
            item["lastError"] = "post_command_not_configured"
            item["updatedAt"] = iso(now)
            continue

        ok, info = run_post_command(post_command, item)
        item["attempts"] = int(item.get("attempts", 0) or 0) + 1
        item["updatedAt"] = iso(now)
        if ok:
            posted += 1
            item["status"] = "posted"
            item["postedAt"] = iso(now)
            item["lastError"] = None
            item["postReceipt"] = info
        else:
            item["status"] = "queued"
            item["lastError"] = info
            item["nextAttemptAt"] = iso(now + timedelta(minutes=30))

    queue_payload["processedAt"] = iso(now)
    queue_payload["postStats"] = {"postedThisRun": posted, "maxPostsPerRun": max_posts}
    save_json(queue_path, queue_payload)
    return queue_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and process ClawHub comment queue.")
    parser.add_argument("--audit", default="data/audit-findings.json", help="Audit findings JSON path.")
    parser.add_argument("--queue", default="data/comment-post-queue.json", help="Queue JSON path.")
    parser.add_argument("--comments-md", default="docs/COMMENTS.md", help="Comment markdown output path.")
    parser.add_argument("--limit", type=int, default=80, help="Max findings to keep in queue.")
    parser.add_argument("--min-signal", default="medium", choices=["low", "medium", "high", "critical"], help="Minimum signal level to queue.")
    parser.add_argument("--max-posts", type=int, default=1, help="Max posts to attempt per run.")
    parser.add_argument("--post-command", default="", help="Optional posting command template.")
    parser.add_argument("--process", action="store_true", help="Attempt to process queue using --post-command.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    audit_path = root / args.audit
    queue_path = root / args.queue
    comments_md_path = root / args.comments_md

    audit_payload = load_json(audit_path, {})
    if not isinstance(audit_payload, dict):
        raise SystemExit(f"Invalid audit payload: {audit_path}")

    queue_payload = generate_queue(audit_payload, queue_path, max(1, int(args.limit)), args.min_signal)
    if args.process:
        queue_payload = process_queue(
            queue_payload,
            queue_path,
            max(1, int(args.max_posts)),
            str(args.post_command or "").strip(),
        )

    comments_md_path.write_text(render_markdown(queue_payload), encoding="utf-8")
    print(f"Updated queue: {queue_path}")
    print(f"Updated comments: {comments_md_path}")
    if args.process:
        stats = queue_payload.get("postStats", {})
        print(f"Queue processing: posted {stats.get('postedThisRun', 0)} item(s)")


if __name__ == "__main__":
    main()
