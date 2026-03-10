#!/usr/bin/env python3
"""Generate and optionally deploy nginx vhost configs for multiple projects."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLAN_PATH = PROJECT_ROOT / "data" / "vhost-projects.json"
DEFAULT_DEPLOY_CFG_PATH = PROJECT_ROOT / "data" / "vhost-deploy-config.json"
DEFAULT_OUT_DIR = PROJECT_ROOT / "output" / "vhosts"
DEFAULT_HANDOFF_PATH = PROJECT_ROOT / "data" / "codex-vhost-handoff.json"
DEFAULT_BUILD_VER = "0.5.0"
DEFAULT_PROJECTS_KEY_ROOT = "/System/Volumes/Data/Projects"
DEFAULT_ACCOUNT_CREATE_SCRIPT = PROJECT_ROOT.parent / "OpsCenter" / "scripts" / "create-sftp-project-account.sh"
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)(?:[A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_codex_handoff(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    out_dir: Path,
    deploy_cfg: dict[str, Any] | None,
) -> dict[str, Any]:
    projects: list[dict[str, Any]] = []
    for item in plan.get("projects", []):
        if not item.get("enabled", True):
            continue
        projects.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "domain": item.get("domain"),
                "aliases": item.get("aliases", []),
                "type": item.get("type"),
                "root": item.get("root"),
                "upstream": item.get("upstream"),
                "tls": item.get("tls"),
                "forceHttps": item.get("forceHttps"),
            }
        )

    deploy = {
        "enabled": False,
        "host": "",
        "port": 22,
        "user": "",
        "sshKeyPath": "",
        "projectsKeyRoot": DEFAULT_PROJECTS_KEY_ROOT,
        "requireProjectsKeyRoot": True,
    }
    if deploy_cfg:
        deploy = {
            "enabled": as_bool(deploy_cfg.get("enabled", False), default=False),
            "host": str(deploy_cfg.get("host", "")).strip(),
            "port": int(deploy_cfg.get("port", 22) or 22),
            "user": str(deploy_cfg.get("user", "")).strip(),
            "sshKeyPath": str(deploy_cfg.get("sshKeyPath", "")).strip(),
            "projectsKeyRoot": str(
                deploy_cfg.get("projectsKeyRoot", DEFAULT_PROJECTS_KEY_ROOT)
            ).strip()
            or DEFAULT_PROJECTS_KEY_ROOT,
            "requireProjectsKeyRoot": as_bool(
                deploy_cfg.get("requireProjectsKeyRoot", True), default=True
            ),
        }

    notes: list[str] = []
    if not deploy["host"] or deploy["host"] == "YOUR_SERVER_IP_OR_DNS":
        notes.append("Set deploy.host in vhost-deploy-config.json.")
    if not deploy["user"]:
        notes.append("Set deploy.user in vhost-deploy-config.json.")
    if not deploy["sshKeyPath"]:
        notes.append(
            f"Set deploy.sshKeyPath in vhost-deploy-config.json to a project key path under {deploy.get('projectsKeyRoot', DEFAULT_PROJECTS_KEY_ROOT)}."
        )
    elif deploy.get("requireProjectsKeyRoot", True) and not deploy[
        "sshKeyPath"
    ].startswith(deploy.get("projectsKeyRoot", DEFAULT_PROJECTS_KEY_ROOT).rstrip("/") + "/"):
        notes.append(
            f"Move deploy.sshKeyPath under {deploy.get('projectsKeyRoot', DEFAULT_PROJECTS_KEY_ROOT)} to avoid personal key usage."
        )

    return {
        "version": DEFAULT_BUILD_VER,
        "generatedAt": now_iso(),
        "copyPasteForCodex": True,
        "cwd": str(PROJECT_ROOT),
        "vhostPlanPath": str(DEFAULT_PLAN_PATH),
        "vhostDeployConfigPath": str(DEFAULT_DEPLOY_CFG_PATH),
        "vhostMigrationTargetsPath": str(PROJECT_ROOT / "data" / "vhost-migration-targets.json"),
        "vhostMigrationPlanPath": str(PROJECT_ROOT / "data" / "vhost-migration-plan.json"),
        "generatedNginxDir": str(out_dir / "nginx"),
        "projectCount": manifest.get("count", 0),
        "projects": projects,
        "deploy": deploy,
        "commands": {
            "generate_vhosts": (
                f"cd {shlex.quote(str(PROJECT_ROOT))} && "
                "python3 scripts/manage-vhosts.py"
            ),
            "deploy_vhosts": (
                f"cd {shlex.quote(str(PROJECT_ROOT))} && "
                "python3 scripts/manage-vhosts.py --deploy"
            ),
            "build_migration_plan": (
                f"cd {shlex.quote(str(PROJECT_ROOT))} && "
                "python3 scripts/build-vhost-migration-plan.py"
            ),
            "create_unique_sftp_account": (
                "PROJECT_SLUG='client' && USERNAME=\"c_${PROJECT_SLUG}_$(date +%y%m%d)_$(openssl rand -hex 2)\" && "
                "echo \"$USERNAME\" && "
                f"mkdir -p \"{DEFAULT_PROJECTS_KEY_ROOT}/${{PROJECT_SLUG}}/keys\" && "
                f"KEY=\"{DEFAULT_PROJECTS_KEY_ROOT}/${{PROJECT_SLUG}}/keys/${{USERNAME}}_m1_sftp\" && "
                "if [ ! -f \"$KEY\" ]; then ssh-keygen -t ed25519 -N '' -f \"$KEY\" -C \"$USERNAME@m1.local\"; fi && "
                "sudo USERNAME=\"$USERNAME\" PUBLIC_KEY_FILE=\"${KEY}.pub\" "
                f"{shlex.quote(str(DEFAULT_ACCOUNT_CREATE_SCRIPT))}"
            ),
        },
        "notes": notes,
    }


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_id(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")
    return cleaned or "project"


def ensure_domain(domain: str, label: str) -> str:
    d = domain.strip().lower()
    if not d:
        raise ValueError(f"{label} is required")
    if not DOMAIN_RE.match(d):
        raise ValueError(f"{label} is invalid: {domain}")
    return d


def normalize_aliases(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = [x.strip() for x in raw.split(",")]
    elif isinstance(raw, list):
        parts = [str(x).strip() for x in raw]
    else:
        raise ValueError("aliases must be a list or comma-separated string")
    out: list[str] = []
    seen: set[str] = set()
    for part in parts:
        if not part:
            continue
        alias = ensure_domain(part, "alias")
        if alias in seen:
            continue
        seen.add(alias)
        out.append(alias)
    return out


def normalize_project(raw: dict[str, Any], idx: int, defaults: dict[str, Any]) -> dict[str, Any]:
    domain = ensure_domain(str(raw.get("domain", "")), f"project[{idx}].domain")
    aliases = [a for a in normalize_aliases(raw.get("aliases")) if a != domain]
    project_type = str(raw.get("type", "static")).strip().lower()
    if project_type not in {"static", "proxy"}:
        raise ValueError(f"project[{idx}] type must be static|proxy, got: {project_type}")

    project_id = normalize_id(str(raw.get("id", "")).strip() or domain.replace(".", "-"))
    name = str(raw.get("name", "")).strip() or project_id
    enabled = as_bool(raw.get("enabled", True), default=True)
    tls_mode = str(raw.get("tls", "letsencrypt")).strip().lower()
    if tls_mode not in {"letsencrypt", "none"}:
        raise ValueError(f"project[{idx}] tls must be letsencrypt|none")
    force_https = as_bool(raw.get("forceHttps", tls_mode == "letsencrypt"), default=tls_mode == "letsencrypt")
    acme_webroot = str(
        raw.get("acmeWebroot")
        or defaults.get("acmeWebroot")
        or "/var/www/letsencrypt"
    ).strip()

    base: dict[str, Any] = {
        "id": project_id,
        "name": name,
        "domain": domain,
        "aliases": aliases,
        "type": project_type,
        "enabled": enabled,
        "tls": tls_mode,
        "forceHttps": force_https,
        "acmeWebroot": acme_webroot,
    }

    if project_type == "static":
        root = str(raw.get("root", "")).strip()
        if not root:
            raise ValueError(f"project[{idx}] static project needs root")
        base["root"] = root
        base["index"] = str(raw.get("index", "index.html")).strip() or "index.html"
        base["spa"] = as_bool(raw.get("spa", True), default=True)
    else:
        upstream = str(raw.get("upstream", "")).strip()
        if not upstream:
            raise ValueError(f"project[{idx}] proxy project needs upstream")
        if not re.match(r"^https?://", upstream):
            raise ValueError(f"project[{idx}] upstream must start with http:// or https://")
        base["upstream"] = upstream

    return base


def server_name_line(project: dict[str, Any]) -> str:
    names = [project["domain"], *project["aliases"]]
    return " ".join(names)


def render_site_content_block(project: dict[str, Any]) -> str:
    if project["type"] == "static":
        root = project["root"]
        index = project["index"]
        if project.get("spa", True):
            fallback = "try_files $uri $uri/ /index.html;"
        else:
            fallback = "try_files $uri $uri/ =404;"
        return (
            f"root {root};\n"
            f"index {index};\n\n"
            "location / {\n"
            f"    {fallback}\n"
            "}\n"
        )
    upstream = project["upstream"]
    return (
        "location / {\n"
        f"    proxy_pass {upstream};\n"
        "    proxy_http_version 1.1;\n"
        "    proxy_set_header Host $host;\n"
        "    proxy_set_header X-Real-IP $remote_addr;\n"
        "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        "    proxy_set_header X-Forwarded-Proto $scheme;\n"
        "    proxy_set_header Upgrade $http_upgrade;\n"
        "    proxy_set_header Connection \"upgrade\";\n"
        "}\n"
    )


def render_nginx_config(project: dict[str, Any]) -> str:
    names = server_name_line(project)
    content = render_site_content_block(project)
    tls_mode = project["tls"]
    force_https = project["forceHttps"]
    acme_webroot = project["acmeWebroot"]
    domain = project["domain"]

    def indent_block(block: str, spaces: int = 4) -> str:
        prefix = " " * spaces
        lines = block.strip("\n").splitlines()
        return "\n".join((prefix + line) if line else "" for line in lines) + "\n"

    indented_content = indent_block(content, spaces=4)

    if tls_mode == "none":
        return (
            f"# Auto-generated by manage-vhosts.py at {now_iso()}\n"
            f"# Project: {project['name']} ({project['id']})\n\n"
            "server {\n"
            "    listen 80;\n"
            "    listen [::]:80;\n"
            f"    server_name {names};\n\n"
            f"{indented_content}"
            "}\n"
        )

    port_80_content = (
        "location /.well-known/acme-challenge/ {\n"
        f"    root {acme_webroot};\n"
        "}\n\n"
    )
    if force_https:
        port_80_content += (
            "location / {\n"
            "    return 301 https://$host$request_uri;\n"
            "}\n"
        )
    else:
        port_80_content += content
    indented_port_80 = indent_block(port_80_content, spaces=4)

    return (
        f"# Auto-generated by manage-vhosts.py at {now_iso()}\n"
        f"# Project: {project['name']} ({project['id']})\n\n"
        "server {\n"
        "    listen 80;\n"
        "    listen [::]:80;\n"
        f"    server_name {names};\n\n"
        f"{indented_port_80}"
        "}\n\n"
        "server {\n"
        "    listen 443 ssl http2;\n"
        "    listen [::]:443 ssl http2;\n"
        f"    server_name {names};\n\n"
        f"    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;\n"
        f"    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;\n"
        "    include /etc/letsencrypt/options-ssl-nginx.conf;\n"
        "    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;\n\n"
        f"{indented_content}"
        "}\n"
    )


def normalize_plan(payload: dict[str, Any]) -> dict[str, Any]:
    defaults = payload.get("defaults", {}) if isinstance(payload.get("defaults"), dict) else {}
    projects_raw = payload.get("projects", [])
    if not isinstance(projects_raw, list):
        raise ValueError("projects must be a list")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_domains: set[str] = set()
    for idx, raw in enumerate(projects_raw):
        if not isinstance(raw, dict):
            raise ValueError(f"project[{idx}] must be an object")
        project = normalize_project(raw, idx, defaults)
        if project["id"] in seen_ids:
            raise ValueError(f"duplicate project id: {project['id']}")
        if project["domain"] in seen_domains:
            raise ValueError(f"duplicate project domain: {project['domain']}")
        seen_ids.add(project["id"])
        seen_domains.add(project["domain"])
        normalized.append(project)
    return {
        "version": str(payload.get("version", DEFAULT_BUILD_VER)).strip() or DEFAULT_BUILD_VER,
        "defaults": defaults,
        "projects": normalized,
    }


def generate_outputs(plan: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    nginx_dir = out_dir / "nginx"
    nginx_dir.mkdir(parents=True, exist_ok=True)

    active = [p for p in plan["projects"] if p.get("enabled", True)]
    generated: list[dict[str, Any]] = []

    for project in active:
        conf_name = f"{project['id']}.conf"
        conf_path = nginx_dir / conf_name
        conf_path.write_text(render_nginx_config(project), encoding="utf-8")
        generated.append(
            {
                "id": project["id"],
                "name": project["name"],
                "domain": project["domain"],
                "aliases": project["aliases"],
                "type": project["type"],
                "tls": project["tls"],
                "configFile": str(conf_path),
            }
        )

    manifest = {
        "generatedAt": now_iso(),
        "version": plan["version"],
        "count": len(generated),
        "projects": generated,
    }
    write_json(out_dir / "manifest.json", manifest)
    return manifest


def build_ssh_base(deploy_cfg: dict[str, Any]) -> list[str]:
    port = int(deploy_cfg.get("port", 22) or 22)
    args = [
        "-p",
        str(port),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]
    key_path = str(deploy_cfg.get("sshKeyPath", "")).strip()
    if key_path:
        args.extend(["-i", key_path])
    return args


def validate_deploy_key_policy(deploy_cfg: dict[str, Any]) -> None:
    if not as_bool(deploy_cfg.get("enabled", False), default=False):
        return

    key_path = str(deploy_cfg.get("sshKeyPath", "")).strip()
    if not key_path:
        raise ValueError(
            f"deploy sshKeyPath is required and must point to a project key under {DEFAULT_PROJECTS_KEY_ROOT}"
        )

    require_projects_root = as_bool(
        deploy_cfg.get("requireProjectsKeyRoot", True), default=True
    )
    projects_root = str(
        deploy_cfg.get("projectsKeyRoot", DEFAULT_PROJECTS_KEY_ROOT)
    ).rstrip("/")
    if require_projects_root and not key_path.startswith(projects_root + "/"):
        raise ValueError(
            f"deploy sshKeyPath must be under {projects_root} (got: {key_path})"
        )


def run_cmd(args: list[str], input_text: str | None = None) -> None:
    print("+", shlex.join(args))
    subprocess.run(args, input=input_text, text=True, check=True)


def deploy_manifest(manifest: dict[str, Any], deploy_cfg: dict[str, Any], out_dir: Path) -> None:
    if not as_bool(deploy_cfg.get("enabled", False), default=False):
        raise ValueError("vhost deploy config is disabled (set enabled=true to allow deploy)")
    validate_deploy_key_policy(deploy_cfg)

    host = str(deploy_cfg.get("host", "")).strip()
    user = str(deploy_cfg.get("user", "")).strip() or "ubuntu"
    if not host:
        raise ValueError("deploy host is required")

    files = [Path(x["configFile"]) for x in manifest["projects"]]
    if not files:
        print("No enabled projects to deploy. Skipping remote deployment.")
        return

    remote_tmp = str(deploy_cfg.get("remoteTempDir", "~/.openclaw-vhost-sync")).strip()
    remote_available = str(
        deploy_cfg.get("remoteSitesAvailableDir", "/etc/nginx/sites-available")
    ).strip()
    remote_enabled = str(
        deploy_cfg.get("remoteSitesEnabledDir", "/etc/nginx/sites-enabled")
    ).strip()
    remote_acme = str(
        deploy_cfg.get("remoteAcmeWebroot", "/var/www/letsencrypt")
    ).strip()
    test_cmd = str(deploy_cfg.get("testCommand", "sudo nginx -t")).strip()
    reload_cmd = str(
        deploy_cfg.get("reloadCommand", "sudo systemctl reload nginx")
    ).strip()
    auto_certbot = as_bool(deploy_cfg.get("autoCertbot", False), default=False)
    certbot_email = str(deploy_cfg.get("certbotEmail", "")).strip()

    ssh_base = ["ssh", *build_ssh_base(deploy_cfg)]
    scp_base = ["scp", *build_ssh_base(deploy_cfg)]
    remote = f"{user}@{host}"

    run_cmd([*ssh_base, remote, "mkdir -p " + shlex.quote(remote_tmp)])

    for conf in files:
        run_cmd([*scp_base, str(conf), f"{remote}:{remote_tmp}/{conf.name}"])

    remote_lines = [
        "set -euo pipefail",
        f"remote_tmp={shlex.quote(remote_tmp)}",
        f"remote_available={shlex.quote(remote_available)}",
        f"remote_enabled={shlex.quote(remote_enabled)}",
        f"remote_acme={shlex.quote(remote_acme)}",
        "sudo mkdir -p \"$remote_available\" \"$remote_enabled\" \"$remote_acme\"",
    ]
    for conf in files:
        name = conf.name
        remote_lines.append(
            f"if [ -f \"$remote_tmp/{name}\" ]; then sudo mv \"$remote_tmp/{name}\" \"$remote_available/{name}\"; fi"
        )
        remote_lines.append(
            f"sudo ln -sfn \"$remote_available/{name}\" \"$remote_enabled/{name}\""
        )
    remote_lines.extend([test_cmd, reload_cmd])

    if auto_certbot:
        if not certbot_email:
            raise ValueError("autoCertbot=true requires certbotEmail")
        for project in manifest["projects"]:
            domains = [project["domain"], *project.get("aliases", [])]
            domain_flags = " ".join(
                f"-d {shlex.quote(domain)}" for domain in domains
            )
            remote_lines.append(
                "sudo certbot certonly --webroot "
                f"-w \"$remote_acme\" --non-interactive --agree-tos --keep-until-expiring "
                f"--email {shlex.quote(certbot_email)} {domain_flags} || true"
            )
        remote_lines.extend([test_cmd, reload_cmd])

    remote_script = "\n".join(remote_lines) + "\n"
    run_cmd([*ssh_base, remote, "bash -s"], input_text=remote_script)

    deploy_report = {
        "deployedAt": now_iso(),
        "host": host,
        "user": user,
        "count": len(files),
        "autoCertbot": auto_certbot,
        "files": [str(p) for p in files],
    }
    write_json(out_dir / "last-deploy.json", deploy_report)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and deploy nginx virtual host config files from a JSON plan."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help=f"Path to vhost plan JSON (default: {DEFAULT_PLAN_PATH})",
    )
    parser.add_argument(
        "--deploy-config",
        type=Path,
        default=DEFAULT_DEPLOY_CFG_PATH,
        help=f"Path to deploy config JSON (default: {DEFAULT_DEPLOY_CFG_PATH})",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--write-normalized-plan",
        action="store_true",
        help="Overwrite --plan with normalized output after validation.",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy generated configs to remote host using --deploy-config.",
    )
    parser.add_argument(
        "--handoff-path",
        type=Path,
        default=DEFAULT_HANDOFF_PATH,
        help=f"Path to write Codex copy/paste handoff JSON (default: {DEFAULT_HANDOFF_PATH})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.plan.exists():
        print(f"Missing plan: {args.plan}", file=sys.stderr)
        return 1
    raw_plan = load_json(args.plan)
    plan = normalize_plan(raw_plan)

    if args.write_normalized_plan:
        write_json(args.plan, plan)

    manifest = generate_outputs(plan, args.out_dir)
    print(
        f"Generated {manifest['count']} nginx vhost config(s) in {args.out_dir / 'nginx'} "
        f"(version {plan['version']})."
    )

    deploy_cfg_for_handoff: dict[str, Any] | None = None
    if args.deploy_config.exists():
        deploy_cfg_for_handoff = load_json(args.deploy_config)
    handoff = build_codex_handoff(
        plan=plan,
        manifest=manifest,
        out_dir=args.out_dir,
        deploy_cfg=deploy_cfg_for_handoff,
    )
    write_json(args.handoff_path, handoff)
    print(f"Wrote Codex handoff JSON: {args.handoff_path}")

    if not args.deploy:
        print("Deploy skipped. Re-run with --deploy when ready.")
        return 0

    if not args.deploy_config.exists():
        print(f"Missing deploy config: {args.deploy_config}", file=sys.stderr)
        return 1

    deploy_cfg = deploy_cfg_for_handoff if deploy_cfg_for_handoff is not None else load_json(args.deploy_config)
    deploy_manifest(manifest, deploy_cfg, args.out_dir)
    print("Deploy completed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
