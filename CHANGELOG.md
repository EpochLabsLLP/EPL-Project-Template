# Changelog

All notable changes to the EPL Project Template are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions use [Semantic Versioning](https://semver.org/).

Upgrade projects with `/template-sync --apply`. See Migration Notes for version-specific instructions.

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
