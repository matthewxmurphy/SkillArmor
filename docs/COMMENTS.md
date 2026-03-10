# ClawHub Comment Queue

Generated: 2026-03-06T01:00:02+00:00

Each item includes two POV drafts:
1. Safety/Runtime POV
2. Maintainer/Quality POV

## 1. `my-claw-shell`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `biosaylom`
- versions: `1`
- markdown present: `True`

### POV 1

[POV 1: Safety / Runtime]
Skill `my-claw-shell` by `biosaylom` is currently `high` risk with `critical` signal.
Observed behavior: Runs shell commands inside a dedicated tmux session named claw, returning the command output while restricting dangerous commands without confirmation.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author `biosaylom` appears to have no public repos and little/no public GitHub activity.
Legitimacy checks used:
- Owner handle reviewed: `biosaylom`.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- No public repositories observed on GitHub profile.
- No public follower activity observed.
- Profile metadata is sparse (bio/name/location/blog fields mostly empty).
- GitHub bio appears missing.
- GitHub display name appears missing.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: present.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 2. `terminal-command-execution`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `big-fox`
- versions: `1`
- markdown present: `True`

### POV 1

[POV 1: Safety / Runtime]
Skill `terminal-command-execution` by `big-fox` is currently `high` risk with `critical` signal.
Observed behavior: Execute terminal commands safely and reliably with clear pre-checks, output validation, and recovery steps. Use when users ask to run shell/CLI commands, ins...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author `big-fox` appears to have no public repos and little/no public GitHub activity.
Legitimacy checks used:
- Owner handle reviewed: `big-fox`.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- No public repositories observed on GitHub profile.
- No public follower activity observed.
- Profile metadata is sparse (bio/name/location/blog fields mostly empty).
- GitHub bio appears missing.
- GitHub display name appears missing.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: present.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 3. `high-risk-file-writes`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `Morpheus`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `high-risk-file-writes` by `Morpheus` is currently `high` risk with `critical` signal.
Observed behavior: The use of 'chmod +x' and 'rm -rf' commands by Morpheus indicates a high risk as these can be used to execute arbitrary code and delete critical files, potentially leading to data loss or system compromise.
Template guidance: No default template matched; manual review comment generated.

### POV 2

[POV 2: Maintainer / Quality]
Author `Morpheus` public profile currently shows 0 repos and 1 followers.
Legitimacy checks used:
- Owner handle reviewed: `Morpheus`.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- No public repositories observed on GitHub profile.
- Profile metadata is sparse (bio/name/location/blog fields mostly empty).
- GitHub bio appears missing.
- GitHub display name appears missing.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 4. `high-risk-sudo-usage`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `Morpheus`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `high-risk-sudo-usage` by `Morpheus` is currently `high` risk with `critical` signal.
Observed behavior: The use of 'sudo' without confirmation or in scripts ('sudo chmod +x') can lead to privilege escalation attacks. This is a high-risk finding that requires immediate attention and mitigation.
Template guidance: No default template matched; manual review comment generated.

### POV 2

[POV 2: Maintainer / Quality]
Author `Morpheus` public profile currently shows 0 repos and 1 followers.
Legitimacy checks used:
- Owner handle reviewed: `Morpheus`.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- No public repositories observed on GitHub profile.
- Profile metadata is sparse (bio/name/location/blog fields mostly empty).
- GitHub bio appears missing.
- GitHub display name appears missing.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 5. `skills-backup-claw-shell`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `Gexsta`
- versions: `1`
- markdown present: `True`

### POV 1

[POV 1: Safety / Runtime]
Skill `skills-backup-claw-shell` by `Gexsta` is currently `high` risk with `critical` signal.
Observed behavior: Clone variant with same shell passthrough handler pattern.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author `Gexsta` public profile currently shows 1 repos and 0 followers.
Legitimacy checks used:
- Owner handle reviewed: `Gexsta`.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- No public follower activity observed.
- Profile metadata is sparse (bio/name/location/blog fields mostly empty).
- GitHub bio appears missing.
- GitHub display name appears missing.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: present.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 6. `high-risk-shell-commands`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `Agent Smith`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `high-risk-shell-commands` by `Agent Smith` is currently `high` risk with `critical` signal.
Observed behavior: The presence of shell commands such as 'shell', 'exec', 'tmux send-keys', 'eval(', 'curl | bash', and 'wget | sh' poses a high risk due to potential execution of arbitrary code. These commands can be exploited to gain unauthorized access or perform malicious actions.
Template guidance: No default template matched; manual review comment generated.

### POV 2

[POV 2: Maintainer / Quality]
Author handle `Agent Smith` does not resolve to a public GitHub profile.
Legitimacy checks used:
- Owner handle reviewed: `Agent Smith`.
- No public ClawHub author bio field was present in this record.
- GitHub handle did not resolve to a public profile.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 7. `claw-shell`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `imaginelogo`
- versions: `1`
- markdown present: `True`

### POV 1

[POV 1: Safety / Runtime]
Skill `claw-shell` by `imaginelogo` is currently `high` risk with `critical` signal.
Observed behavior: Raw shell execution through tmux with blacklist-only filtering.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author `imaginelogo` public profile currently shows 2 repos and 0 followers.
Legitimacy checks used:
- Owner handle reviewed: `imaginelogo`.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- No public follower activity observed.
- Profile metadata is sparse (bio/name/location/blog fields mostly empty).
- GitHub bio appears missing.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: present.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 8. `macos-desktop-control`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `macos-desktop-control` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Automate macOS desktop by capturing screenshots and executing precise mouse movements, clicks, and keyboard inputs via cliclick.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 9. `gsd`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `gsd` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Get Shit Done - Full project planning and execution workflow. Handles project initialization with deep context gathering, automated research, roadmap creation, phase planning, and execution with verification.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 10. `multi-agent-collaboration`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `multi-agent-collaboration` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: 多智能体协作系统V1.4（最终版），支持**所有行业所有内容**的智能协作： 通用信息守护者(信息采集)、内容趋势优化系统(趋势创作)、状态洞察模块(个人状态)、工作流沉淀系统(报告生成)。 适用于：金融、医疗、教育、零售、科技、制造业、餐饮、服务业等**全行业**。 核心功能：意图识别+智能路由+反思机制+主动...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 11. `image-to-video`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `image-to-video` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Still-to-video conversion guide: model selection, motion prompting, and camera movement. Covers Wan 2.5 i2v, Seedance, Fabric, Grok Video with when to use ea...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 12. `automation-runner`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `automation-runner` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Executes approved shell commands, manages backups, and safely retrieves secrets from Bitwarden.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 13. `astra-docker`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `astra-docker` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Interact with Astra's Docker container workspace by executing commands and reading or writing files at /workspace inside the astra-env container.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 14. `error-recovery-automation`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `error-recovery-automation` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Standardize handling of common OpenClaw errors (gateway restart, browser service unavailable, cron failures) with automated recovery steps. Use when you need...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 15. `abby-browser`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `abby-browser` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: 基于 OpenClaw 的浏览器工具，支持自然语言控制网页打开、截图、点击、输入、表单填写、数据提取和页面操作。
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 16. `subagent-overseer`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `subagent-overseer` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Monitor sub-agent health and progress via a pull-based bash daemon. Use when spawning sub-agents that need progress tracking, staleness detection, and automa...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 17. `epistemic-council`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `epistemic-council` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Manage and execute all Epistemic Council pipeline operations including status checks, validations, audits, and adversarial re-challenges.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 18. `thor-generator`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `thor-generator` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Generate high-quality images locally using the ComfyUI Thor pipeline from user-provided text prompts.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 19. `dev-serve`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `dev-serve` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Start and manage tmux-backed dev servers exposed through Caddy at wildcard subdomains.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 20. `claw-shell-1-0-0`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `claw-shell-1-0-0` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Runs shell commands exclusively inside tmux session 'claw', captures output, and requests confirmation for potentially destructive commands.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 21. `pls-agent-tools`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `pls-agent-tools` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Provides utilities for safe file handling, JSON/YAML editing, regex text processing, system commands, encoding, date/time, and validation tasks.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 22. `n8n-workflow-templates`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `n8n-workflow-templates` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Production-ready n8n workflow templates for AI agents. Deploy pre-built automations for webhooks, RSS monitoring, health checks, social metrics, and data bac...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 23. `server-health-agent`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `server-health-agent` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Monitor VPS and server health metrics including real-time CPU usage, RAM utilization, disk usage, and Docker container status. Useful for DevOps monitoring,...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 24. `aetherlang-karpathy-skill`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `aetherlang-karpathy-skill` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Implement 10 advanced AI agent node types for any DSL/runtime system — plan compiler, code interpreter, critique loops, intelligent routing, multi-agent ense...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 25. `agent-synthesizer`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `agent-synthesizer` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Enable and configure Agent Synthesizer for OpenClaw to improve autonomy and execution throughput. Use when a user asks to install, set up, troubleshoot, or o...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 26. `agentgate-security`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `agentgate-security` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Enforces regex-based, real-time authorization policies on OpenClaw agents’ tool calls, blocking, allowing, or requiring approval before execution.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 27. `agent-os`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `agent-os` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Persistent agent operating system for OpenClaw. Agents remember across sessions, learn from experience, coordinate on complex projects without duplicate work.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 28. `url-intent-parser`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `url-intent-parser` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Parse product and landing URLs into an executable ads brief for Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, Shopify Ads, and...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 29. `browser-use-1-0-2`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `browser-use-1-0-2` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with w...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 30. `auto-workflow-builder`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `auto-workflow-builder` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Create and manage automated workflows visually with drag-and-drop triggers, actions, conditions, and 100+ integrations without coding.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 31. `dev-tools-pack`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `dev-tools-pack` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Collection of developer tools including Chrome extension templates, AI code reviews, GitHub README generators, SaaS landing pages, tech blogs, and tweet thre...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 32. `my-awesome-tools`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `my-awesome-tools` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Suite of shell scripts for developers to generate Chrome extensions, GitHub READMEs, SaaS landing pages, tech blogs, tweet threads, and automate code reviews.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 33. `pls-audit-website`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `pls-audit-website` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Perform comprehensive website health checks covering performance, broken links, security headers, accessibility, and SEO issues.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 34. `agent-browser-4`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `agent-browser-4` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 35. `fathom-meetings`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `fathom-meetings` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Access Fathom AI meeting recordings, transcripts, summaries, and action items via the Fathom API. Use when the user asks about meeting notes, call summaries,...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 36. `clawflow`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `clawflow` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Protocol for multi-agent collaboration via OpenClaw's message-passing and recursive task DAGs. Use this skill whenever the user wants to coordinate work acro...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 37. `qdrant-advanced`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `qdrant-advanced` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Advanced Qdrant vector database operations for AI agents. Semantic search, contextual document ingestion with chunking, collection management, snapshots, and...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 38. `fish-tts`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `fish-tts` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Generate high-quality speech from text using Fish Audio S1 and optionally upload the MP3 audio file to NextCloud via WebDAV.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 39. `research-reprompter`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `research-reprompter` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Transform rough research questions into executable USACF research prompts. Use when user says "research", "research this", "investigate", "deep dive", "resea...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 40. `track-flight`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `track-flight` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Track flights in real-time with detailed status, gate info, delays, and live position. Use when user asks to track a flight, check flight status, look up fli...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 41. `vscode-tunnel`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `vscode-tunnel` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Start VS Code Remote Tunnel in Docker containers for remote terminal access
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 42. `bilibili-player`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `bilibili-player` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: B 站视频播放器。用 Playwright 搜索 B 站视频并获取准确链接，然后用 open 命令在当前浏览器打开播放。Use when users request to play Bilibili videos or search for specific content.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 43. `enterprise-legal-guardrails-public`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `enterprise-legal-guardrails-public` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Legal/compliance guardrails for outbound OpenClaw actions (anti-spam, defamation, privacy, financial claims).
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 44. `telegram-media`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `telegram-media` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Send generated charts, photos, documents, and ElevenLabs TTS voice clips securely through Telegram using executed shell commands.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 45. `best-image`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `best-image` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Best quality AI image generation (~$0.12-0.20/image). Text-to-image, image-to-image, and image editing via the EvoLink API.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 46. `query-dbpedia`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `query-dbpedia` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Transform natural language questions into SPARQL queries for DBpedia and generate beautiful HTML results pages. Query the DBpedia knowledge graph using plain...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 47. `supabase-query`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `supabase-query` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Query Supabase projects - count users, list signups, check stats. Use for database queries and user analytics.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 48. `pmctl`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `pmctl` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Browse and inspect Postman collections, requests, and environments from the terminal using pmctl. Use when you need to discover API endpoints, look up reques...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 49. `atlas-argos`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `atlas-argos` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Gestor autónomo e operador executivo do ecossistema ARGOS.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 50. `cheapest-image`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `cheapest-image` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Possibly the cheapest AI image generation (~$0.0036/image). Text-to-image via the EvoLink API.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 51. `nyne-deep-research`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `nyne-deep-research` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Research any person using the Nyne Deep Research API. Submit an email, phone, social URL, or name and receive a comprehensive intelligence dossier with psych...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 52. `acp-job-submitter`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `acp-job-submitter` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Submit jobs to other ACP agents and earn from the spread | 提交ACP Jobs賺取差價
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 53. `shelly-seo-analyzer`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `shelly-seo-analyzer` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Analyze any webpage URL for SEO issues and get actionable recommendations. Checks title tags, meta descriptions, heading structure, keyword density, image al...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 54. `percept-voice-cmd`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `percept-voice-cmd` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Detects wake words in speech and routes voice commands like email, text, reminders, search, and notes to OpenClaw agents for execution.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 55. `local-task-runner`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `local-task-runner` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Executes Node.js code snippets or scripts locally with isolation, cleanup, and timeout, serving as a lightweight alternative to spawning subagents.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 56. `jsrt-claw`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `jsrt-claw` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Automate Windows system tasks by generating and running a single JavaScript file using Microsoft JsRT with COM objects and fallback support.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 57. `hz-error-guard`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `hz-error-guard` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Monitors, classifies, intercepts errors in real-time, enforces auto-retry and circuit breaking, and ensures graceful recovery and prevention.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 58. `shelly-invoice-generator`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `shelly-invoice-generator` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Generate professional invoices in Markdown or HTML by specifying client, items, tax, currency, dates, and output format.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 59. `clawlife`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `clawlife` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Give your agent a home in a shared pixel world. Own a room, visit neighbors, earn shells, customize your lobster avatar, and build real relationships. Use wh...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 60. `shelly-competitor-analyzer`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `shelly-competitor-analyzer` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Generates a detailed report on a company's market position, pricing, social activity, recent news, and strengths by analyzing its name or URL.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 61. `shelly-landing-gen`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `shelly-landing-gen` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Generate complete, responsive HTML landing pages from a product name, tagline, and description. Clean CSS, mobile-ready, with hero, features, CTA, and footer...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 62. `humanize-image`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `humanize-image` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Detect and remove AI fingerprints from AI-generated images. Strip metadata, add film grain, recompress, and bypass AI image detectors. Works with Midjourney,...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 63. `openclaw-switch`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `openclaw-switch` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Manage multi-provider model switching and fallback chains in OpenClaw. "OpenClaw Switch" helps users set up automatic model failover (e.g. 429 rate-limit → f...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 64. `skill-optimizer`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `skill-optimizer` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Analyzes AI conversation logs to evaluate skill performance and generate optimization suggestions. Use when user mentions "优化技能", "迭代技能", "skill optimization...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 65. `task-orchestra`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `task-orchestra` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Coordinate multiple agents and tasks for complex workflows. Orchestrate subagents, manage dependencies, handle parallel execution, and ensure successful comp...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 66. `dacker`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `dacker` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Installs and uses Docker reliably with official docs. Use when installing Docker (Desktop or Engine), building or running containers, writing Dockerfiles, us...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 67. `cord-sentinel`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `cord-sentinel` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: SENTINEL/CORD governance engine — mandatory pre-flight enforcement for agent tool calls. Use when: (1) about to run exec/write/browser/network/message tool c...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 68. `cancorteaw-app`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `cancorteaw-app` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Manage Expo React Native apps on OpenClaw: create apps, add screens, start web previews on localhost, and check preview status safely within /home/patron/apps.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 69. `generate-news-article`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `generate-news-article` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Generate individual Markdown articles from SerpAPI Google search results with images
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 70. `claude-code-launcher`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `claude-code-launcher` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Launch Claude Code in a new terminal window with Remote Control enabled. Use when opening a project for interactive coding sessions where you need to access...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 71. `agos-claw-chat`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `agos-claw-chat` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Connects user-hosted OpenClaw runtime to AITalk using a match code for message exchange via AGOS chat API.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 72. `clawhub-skill-smart-cron`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `clawhub-skill-smart-cron` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Schedule OpenClaw tasks using natural language with full cron lifecycle, timezone support, failure alerts, and execution logs without needing cron syntax.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 73. `snowflake`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `snowflake` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Execute read-only Snowflake SELECT queries with forbidden keyword blocking, row limits, timeouts, and structured JSON results.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 74. `contract-review`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `contract-review` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Legal contract analysis using CUAD dataset (41 risk categories). Supports NDA, SaaS, M&A, employment, payment/merchant, and finder/broker agreements. Identif...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 75. `qr-code-generator-skill`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `qr-code-generator-skill` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: A precision utility to generate QR code images from URLs or text using Python.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 76. `tmux-remote-control`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `tmux-remote-control` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 77. `tmux-controller`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `tmux-controller` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 78. `openclaw-agent-compute`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `openclaw-agent-compute` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Public HTTP client skill exposing compute.* tools by calling a private Compute Gateway over HTTPS. Includes a starter kit to run OpenClaw preconfigured.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 79. `freeapi`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `freeapi` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Connect directly to any API using its OpenAPI spec with local API key storage, ensuring private, middleware-free requests from your machine.
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

## 80. `ssh-netmiko`

- status: `queued`
- risk/signal: `high` / `critical`
- owner: `unknown`
- versions: `1`
- markdown present: `False`

### POV 1

[POV 1: Safety / Runtime]
Skill `ssh-netmiko` by `unknown` is currently `high` risk with `critical` signal.
Observed behavior: Provides access to the MCP_Server_Trigger (v0.1.0) MCP server. It offers 7 tool(s): {"close_ssh_session":"\nFecha uma sessão SSH ativa.\n\nArgs:\n session_id...
Template guidance: I reviewed this skill locally. The implementation executes raw shell commands through tmux and relies on blacklist-only filtering for dangerous commands. That pattern is bypassable and risky for destructive execution. Please move to an allowlist or explicit per-command approval model before this should be considered trusted.

### POV 2

[POV 2: Maintainer / Quality]
Author identity is unknown in this source record.
Legitimacy checks used:
- ClawHub source did not provide a stable owner handle.
- No public ClawHub author bio field was present in this record.
- GitHub profile lookup completed.
- SKILL.md evidence missing in sampled artifacts.
- Only one visible release/version in current metadata.
Version history observed: 1 release(s).
SKILL.md evidence: missing.
Request: add/expand public docs, publish transparent version notes, and narrow any risky behavior scope.

