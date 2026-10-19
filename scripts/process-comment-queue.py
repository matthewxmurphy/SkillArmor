#!/usr/bin/env python3
"""Generate and process queued ClawHub comment write-ups.

Copyright (c) 2026 Matthew X Murphy, https://MatthewxMurphy.com.
Product: https://builtnotbegged.com. Existing distribution rights retained.
"""

from __future__ import annotations

import argparse
import re
import json
import subprocess
import shlex
import os
import fcntl
from contextlib import contextmanager
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
    except json.JSONDecodeError as error:
        raise ValueError("Malformed persisted JSON requires owner repair") from error


def save_json(path: Path, payload: Any) -> None:
    if path.is_symlink():
        raise ValueError("Queue symlinks are not supported")
    descriptor, temporary = tempfile.mkstemp(prefix=".comment-queue-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


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


def validated_queue_items(payload: Any) -> list[dict[str, Any]]:
    """Require one durable record per item before generation or delivery.

    Duplicate identities can carry conflicting attempts/receipts, so persisted
    duplicates require owner reconciliation rather than merging or posting both.
    Validation finishes before callers mutate state or invoke an adapter.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("Malformed persisted queue requires owner repair")
    seen: set[str] = set()
    for row in payload["items"]:
        item_id = row.get("id") if isinstance(row, dict) else None
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("Queue items require nonempty string identities")
        if item_id in seen:
            raise ValueError("Duplicate queue identities require owner reconciliation")
        seen.add(item_id)
    return payload["items"]


def generate_queue(
    audit_payload: dict[str, Any],
    queue_path: Path,
    limit: int,
    min_signal: str,
) -> dict[str, Any]:
    existing = load_json(queue_path, {"items": []})
    old_items = validated_queue_items(existing)
    old_map = {
        str(item.get("id")): item for item in old_items if isinstance(item, dict) and item.get("id")
    }

    templates = audit_payload.get("autoComments", {}) if isinstance(audit_payload.get("autoComments"), dict) else {}
    findings = audit_payload.get("findings", []) if isinstance(audit_payload.get("findings"), list) else []

    # Source feeds may repeat a finding. Apply the cap to unique identities so
    # one logical item has one claim and cannot consume multiple send attempts.
    selected = []
    seen_findings: set[str] = set()
    for finding in findings:
        if len(selected) >= limit:
            break
        if not isinstance(finding, dict) or not should_include(finding, min_signal):
            continue
        item_id = queue_item_id(finding)
        if item_id in seen_findings:
            continue
        seen_findings.add(item_id)
        selected.append(finding)

    now = now_utc()
    items: list[dict[str, Any]] = []
    for finding in selected:
        item_id = queue_item_id(finding)
        prior = old_map.get(item_id, {})
        if prior and (prior.get("status") != "queued" or int(prior.get("attempts", 0) or 0) > 0):
            items.append(prior)  # Attempts freeze exact text and reconciliation evidence.
            continue
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

    selected_ids = {row["id"] for row in items}
    items.extend(row for row in old_items if row["id"] not in selected_ids and (row.get("status") != "queued" or int(row.get("attempts", 0) or 0) > 0))
    if len(items) > 10000:
        raise ValueError("Queue history capacity requires owner archival; receipts cannot be evicted")
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


def adapter_arguments(template: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Admit a trusted execution prefix and a closed data-only adapter protocol.

    Untrusted fields cannot select executables, scripts, switches or positional
    arguments. Values become --key=value tokens so leading dashes stay data.
    Operators own the executable/script and must keep those files trusted.
    """
    command = shlex.split(template)
    if not command or not Path(command[0]).is_absolute() or any(c in command[0] for c in "{}"):
        raise ValueError("absolute_fixed_executable_required")
    name = Path(command[0]).name.lower()
    if name in {"sh", "bash", "dash", "zsh", "fish", "cmd", "powershell", "pwsh", "env", "xargs", "sudo"}:
        raise ValueError("shell_or_launcher_adapter_denied")
    prefix = command[:1]
    remaining = command[1:]
    if re.fullmatch(r"python(?:[0-9]+(?:\.[0-9]+)*)?", name) or name in {"node", "nodejs"}:
        # No interpreter flags, module execution or dynamic program selection.
        if not remaining or not Path(remaining[0]).is_absolute() or any(c in remaining[0] for c in "{}"):
            raise ValueError("fixed_absolute_adapter_script_required")
        suffixes = {".py"} if name.startswith("python") else {".js", ".mjs", ".cjs"}
        if Path(remaining[0]).suffix not in suffixes:
            raise ValueError("adapter_script_type_required")
        prefix.append(remaining.pop(0))
    allowed = {"--slug": "{slug}", "--owner": "{owner}",
               "--comment-file": "{comment_file}", "--body-file": "{comment_file}"}
    pairs = []
    seen = set()
    while remaining:
        token = remaining.pop(0)
        if "=" in token:
            key, value = token.split("=", 1)
        else:
            key = token
            if not remaining:
                raise ValueError("adapter_data_value_required")
            value = remaining.pop(0)
        if key not in allowed or value != allowed[key] or key in seen:
            raise ValueError("unsupported_adapter_argument")
        seen.add(key)
        pairs.append((key, value[1:-1]))
    if not seen.intersection({"--comment-file", "--body-file"}):
        raise ValueError("private_comment_file_required")
    return prefix, pairs


def run_post_command(command_template: str, item: dict[str, Any]) -> tuple[bool, str]:
    """Run only the fixed adapter prefix plus data; require provider receipt.

    Timeout/nonzero/malformed output is uncertain, never automatic retry authority.
    Arbitrary comment text is passed only through a private temporary file.
    """
    body = str((item.get("comment") or {}).get("combined", "")).strip()
    if not body:
        return False, "empty_comment_body"
    try:
        prefix, arguments = adapter_arguments(command_template)
    except ValueError:
        return False, "invalid_adapter_arguments"
    comment_file = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tf:
            tf.write(body + "\n")
            comment_file = tf.name
        fields = dict(slug=str(item.get("slug", "")), owner=str(item.get("owner", "")),
                      comment_file=comment_file)
        argv = prefix + [key + "=" + fields[field] for key, field in arguments]
        result = subprocess.run(argv, shell=False, text=True, capture_output=True, timeout=120)
        if result.returncode != 0:
            return False, "adapter_outcome_uncertain"
        receipt = json.loads(result.stdout)
        if not isinstance(receipt, dict) or receipt.get("confirmed") is not True or not isinstance(receipt.get("receipt_id"), str) or not 1 <= len(receipt["receipt_id"]) <= 200:
            return False, "adapter_confirmation_missing"
        return True, json.dumps({"confirmed": True, "receipt_id": receipt["receipt_id"]})
    except (ValueError, KeyError, OSError, subprocess.SubprocessError):
        return False, "adapter_outcome_uncertain"
    finally:
        if comment_file is not None:
            if os.path.exists(comment_file):
                os.unlink(comment_file)


@contextmanager
def queue_lock(path: Path):
    """One local worker owns generation plus delivery; lock files contain no data."""
    descriptor = os.open(str(path) + ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(descriptor)


def _process_queue(queue_payload: dict[str, Any], queue_path: Path, max_posts: int, post_command: str) -> dict[str, Any]:
    items = validated_queue_items(queue_payload)

    now = now_utc()
    posted = 0
    attempted = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        if attempted >= max_posts:
            break
        if item.get("status") == "posting":
            item["status"] = "uncertain"
            item["lastError"] = "interrupted_adapter_requires_owner_reconciliation"
        if str(item.get("status", "queued")) != "queued":
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

        attempted += 1
        item["status"] = "posting"
        item["attempts"] = int(item.get("attempts", 0) or 0) + 1
        save_json(queue_path, queue_payload)
        ok, info = run_post_command(post_command, item)
        item["updatedAt"] = iso(now)
        if ok:
            posted += 1
            item["status"] = "posted"
            item["postedAt"] = iso(now)
            item["lastError"] = None
            item["postReceipt"] = info
        else:
            item["status"] = "uncertain"
            item["lastError"] = info
            item["nextAttemptAt"] = iso(now + timedelta(minutes=30))

    queue_payload["processedAt"] = iso(now)
    queue_payload["postStats"] = {"postedThisRun": posted, "attemptedThisRun": attempted, "maxPostsPerRun": max_posts}
    save_json(queue_path, queue_payload)
    return queue_payload


def process_queue(queue_payload, queue_path, max_posts, post_command):
    with queue_lock(queue_path):
        durable = load_json(queue_path, queue_payload)
        return _process_queue(durable, queue_path, max_posts, post_command)


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

    with queue_lock(queue_path):
        audit_payload = load_json(audit_path, {})
        if not isinstance(audit_payload, dict):
            raise SystemExit(f"Invalid audit payload: {audit_path}")

        queue_payload = generate_queue(audit_payload, queue_path, max(1, int(args.limit)), args.min_signal)
        if args.process:
            queue_payload = _process_queue(
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
