# Changelog

All notable changes to the EPL Project Template are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions use [Semantic Versioning](https://semver.org/).

Upgrade projects with `/template-sync --apply`. See Migration Notes for version-specific instructions.

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
