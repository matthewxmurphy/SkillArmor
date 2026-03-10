# ClawHub Trust Audit

Generated: 2026-03-04T17:00:26-08:00
Scope: merged_local_big_pickel_public_index (2510 findings)

## Findings Summary

- high: 197
- high_operational: 402
- medium: 147
- review_needed: 1690
- low: 74
- signal critical: 198
- signal high: 489
- signal medium: 1031
- signal low: 792

## Runtime Signals

- none

## Ranked Findings

1. `my-claw-shell` | signal `critical` | risk `high` | owner `biosaylom` | installs 5 | downloads 298 | docs present | releases single-release
   - Runs shell commands inside a dedicated tmux session named claw, returning the command output while restricting dangerous commands without confirmation.
   - owner-signal `high` flags: no_public_repos, no_followers, sparse_public_profile, avatar_generic_possible
2. `terminal-command-execution` | signal `critical` | risk `high` | owner `big-fox` | installs 0 | downloads 45 | docs present | releases single-release
   - Execute terminal commands safely and reliably with clear pre-checks, output validation, and recovery steps. Use when users ask to run shell/CLI commands, ins...
   - owner-signal `high` flags: no_public_repos, no_followers, sparse_public_profile, avatar_generic_possible
3. `high-risk-file-writes` | signal `critical` | risk `high` | owner `Morpheus` | installs 0 | downloads 0 | docs missing-in-sample | releases single-release
   - The use of 'chmod +x' and 'rm -rf' commands by Morpheus indicates a high risk as these can be used to execute arbitrary code and delete critical files, potentially leading to data loss or system compromise.
   - owner-signal `high` flags: no_public_repos, sparse_public_profile, stale_profile_activity, avatar_generic_possible
4. `high-risk-sudo-usage` | signal `critical` | risk `high` | owner `Morpheus` | installs 0 | downloads 0 | docs missing-in-sample | releases single-release
   - The use of 'sudo' without confirmation or in scripts ('sudo chmod +x') can lead to privilege escalation attacks. This is a high-risk finding that requires immediate attention and mitigation.
   - owner-signal `high` flags: no_public_repos, sparse_public_profile, stale_profile_activity, avatar_generic_possible
5. `skills-backup-claw-shell` | signal `critical` | risk `high` | owner `Gexsta` | installs 3 | downloads 315 | docs present | releases single-release
   - Clone variant with same shell passthrough handler pattern.
   - owner-signal `medium` flags: very_few_public_repos, no_followers, sparse_public_profile, avatar_generic_possible
6. `high-risk-shell-commands` | signal `critical` | risk `high` | owner `Agent Smith` | installs 0 | downloads 0 | docs missing-in-sample | releases single-release
   - The presence of shell commands such as 'shell', 'exec', 'tmux send-keys', 'eval(', 'curl | bash', and 'wget | sh' poses a high risk due to potential execution of arbitrary code. These commands can be exploited to gain unauthorized access or perform malicious actions.
   - owner-signal `medium` flags: github_profile_not_found
7. `claw-shell` | signal `critical` | risk `high` | owner `imaginelogo` | installs 95 | downloads 5964 | docs present | releases single-release
   - Raw shell execution through tmux with blacklist-only filtering.
   - owner-signal `low` flags: very_few_public_repos, no_followers, partial_public_profile
8. `macos-desktop-control` | signal `critical` | risk `high` | owner `unknown` | installs 9 | downloads 895 | docs missing-in-sample | releases single-release
   - Automate macOS desktop by capturing screenshots and executing precise mouse movements, clicks, and keyboard inputs via cliclick.
   - owner-signal `none` flags: none
9. `gsd` | signal `critical` | risk `high` | owner `unknown` | installs 7 | downloads 873 | docs missing-in-sample | releases single-release
   - Get Shit Done - Full project planning and execution workflow. Handles project initialization with deep context gathering, automated research, roadmap creation, phase planning, and execution with verification.
   - owner-signal `none` flags: none
10. `multi-agent-collaboration` | signal `critical` | risk `high` | owner `unknown` | installs 5 | downloads 288 | docs missing-in-sample | releases single-release
   - 多智能体协作系统V1.4（最终版），支持**所有行业所有内容**的智能协作： 通用信息守护者(信息采集)、内容趋势优化系统(趋势创作)、状态洞察模块(个人状态)、工作流沉淀系统(报告生成)。 适用于：金融、医疗、教育、零售、科技、制造业、餐饮、服务业等**全行业**。 核心功能：意图识别+智能路由+反思机制+主动...
   - owner-signal `none` flags: none
11. `image-to-video` | signal `critical` | risk `high` | owner `unknown` | installs 4 | downloads 352 | docs missing-in-sample | releases single-release
   - Still-to-video conversion guide: model selection, motion prompting, and camera movement. Covers Wan 2.5 i2v, Seedance, Fabric, Grok Video with when to use ea...
   - owner-signal `none` flags: none
12. `automation-runner` | signal `critical` | risk `high` | owner `unknown` | installs 3 | downloads 201 | docs missing-in-sample | releases single-release
   - Executes approved shell commands, manages backups, and safely retrieves secrets from Bitwarden.
   - owner-signal `none` flags: none
13. `astra-docker` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 287 | docs missing-in-sample | releases single-release
   - Interact with Astra's Docker container workspace by executing commands and reading or writing files at /workspace inside the astra-env container.
   - owner-signal `none` flags: none
14. `error-recovery-automation` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 273 | docs missing-in-sample | releases single-release
   - Standardize handling of common OpenClaw errors (gateway restart, browser service unavailable, cron failures) with automated recovery steps. Use when you need...
   - owner-signal `none` flags: none
15. `abby-browser` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 217 | docs missing-in-sample | releases single-release
   - 基于 OpenClaw 的浏览器工具，支持自然语言控制网页打开、截图、点击、输入、表单填写、数据提取和页面操作。
   - owner-signal `none` flags: none
16. `subagent-overseer` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 212 | docs missing-in-sample | releases single-release
   - Monitor sub-agent health and progress via a pull-based bash daemon. Use when spawning sub-agents that need progress tracking, staleness detection, and automa...
   - owner-signal `none` flags: none
17. `epistemic-council` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 186 | docs missing-in-sample | releases single-release
   - Manage and execute all Epistemic Council pipeline operations including status checks, validations, audits, and adversarial re-challenges.
   - owner-signal `none` flags: none
18. `thor-generator` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 160 | docs missing-in-sample | releases single-release
   - Generate high-quality images locally using the ComfyUI Thor pipeline from user-provided text prompts.
   - owner-signal `none` flags: none
19. `dev-serve` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 108 | docs missing-in-sample | releases single-release
   - Start and manage tmux-backed dev servers exposed through Caddy at wildcard subdomains.
   - owner-signal `none` flags: none
20. `claw-shell-1-0-0` | signal `critical` | risk `high` | owner `unknown` | installs 2 | downloads 34 | docs missing-in-sample | releases single-release
   - Runs shell commands exclusively inside tmux session 'claw', captures output, and requests confirmation for potentially destructive commands.
   - owner-signal `none` flags: none
21. `pls-agent-tools` | signal `critical` | risk `high` | owner `unknown` | installs 1 | downloads 707 | docs missing-in-sample | releases single-release
   - Provides utilities for safe file handling, JSON/YAML editing, regex text processing, system commands, encoding, date/time, and validation tasks.
   - owner-signal `none` flags: none
22. `n8n-workflow-templates` | signal `critical` | risk `high` | owner `unknown` | installs 1 | downloads 447 | docs missing-in-sample | releases single-release
   - Production-ready n8n workflow templates for AI agents. Deploy pre-built automations for webhooks, RSS monitoring, health checks, social metrics, and data bac...
   - owner-signal `none` flags: none
23. `server-health-agent` | signal `critical` | risk `high` | owner `unknown` | installs 1 | downloads 396 | docs missing-in-sample | releases single-release
   - Monitor VPS and server health metrics including real-time CPU usage, RAM utilization, disk usage, and Docker container status. Useful for DevOps monitoring,...
   - owner-signal `none` flags: none
24. `aetherlang-karpathy-skill` | signal `critical` | risk `high` | owner `unknown` | installs 1 | downloads 239 | docs missing-in-sample | releases single-release
   - Implement 10 advanced AI agent node types for any DSL/runtime system — plan compiler, code interpreter, critique loops, intelligent routing, multi-agent ense...
   - owner-signal `none` flags: none
25. `agent-synthesizer` | signal `critical` | risk `high` | owner `unknown` | installs 1 | downloads 194 | docs missing-in-sample | releases single-release
   - Enable and configure Agent Synthesizer for OpenClaw to improve autonomy and execution throughput. Use when a user asks to install, set up, troubleshoot, or o...
   - owner-signal `none` flags: none

## Developer Pattern Notes

- `cross_owner_clone_cluster` `high`: Multiple owners share reasonCode `shell_passthrough_blacklist` across similar risky findings.
- `cross_owner_clone_cluster` `medium`: Multiple owners share reasonCode `high_stakes_finance` across similar risky findings.
- `cross_owner_clone_cluster` `medium`: Multiple owners share reasonCode `secret_in_argv` across similar risky findings.
- `cross_owner_clone_cluster` `medium`: Multiple owners share reasonCode `defensive_pattern` across similar risky findings.
- `same_owner_repeat_risk` `high`: Owner `Morpheus` has multiple medium/high risk findings in current dataset.
- `same_owner_repeat_risk` `high`: Owner `Trinity` has multiple medium/high risk findings in current dataset.
- `same_owner_repeat_risk` `high`: Owner `unknown` has multiple medium/high risk findings in current dataset.

## Recommended Next Actions

1. Post evidence-based comments on high-risk findings and queue safe replacements.
2. Add mandatory simulation/confirmation guardrails to operational-risk skills.
3. Patch medium-risk secret handling and enforce env-only token patterns.
4. Escalate repeat-risk owners into deeper review cycle.
5. Re-run analytizer after each publish cycle and compare deltas.
