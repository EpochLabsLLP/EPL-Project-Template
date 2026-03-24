# Changelog

All notable changes to the EPL Project Template are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions use [Semantic Versioning](https://semver.org/).

Upgrade projects with `/template-sync --apply`. See Migration Notes for version-specific instructions.

---

## [2.8.1] - 2026-03-24

### Added
- **`/work` skill** — Unified autonomous work pickup and execution sequence. 8-step process: check stop-work, read progress log, check checkpoint, read Work Ledger, evaluate in-progress WOs, pick next WO, execute full lifecycle, escalate if blocked. Designed for unattended CLI heartbeats — agents proceed without asking for approval. Also works in interactive VS Code sessions.

### Changed
- Template CLAUDE.md skill table now includes `/work`
- `TEMPLATE_MANIFEST.json` updated with `work/SKILL.md`

### Migration Notes
- **From v2.8.0**: Run `/template-sync --apply`. Purely additive — adds the `/work` skill directory and updates the skill table reference.

---

## [2.8.0] - 2026-03-23

### Added
- **Multi-Instance Collaboration Protocol (foundation):** Support for multiple Claude instances (VS Code + CLI heartbeats) working in the same repo without conflicts.
  - **Instance Identity:** `instance-id.sh` generates session-unique stamps (`{agent}-{env}-{YYYYMMDD}-{HHMM}`) at session start. Used to fingerprint progress log entries, session summaries, and created files. Detects VS Code vs CLI automatically.
  - **Progress Log:** `progress-log.sh` provides append-only activity journal at `.claude/progress.log`. Instance-stamped entries enable cross-session and cross-instance awareness. Session hooks display recent entries on startup/resume/compact.
  - **Stop Work Order:** All three session hooks now check `.claude/stop-work.md` FIRST. If present, the session halts immediately with the stop reason displayed. Emergency brake for critical issues discovered by any instance.
  - **Multi-Instance Awareness section** added to template CLAUDE.md — rules for checkpoint scoping, progress logging, and conflict avoidance.
  - **Project abbreviation file:** `.claude/project-abbreviation` (optional) sets the agent name prefix for instance IDs.

### Changed
- All 3 session hooks now source `instance-id.sh` and `progress-log.sh`
- `session-start.sh` generates instance ID, checks stop-work, displays progress log, logs session start
- `session-resume.sh` and `session-compact.sh` check stop-work and display progress log
- Observability events now include `instance_id` metadata
- `.gitignore` updated: `.claude/instance-id` and `.claude/progress.log` are local-only
- `TEMPLATE_MANIFEST.json` updated with new infrastructure files

### Migration Notes
- **From v2.7.0**: Run `/template-sync --apply`. All changes are additive and backward-compatible. Stop-work and progress log features activate automatically. To set your project's instance ID prefix, create `.claude/project-abbreviation` with your abbreviation (e.g., `atlas`). Without it, the directory name is used.

---

## [2.7.0] - 2026-03-23

### Added
- **Dynamic Tool Scoping (advisory):** Phase-aware tool guidance system. `detect_phase.py` derives the current SDD phase (SPEC/PLANNING/IMPLEMENTATION/VALIDATION/MAINTENANCE) from project state — no explicit marker needed. `phase-scope.sh` hook fires on all Bash/Edit/Write tool calls and outputs advisory `systemMessage` when a tool is unusual for the current phase (e.g., code editing during spec authoring, spec creation during implementation). Restriction table in `.claude/phase-restrictions.json` (scaffolding — project-customizable).
- **Phase banner in session start:** Session-start hook now displays `[CURRENT PHASE: IMPLEMENTATION]` (or whatever the detected phase is) at the top of the session context.
- `/integration-logic` upgraded: now defaults to checking ALL completed modules when invoked without arguments (previously required two specific module names).

### Changed
- `session-start.sh` displays detected phase
- `phase-scope.sh` registered on `Bash|Edit|Write` matcher
- `TEMPLATE_MANIFEST.json` updated with new infrastructure files and hook registrations

### Migration Notes
- **From v2.6.0**: Run `/template-sync --apply`. Phase scoping is advisory-only (no tool calls blocked). Projects can customize `.claude/phase-restrictions.json` to adjust advisories for their workflow. `detect_phase.py` caches results for 5 seconds to minimize overhead.

---

## [2.6.0] - 2026-03-22

### Added
- **Checkpoint/Resume system:** `.claude/checkpoint.md` — structured scratchpad written by agents at WO lifecycle transitions (IN-PROGRESS, milestones, quality gates, DONE). Session hooks auto-inject checkpoint state on crash/compact/start for context recovery. Follows Anthropic's `claude-progress.txt` harness pattern.
- **Governance observability:** All 6 gate hooks now emit structured events to `.claude/observability/events.jsonl` (JSONL, <10ms per emit, fail-open). Session lifecycle events (start, resume, compact) also logged. `aggregate_events.py` computes compliance metrics displayed at session start.
- **Shared hook utilities:** `observe.sh` (event emission) and `checkpoint.sh` (checkpoint reader) sourced by all hooks — DRY infrastructure.
- **Checkpoint Protocol** added to `execution-protocol.md` — mandatory agent instruction for when/how to write checkpoints.
- **Compliance metrics in session banner:** Session start displays `Compliance: 95% (19/20 allowed) | Blocks: 1 spec-gate | Compactions: 2`.

### Changed
- All 9 hooks (6 gate + 3 session) now source `observe.sh` for event emission
- All 3 session hooks now source `checkpoint.sh` for checkpoint display
- `.gitignore` updated: `.claude/observability/` and `.claude/checkpoint.md` are local-only (not committed)
- CLAUDE.md template updated with Checkpoint/Resume and Observability under Governance Heartbeat

### Migration Notes
- **From v2.5.4**: Run `/template-sync --apply`. All new files are infrastructure (auto-deployed). Checkpoint writing is agent-driven (no new hooks in settings.json required). Observability events accumulate automatically from existing hook invocations.

---

## [2.5.4] - 2026-03-22

### Fixed
- **Code-gate Bash bypass closed:** `spec-gate.sh` now triggers on `PreToolUse → Bash` in addition to `Edit|Write`. Detects file-writing Bash commands (`cat >`, `echo >`, `tee`, `cp`, `mv`, `mkdir -p`) targeting code directories and enforces the same frozen-spec + active-WO requirements. Previously, agents could bypass governance entirely by using Bash heredocs/redirects instead of Claude Code's Edit/Write tools. Inspired by harness engineering principle: "Constraint > Documentation."
- **Tier 0: Flip On the Lights** added to `problem-solving.md`: New mandatory first step — search project specs, epoch-search, decision records, and research docs BEFORE reasoning from scratch. Prevents agents from re-deriving what's already documented.

### Changed
- `spec-gate.sh` registered on both `Bash` and `Edit|Write` matchers in `settings.json`
- `problem-solving.md` restructured: Tier 0 (search docs) → Tier 1 (read/trace) → Tier 2 (internal) → Tier 3 (external) → Tier 4 (escalate)

### Migration Notes
- **From v2.5.3**: Run `/template-sync --apply`. Both fixes are infrastructure (auto-deployed). The spec-gate now fires on Bash commands — agents can no longer use shell redirects to bypass governance.

---

## [2.5.3] - 2026-03-17

### Added
- **Agent Mail system** (`/mail` skill + inbox hooks): Cross-project async messaging. Agents can send structured messages (with priority and type) to other projects' inboxes. Session start/resume/compact hooks auto-surface unread messages. Urgent messages are flagged for immediate attention. Permanent audit trail in `.claude/inbox/_processed/`.
- **Project registry** (`_SharedCore/project_registry.json`): Central lookup for project names → filesystem paths. Used by `/mail` to resolve target inboxes. Supports multi-OS path roots (Windows + macOS).
- **Agent Mail section in CLAUDE.md template**: Documents the inbox system, `/mail` invocation, and message lifecycle.

### Migration Notes
- **From v2.5.2**: Run `/template-sync --apply`. The `/mail` skill and hook updates are infrastructure (auto-deployed). Create `_SharedCore/project_registry.json` if it doesn't exist (template sync doesn't manage `_SharedCore`). Inbox directories are created on-demand by the `/mail` skill.

---

## [2.5.2] - 2026-03-17

### Fixed
- **Cross-platform hook compatibility (macOS):** All 9 shell hooks now use portable Python detection (`python3` → `python` fallback) instead of bare `python`. macOS ships only `python3`; bare `python` caused every hook to fail silently on Mac.
- **CRLF line ending corruption:** Added `.gitattributes` forcing LF line endings for `*.sh` and `*.py` files. Windows `core.autocrlf=true` was injecting `\r` into shell scripts, causing `\r: command not found` errors on macOS/Linux.

### Migration Notes
- **From v2.5.1**: Run `/template-sync --apply`. Both fixes are infrastructure (auto-deployed). After sync, verify hooks work on macOS with `bash .claude/hooks/session-start.sh`.

---

## [2.5.1] - 2026-03-16

### Changed
- **`problem-solving.md` rule**: Strengthened anti-wall-banging enforcement. Failed fix attempts now explicitly count as tier actions — agents cannot try multiple fix variations at the same tier without researching first. Added "stop hitting, start reading" principle and reinforced each tier's purpose (Tier 1: diagnose, Tier 2: understand internally, Tier 3: research externally). Addresses agents burning context on repeated blind fix attempts instead of stepping back to gather understanding.

### Migration Notes
- **From v2.5.0**: Run `/template-sync --apply`. The updated `problem-solving.md` is infrastructure (auto-deployed).

---

## [2.5.0] - 2026-03-15

### Added
- **`.mcp.json` template** (scaffolding): Pre-configured MCP servers for the Epoch Labs shared memory system — `memory-db` (local SQLite at `claude_memory.db`), `supabase-dev` (cloud PostgreSQL + pgvector + knowledge graph), and `context7` (library documentation). Agents in every project now have immediate access to session history, project context, knowledge graph, and semantic search without manual configuration.
- **Memory System section in `CLAUDE.md`**: Documents the three MCP servers and provides guidance on when/how agents should use the memory system (session start/end, research, document registration).
- **`intellectual-honesty.md` rule** (infrastructure): Three-part rule addressing agent behavior:
  - **Research before opinion:** Agents must verify claims before stating them as fact. No bluffing — "I'm not sure, let me check" beats a confident guess.
  - **Truthful quality reporting:** No sugarcoating completeness, hiding failures, or burying bad news in optimistic framing. Nathan makes business decisions based on agent reports.
  - **Observation vs. speculation:** Agents must clearly label what they verified, what they inferred, and what they're guessing.

### Changed
- **`TEMPLATE_MANIFEST.json`**: Added `intellectual-honesty.md` to infrastructure files; added `.mcp.json` to scaffolding files. Version bump to 2.5.0.

### Migration Notes
- **From v2.4.3**: Run `/template-sync --apply`. The sync will deploy the new `intellectual-honesty.md` rule (infrastructure, auto-deployed). `.mcp.json` is scaffolding — it will be created if absent but won't overwrite an existing project `.mcp.json`. If your project already has a `.mcp.json`, manually add the `memory-db` and `supabase-dev` servers from the template version. The CLAUDE.md Memory System section must be added manually (scaffolding — use `/template-migrate` if needed).

---

## [2.4.3] - 2026-03-15

### Added
- **Plugin Marketplace integration**: Template now declares the Anthropic Agent Skills marketplace (`anthropics/skills`) in `settings.json` via `extraKnownMarketplaces` and `enabledPlugins`. Projects will prompt users to install the marketplace on first trust. Skills like skill-creator, frontend-design, and webapp-testing are now consumed from the marketplace (always up-to-date) rather than shipped as local copies.
- **Marketplace merge in `template_sync.py`**: The sync engine now merges `extraKnownMarketplaces` and `enabledPlugins` from the manifest into project `settings.json`, following the same additive-only philosophy as hook merging. Never removes project marketplaces or plugins.
- **`marketplace_registrations` in `TEMPLATE_MANIFEST.json`**: Single source of truth for marketplace declarations, parallel to `hook_registrations`.

### Removed
- **Local `skill-creator/SKILL.md`**: Replaced by `example-skills@anthropic-agent-skills` marketplace plugin. The marketplace version auto-updates and is always authoritative.
- **Local `frontend-design/SKILL.md`**: Same — now from marketplace.
- **Local `webapp-testing/` (SKILL.md + scripts + examples)**: Same — now from marketplace.

### Changed
- **`TEMPLATE_MANIFEST.json`**: Added `marketplace_registrations` section; removed 3 Anthropic skill files from infrastructure list (skill-creator, frontend-design, webapp-testing). Updated managed_scaffolding description to include marketplace declarations.
- **`CLAUDE.md` template**: Removed skill-creator, frontend-design, webapp-testing from local skills table. Added marketplace note directing users to accept the marketplace prompt or check `/plugin marketplace list`.

### Migration Notes
- **From v2.4.2**: Run `/template-sync --apply`. The sync will add marketplace declarations to your `settings.json` and remove the 3 local Anthropic skill copies (replaced by marketplace versions). On next session start, Claude Code will prompt you to install the Anthropic Agent Skills marketplace — accept it to get auto-updating skills.
- **If marketplace is unavailable** (offline, CI, etc.): The 16 governance skills remain local and fully functional. Only skill-creator, frontend-design, and webapp-testing require marketplace access.

---

## [2.4.2] - 2026-03-14

### Fixed
- **Skill frontmatter spelling**: Corrected `user-invokable` to `user-invocable` (with "c") across 8 skill files. The prior spelling was silently ignored by Claude Code — no functional impact since default is `true`, but would have caused silent failures for any skill set to `false`.

### Changed
- **skill-creator/SKILL.md**: Updated frontmatter documentation to list `user-invocable` and `disable-model-invocation` as Claude Code extension fields, distinct from the 6 agent-skills-spec standard fields.

---

## [2.4.1] - 2026-03-08

### Added
- **`/unlock-frozen` skill**: Formal edit authorization for frozen spec files. Agent must provide scope, rationale, and authorization reference before a one-shot bypass is granted. All authorizations are permanently logged to `.claude/frozen-edit-log.md` for audit trail. One bypass at a time, consumed after a single write.

### Changed
- **`protect-frozen-files.sh`**: Checks for `.claude/frozen-bypass` marker before blocking frozen spec edits. Marker is consumed (deleted) after one write — subsequent edits require a new `/unlock-frozen` authorization.

---

## [2.4.0] - 2026-03-08

### Added
- **Vertical-first build architecture**: Waves restructured as vertical feature threads instead of horizontal layers. Walking Skeleton (Wave 0) is mandatory — proves architecture with thinnest end-to-end slice before feature work begins.
- **Task Type field**: Blueprint task cards and Work Orders now carry `Task Type` (IMPLEMENTATION, INTEGRATION, SKELETON, E2E_VALIDATION). Pre-v2.4.0 tasks default to IMPLEMENTATION.
- **INTEGRATION tasks**: Every row in the Engineering Spec's Module Integration Matrix should have a corresponding INTEGRATION-type task in the Blueprint. Integration is a task, not a phase.
- **E2E_VALIDATION capstone**: The last task in every wave must be E2E_VALIDATION, validating the complete feature flow end-to-end.
- **`/wave-complete` skill**: Validates wave exit criteria — all tasks DONE, all INTEGRATION tasks WIRED, E2E capstone passed, traceability intact. Required before proceeding to next wave.
- **`/feature-complete` skill**: Validates a PVD feature is fully implemented — all BP tasks, integration wiring, E2E tests, and feature flow verification.
- **Gate 7 (Integration verified)**: New quality gate in `/module-complete` checks that all integration points involving the module are verified WIRED via `/integration-logic`.
- **Integration gap detection in `/trace-check`**: Parses Engineering Spec's Module Integration Matrix and warns if any integration pair lacks a corresponding INTEGRATION task in the Blueprint. Warnings only (backward compatible).
- **Integration Coverage section in Work Ledger**: Shows each Integration Matrix pair and whether it's covered by an INTEGRATION task.

### Changed
- **TEMPLATE_Blueprint.md**: Major restructure — vertical build principles, prescribed wave structure (Wave 0 / Feature Threads / Final Wave), task card examples for all 4 types, strengthened integration checkpoints, expanded quality gates checklist.
- **TEMPLATE_Work_Order.md**: Added Task Type and Blueprint fields to frontmatter, integration checklist items to validation and commit sections.
- **TEMPLATE_Engineering_Spec.md**: Added guidance note to Module Integration Matrix linking rows to Blueprint INTEGRATION tasks.
- **quality-gates.md**: Added Gate 7 (integration verified), updated How to Invoke to reference Gates 1-7.
- **module-complete/SKILL.md**: Added Gate 7 (integration), renumbered WO status gate to Gate 8, updated description and verdict references.
- **integration-logic/SKILL.md**: Added "When to Use" section clarifying when the skill is required.
- **execution-protocol.md**: Added Wave Completion Gate section, integration evidence step (8b), INTEGRATION commit message format, updated quality gate count to 7.
- **validate_traceability.py**: BP task parsing now extracts Task Type, Integrates, and Module fields. Added `parse_integration_matrix()` and `check_integration_coverage()` functions.
- **TEMPLATE_MANIFEST.json**: Registered wave-complete and feature-complete skills, bumped version to 2.4.0.

### Migration Notes
- **From v2.3.x**: Run `/template-sync --apply` to get new files and updated templates. Existing Blueprint task cards without a `Task Type` field default to IMPLEMENTATION — no migration required for existing projects.
- **New projects**: Use the updated TEMPLATE_Blueprint.md with Wave 0 (Walking Skeleton) as the first wave. Define INTEGRATION tasks for every entry in the Module Integration Matrix.

---

## [2.3.4] - 2026-03-08

### Added
- **validate_traceability.py — Gap Tracker (GT) support**: Work Orders with `**Blueprint:** GT` in their body are recognized as Gap Tracker WOs. These skip BP orphan validation, display "Gap Tracker (no BP parent)" in the Work Ledger, and are excluded from Blueprint progress stats. Fixes false ORPHAN errors on WOs that intentionally don't map to a Blueprint task.

---

## [2.3.3] - 2026-03-06

### Fixed
- **commit-gate.sh — .env false positive**: `.env.*.example` template files (placeholder values, no secrets) are no longer blocked. Added `grep -v '\.example$'` exclusion to the `.env` file check.

### Changed
- **validate_traceability.py — Orphan ES/UX severity**: Orphaned ES and UX modules (referencing a non-existent PVD parent) are now warnings instead of errors. Infrastructure modules (e.g., ES-0.x) commonly don't map 1:1 to a PVD feature. Orphaned BP and WO modules remain errors (those break downstream chains).

---

## [2.3.2] - 2026-03-04

### Fixed
- **validate_traceability.py — Status regex**: Now matches both `**Status** | DONE` (table format) and `**Status:** DONE` (colon format). Previously only matched table format, causing WOs with colon-style frontmatter to show as UNKNOWN.
- **validate_traceability.py — WO header regex**: Now matches both `# Work Order: WO-N.M.T-X` and `# WO-N.M.T-X: Title` header formats. Previously only matched the long-form header, causing short-form WOs to be invisible to the validator.

---

## [2.3.1] - 2026-03-04

### Added
- **CHANGELOG.md**: Version history and migration notes for all template releases.
- **Upgrade pointer in sync report**: `template_sync.py` now shows "See CHANGELOG.md" when upgrading across versions.

---

## [2.3.0] - 2026-03-03

### Added
- **settings.json smart merge**: Hook registrations are merged into project settings.json without touching the permissions block. Hook identity = command string; merge is additive only.
- **`claude_md_version` marker**: CLAUDE.md now tracks its structure version independently via `<!-- claude_md_version: X.Y.Z -->` in the first 10 lines.
- **/template-migrate skill**: Guided, human-in-the-loop migration for projects with outdated or missing CLAUDE.md structure.
- **`managed_scaffolding` file category**: Project-owned files with template-managed sections (settings.json hooks block).
- **`hook_registrations` in TEMPLATE_MANIFEST.json**: Single source of truth for template hook wiring.

### Changed
- **execution-protocol.md**: Added commit-after-WO requirement (each completed WO = one commit with WO ID in message).
- **TEMPLATE_Work_Order.md**: Added commit instructions to the WO template.
- **TEMPLATE_MANIFEST.json**: Now includes `claude_md_structure_version`, `hook_registrations`, and `managed_scaffolding` category.
- **template_sync.py**: Full upgrade with managed_scaffolding support, CLAUDE.md version detection, and settings.json hook merging (~210 new lines).

### Fixed
- **commit-gate.sh**: Secrets scan false positive caused by grep matching its own pattern variable.
- **.gitignore**: Removed workshop-specific rules that incorrectly ignored `Sessions/`, `Research/`, and `_Archive/` in template projects.
- **Skill frontmatter**: Corrected `user_invocable` to `user-invokable` across 5 skill files. Fixed `argument-hint` bracket syntax to plain string.
- **Missing directories**: Added `Guides/`, `Quality/`, `Investor/`, `Patents/`, `Processes/` with `.gitkeep` files.

### Migration Notes
- **From v2.2.0**: Run `/template-sync --apply` to get new files. Then run `/template-migrate` to add the `claude_md_version` marker to your CLAUDE.md.
- **From pre-v2.2.0**: Run `/template-migrate` first (it handles both CLAUDE.md structure and infrastructure sync).

---

## [2.2.0] - 2026-03-03

### Added
- **Governance heartbeat system**: 4 automated enforcement checkpoints (code-gate, commit-gate, dep-gate, session heartbeat).
- **10 hooks**: session-start, session-resume, session-compact, spec-gate, commit-gate, dep-gate, block-dangerous, protect-frozen-files, template-guard, parse_hook_input.py.
- **validate_traceability.py**: Traceability chain validator with Work Ledger generation.
- **template_sync.py**: Sync engine with dry-run/apply modes and backup support.
- **.template_version**: Version tracking file for projects.
- **TEMPLATE_MANIFEST.json**: File ownership manifest with infrastructure, template, scaffolding, and generated categories.
- **3 new skills**: governance-health, template-sync, webapp-testing (total: 16 skills).

### Migration Notes
- First version published to EPL-Project-Template. Projects created from earlier copies should start fresh or use `/template-migrate`.

---

## [2.0.0] - 2026-03-01

### Added
- **Spec-Driven Development framework**: 9 document templates (PVD, Product Brief, PRD, Engineering Spec, UX Spec, Blueprint, Testing Plans, Work Order, Decision Record).
- **Traceability ID system**: PVD-N -> ES-N.M -> BP-N.M.T -> TP-N.M.T -> WO-N.M.T-X.
- **13 skills**: spec-lookup, code-review, alignment-check, dep-check, security-review, integration-logic, pre-commit, module-complete, frontend-design, trace-check, skill-creator, init-doc, session template.
- **spec-gate.sh**: Blocks code writes until 4 required specs are FROZEN.
- **6 governance rules**: change-control, execution-protocol, naming-conventions, problem-solving, quality-gates, spec-readiness.

### Migration Notes
- Major restructuring from v1.0. Fresh project setup recommended.

---

## [1.0.0] - 2026-02-28

### Added
- Initial project template with folder structure.
- Standard directory layout: Specs/, Code/, Testing/, Sessions/, Research/, Notes/, WorkOrders/.
- CLAUDE.md project constitution template.
- README.md with Gold Rush Doctrine and project conventions.
