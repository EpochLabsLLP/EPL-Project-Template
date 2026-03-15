# EPL Governance System v2.3.1 — Technical Brief for Coding Agents

**Audience:** AI coding agents working on projects governed by this system.
**Purpose:** Understand every enforcement mechanism, its logic, and how to work within it.

---

## Architecture Overview

The governance system consists of **10 hooks**, **6 rules**, and **16 skills** that enforce Spec-Driven Development (SDD) at the tooling level. Hooks intercept Claude Code tool calls (Bash, Edit, Write) and either allow (exit 0) or block (exit 2) based on project state. Rules are loaded into your context automatically and define behavioral requirements. Skills are invokable workflows (`/skill-name`).

All hooks live in `.claude/hooks/` and are registered in `.claude/settings.json`. All rules live in `.claude/rules/`. All skills live in `.claude/skills/{name}/SKILL.md`. The file `.claude/hooks/parse_hook_input.py` is shared infrastructure that extracts fields from the JSON stdin that Claude Code sends to hooks.

**Key principle: hooks are hard enforcement, rules are soft governance.** If a hook blocks you, there is no workaround — fix the underlying issue. Rules rely on your compliance.

---

## Hook-by-Hook Breakdown

### 1. spec-gate.sh (PreToolUse → Edit|Write)
**Purpose:** Blocks code writes until specs are frozen and a Work Order is active.

**Trigger:** Every Edit or Write call.

**Logic:**
1. Parse `tool_input.file_path` from JSON stdin.
2. Check if the target path contains a code directory: `Code/`, `code/`, `src/`, `lib/`, `app/`, `packages/`. If not → **ALLOW** (exit 0). Writing to Specs/, Testing/, etc. is always allowed.
3. Check for frozen specs. Scans `$PROJECT_DIR/Specs/` for files matching patterns (e.g., `*PVD*`, `*Engineering_Spec*`). For each, reads first 15 lines looking for the word "FROZEN". Skips files named `TEMPLATE_*`.
   - **Path A:** A FROZEN PVD satisfies the product spec requirement.
   - **Path B:** Both a FROZEN Product Brief AND a FROZEN PRD together satisfy it.
   - Additionally required: FROZEN Engineering Spec, FROZEN Blueprint, FROZEN Testing Plans (from `Testing/`).
4. Check for active Work Order. Scans `$PROJECT_DIR/WorkOrders/*.md`, skipping `TEMPLATE_*` and `_Archive*`. Reads first 20 lines of each looking for `**Status**.*IN-PROGRESS` or `Status.*IN-PROGRESS`.
5. If any spec is missing/unfrozen OR no active WO → **BLOCK** (exit 2). Lists exactly what's missing.

**What this means for you:** You cannot write to code directories until: (a) all 4 spec categories are FROZEN, and (b) a Work Order has `**Status:** IN-PROGRESS` in its header. Create specs with `/init-doc`, set them to FROZEN when approved. Create Work Orders with `/init-doc wo WO-N.M.T-X`.

### 2. commit-gate.sh (PreToolUse → Bash)
**Purpose:** Blocks `git commit` when traceability is broken or secrets are in staged changes.

**Trigger:** Every Bash call. First check: does the command match `git\s+commit`? If not → **ALLOW**.

**Logic (for git commits):**
1. **Traceability check:** Runs `validate_traceability.py $PROJECT_DIR --quick`. Exit codes: 0=clean, 1=broken chains (BLOCK), 2=script crash (warn but ALLOW — fail-open on crashes).
2. **Secrets scan:** Gets `git diff --cached` and searches for patterns:
   - API keys: `sk-[a-zA-Z0-9]{20,}`, `pk_live_`, `pk_test_`
   - Password/token assignments: `password\s*[=:]\s*["']...["']`
   - Bearer tokens, private key headers
   - Self-referential false positive excluded: `grep -v 'SECRET_PATTERNS='`
3. **Env file check:** Checks `git diff --cached --name-only` for `.env` files.
4. If traceability broken OR secrets found OR .env staged → **BLOCK** (exit 2).
5. On success: returns a `systemMessage` JSON advising to run `/code-review`.

**Fail-open behavior:** If `validate_traceability.py` is missing or crashes (exit 2), the commit is allowed with a warning. This prevents a broken tool from halting all work. But traceability errors (exit 1) are hard blocks.

### 3. dep-gate.sh (PreToolUse → Bash)
**Purpose:** Blocks package installations until `/dep-check` has been run.

**Trigger:** Every Bash call.

**Logic:**
1. Parse command from JSON stdin.
2. **Safe patterns (ALLOW immediately):**
   - `npm install` or `npm ci` with no package argument (installs from lockfile)
   - `yarn install` or bare `yarn` (lockfile install)
   - `pnpm install` with no package argument
   - `pip install -r requirements.txt` (requirements file)
   - `pip install -e .` or `pip install .` (current project)
3. **Block patterns:** Detects `(npm|yarn|pnpm) (install|add|i) [package]`, `pip install [package]`, `cargo add [package]`, `go get [package]`. Extracts the package name and tells you to run `/dep-check $PACKAGE` first.
4. Any command that doesn't match install patterns → **ALLOW**.

**What this means for you:** Before adding any new dependency, run `/dep-check <package>` first. It checks license (no GPL), security advisories, maintenance status, and compatibility. Only after `/dep-check` approves should you install.

### 4. protect-frozen-files.sh (PreToolUse → Edit|Write)
**Purpose:** Two responsibilities: (a) protect frozen spec files from modification, (b) protect governance infrastructure from modification.

**Trigger:** Every Edit or Write call.

**Logic — Governance protection (Part 1):**
1. Normalizes the file path (backslash → forward slash).
2. Checks if the path contains any governance pattern: `.claude/hooks/`, `.claude/rules/`, `.claude/settings.json`, `parse_hook_input.py`, `validate_traceability.py`, `TEMPLATE_MANIFEST.json`.
3. If matched → **DENY** via `permissionDecision: "deny"` JSON output. Message: "GOVERNANCE PROTECTION: template infrastructure. Do not modify directly."
4. Bypass: `TEMPLATE_BUILD_MODE=1` environment variable disables this (used during template construction only).

**Logic — Frozen file protection (Part 2):**
1. Only fires for paths matching `(Specs|Testing|WorkOrders)/`.
2. Calls `parse_hook_input.py --check-frozen <file_path>`. This reads the first 15 lines looking for FROZEN markers in 4 patterns:
   - `<!-- STATUS: FROZEN -->` (HTML comment)
   - `**Status:** FROZEN` or `**Status**: FROZEN` (bold markdown)
   - `Status: FROZEN` (plain text at line start)
   - `| Status | FROZEN |` (table format)
3. Skips `TEMPLATE_*` and `SESSION_TEMPLATE*` files (they contain instructional text about FROZEN, not actual status).
4. If frozen → **DENY**. Message: "FROZEN FILE: Must not be modified directly. Escalate to Nathan for change control."

### 5. template-guard.sh (PreToolUse → Write)
**Purpose:** Blocks creation of new spec documents that weren't derived from templates.

**Trigger:** Write calls only (not Edit — only new file creation matters).

**Logic:**
1. Captures full JSON stdin (both file_path and content).
2. If file already exists → **ALLOW** (editing existing files is fine).
3. Checks if path is in a governed directory: `Specs/`, `Testing/`, `WorkOrders/`.
4. Checks if filename matches a governed pattern: PVD, PRD, Product_Brief, Engineering_Spec, UX_Spec, Blueprint, Testing_Plan, Work_Order, Decision_Record, gap_tracker, Work_Ledger.
5. Skips `TEMPLATE_*` files.
6. Checks content for `<!-- TEMPLATE_SOURCE:` marker (provenance from `/init-doc`).
7. Escape hatch: `<!-- TEMPLATE_OVERRIDE: reason -->` in content bypasses the guard.
8. If new governed file without provenance → **DENY**. Directs you to use `/init-doc`.

**What this means for you:** Always use `/init-doc <type> [abbreviation]` to create new spec documents. Types: `pvd`, `prd`, `brief`, `es`, `ux`, `bp`, `tp`, `wo`, `dr`. This ensures consistent structure and embeds the provenance marker.

### 6. block-dangerous.sh (PreToolUse → Bash)
**Purpose:** Blocks destructive commands.

**Blocked patterns:**
- `git push --force`, `git push -f`, `git reset --hard`, `git clean -f`, `git branch -D`
- `rm -rf /`, `rm -rf *`, `rm -rf .`, `del /s /q`
- `DROP TABLE`, `DROP DATABASE`, `DELETE FROM table;` (bare DELETE without WHERE)

Returns `permissionDecision: "deny"` — not exit 2. This uses Claude Code's native permission system to hard-deny.

### 7–9. Session Hooks (SessionStart → startup/resume/compact)

These three hooks fire at different session lifecycle events. They don't block — they inject context into your conversation.

**session-start.sh (startup):**
Full context load for fresh sessions. Runs `validate_traceability.py --quick` and regenerates the Work Ledger. Outputs: traceability status, full Work Ledger, Gap Tracker summary (Tier 0/1/2/3 counts + next task), last session summary (tail 20 lines), template awareness (nudges if no product spec exists).

**session-resume.sh (resume):**
Lighter reload for continued conversations. Runs traceability check. Shows: ledger status line, active Work Orders, progress section, next task from Gap Tracker.

**session-compact.sh (compact):**
Most critical hook. After context compaction, you've lost all in-progress nuance. This does a FULL reload: traceability check, entire Work Ledger, entire Gap Tracker, last session summary (tail 25 lines). Opens with: "Pre-compaction memory is UNRELIABLE. You MUST re-read any files you were working on before making edits."

**Scope guard:** All three hooks check for Tier 0 (Critical) items in the Gap Tracker. If any exist, they output: "SCOPE GUARD: Tier 0 defects open. Resolve ALL Tier 0 items before any other work."

---

## Rules (Loaded into Agent Context)

All 6 rules are loaded automatically (no path scope — always active).

### execution-protocol.md
The master workflow definition. Defines:
- **The Heartbeat** — table of 4 auto-enforced checkpoints (session start, code write, git commit, package install).
- **Work Order Lifecycle** — state machine: PENDING → IN-PROGRESS → VALIDATION → DONE (or FAILED → archive → retry).
- **Mandatory Agent Checkpoints** — 15 numbered steps: before (spec-lookup, verify WO, set IN-PROGRESS), during (problem-solving protocol, no stubs, dep-check), after (code-review, module-complete, update WO, trace-check).
- **Commit-per-WO rule** — Each completed WO = one commit. Commit message must contain WO ID. Format: `WO-N.M.T-X: <description>`. Stage only WO-related files.

### change-control.md
Governs scope changes and spec revisions:
- **Scope Change Protocol** — STOP, present to Nathan, wait for approval, record in Decision Record.
- **Spec Revision Protocol** — Frozen specs are immutable. New version = new file (`{Abbrev}_{Spec}_v{N+1}.md`), archive old, update downstream.
- **WO Failure Protocol** — Archive failed WO, create next attempt (WO-N.M.T-A → WO-N.M.T-B), document failure reason.
- **Escalation triggers** — Frozen spec errors, uncovered work, two prior WO failures, security concerns, dependency changes.

### quality-gates.md
Six gates that must ALL pass before marking any module complete:
1. All interface contract methods implemented with real logic (no stubs)
2. Unit tests cover all public methods
3. No TODO/FIXME comments remain
4. No GPL dependencies (Apache 2.0, MIT, BSD only)
5. Compiles/builds without warnings
6. Performance meets Engineering Spec targets

### naming-conventions.md
File naming patterns for specs, Work Orders, sessions, and code files.

### problem-solving.md
Tiered debugging protocol: Tier 1 (read/understand) → Tier 2 (targeted fix) → Tier 3 (broader investigation) → Tier 4 (escalate to Nathan). Max 3 actions per tier before escalating.

### spec-readiness.md
Defines when specs are ready to freeze and what each spec type must contain.

---

## Traceability System

The traceability ID system creates a chain from requirements to code:

```
PVD-N → ES-N.M → BP-N.M.T → TP-N.M.T → WO-N.M.T-X
```

- **PVD-N**: Product Vision Document, feature N
- **ES-N.M**: Engineering Spec, feature N, module M
- **BP-N.M.T**: Blueprint, feature N, module M, task T
- **TP-N.M.T**: Testing Plans (mirrors Blueprint)
- **WO-N.M.T-X**: Work Order, attempt X (A, B, C...)

`validate_traceability.py` parses all specs and Work Orders, follows parent references, and reports:
- **Exit 0:** All chains valid, generates Work Ledger
- **Exit 1:** Broken chains (orphan IDs, missing parents) — commit-gate blocks
- **Exit 2:** Script crash — fail-open (commit allowed with warning)

The Work Ledger (`Specs/Work_Ledger.md`) is auto-generated and shows project status, active WOs, and traceability health.

---

## File Ownership Model

Every file in the project falls into one of 5 categories defined in `TEMPLATE_MANIFEST.json`:

| Category | Sync Behavior | You Can Modify? |
|----------|--------------|-----------------|
| **infrastructure** | Always overwritten on sync | **NO** — protect-frozen-files.sh blocks this |
| **template** | Always overwritten on sync | **NO** — these are reference templates |
| **scaffolding** | Created once, never overwritten | **YES** — CLAUDE.md and README.md are yours |
| **managed_scaffolding** | Hooks block merged, permissions untouched | **NO** for hooks block; permissions are yours |
| **generated** | Skipped by sync | Generated by tools, not manually edited |

**50 managed files total** across all categories. The sync engine (`template_sync.py`) handles upgrades.

---

## Upgrade System (v2.3.x)

### template_sync.py
Compares template repo against project. Run modes:
- `python template_sync.py <template_dir> <project_dir>` — dry-run report
- `python template_sync.py <template_dir> <project_dir> --apply` — apply changes with backup

Reports: WILL CREATE, WILL UPDATE, DRIFTED, SKIPPED (project-owned), UP TO DATE. Shows "UPGRADE: X.Y.Z → A.B.C — See CHANGELOG.md" when versions differ.

### settings.json Smart Merge
Hook registrations in `TEMPLATE_MANIFEST.json` define the template's hooks. The merge algorithm:
1. For each event type (SessionStart, PreToolUse), find matcher blocks
2. Match by matcher string (e.g., "Bash", "Edit|Write")
3. Within matched blocks, match hooks by command string identity
4. **Additive only:** adds missing hooks, updates timeouts, never removes project hooks
5. Never touches the `permissions` block

### CLAUDE.md Version Tracking
Template CLAUDE.md contains `<!-- claude_md_version: X.Y.Z -->` in the first 10 lines. `template_sync.py` compares this against the manifest's `claude_md_structure_version`. If missing or outdated, the sync report warns but does NOT auto-modify CLAUDE.md. Use `/template-migrate` for guided migration.

### CHANGELOG.md
Version history from v1.0.0 through current. Categories: Added, Changed, Fixed, Migration Notes. Infrastructure file — auto-overwritten on sync so projects always have the latest.

---

## Skills Reference (16 total)

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/spec-lookup <module>` | Load specs for a module | Before implementation |
| `/init-doc <type> [abbrev]` | Create spec from template | Starting any new document |
| `/code-review <module>` | Post-implementation review | After implementing, before module-complete |
| `/module-complete <module>` | Run all 6 quality gates | Before marking WO as DONE |
| `/trace-check` | Validate traceability chains | After spec/WO changes, before commit |
| `/dep-check <package>` | Vet a dependency | Before any package install |
| `/pre-commit` | Full commit hygiene | Before git commit |
| `/alignment-check` | Verify code matches spec | When checking spec-code drift |
| `/integration-logic` | Verify cross-module wiring | When connecting modules |
| `/security-review` | Security audit | Before shipping |
| `/governance-health` | Validate governance integrity | After sync, diagnosing hook issues |
| `/template-sync [--apply]` | Sync template updates | After template repo changes |
| `/template-migrate` | Guided CLAUDE.md migration | Legacy projects, major upgrades |
| `/skill-creator` | Create new project skill | Adding custom workflows |
| `/frontend-design` | High-fidelity UI design | Building web interfaces |
| `/webapp-testing` | Browser automation testing | Verifying frontend behavior |

---

## Working Within the System — Quick Reference

**To start coding:**
1. Ensure specs exist and are FROZEN (PVD or Brief+PRD, Engineering Spec, Blueprint, Testing Plans)
2. Create a Work Order: `/init-doc wo WO-N.M.T-X`
3. Set WO status to `**Status:** IN-PROGRESS`
4. Now code writes to `Code/`, `src/`, etc. are allowed

**To commit:**
1. Traceability chains must be clean (`/trace-check`)
2. No secrets in staged diff
3. No .env files staged
4. Commit message includes WO ID: `WO-N.M.T-X: description`

**To add a dependency:**
1. Run `/dep-check <package>` first
2. Only install after it passes

**To complete a module:**
1. `/code-review <module>` — pass quality review
2. `/module-complete <module>` — pass all 6 gates
3. Set WO to DONE
4. Commit with WO ID in message

**To modify a frozen spec:**
1. STOP — do not edit it directly (hook will block you)
2. Escalate to Nathan for change control
3. Follow Spec Revision Protocol (new version file, archive old)

---

*Template version: v2.3.1 | 10 hooks, 6 rules, 16 skills, 50 managed files*
*Check `.template_version` for a project's current governance version.*
