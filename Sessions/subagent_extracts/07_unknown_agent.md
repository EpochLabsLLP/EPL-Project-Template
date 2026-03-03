# 07_unknown_agent (agent-acee81c62beed16f9.jsonl)

## Message 1

Perfect! Now let me create a comprehensive summary document with all the information I've gathered.

## Comprehensive Project Template Exploration Report

I've completed a thorough exploration of the Epoch Labs Project Template repository. Here's the complete inventory:

---

## FILE INVENTORY

### Root-Level Files
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\README.md** — Master documentation (v2.0, 2026-03-01)
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\CLAUDE.md** — Project constitution template with placeholders for project-specific customization
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.gitignore** — Standard gitignore for secrets, artifacts, and local builds
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.mcp.json** — MCP server configuration (Context7 as default)

---

## .CLAUDE DIRECTORY STRUCTURE

### .claude/settings.json
```
Hook registrations for SessionStart and PreToolUse events:
- SessionStart hooks:
  - startup → runs session-start.sh (injects Work Ledger + Gap Tracker)
  - resume → runs session-resume.sh (lightweight re-anchor)
  - compact → runs session-compact.sh (full context recovery post-compaction)
- PreToolUse hooks:
  - Bash → block-dangerous.sh + pre-commit-reminder.sh
  - Edit|Write → protect-frozen-files.sh + spec-gate.sh
```

### .claude/settings.local.json.example
Example permissions template for per-machine overrides (gitignored in actual use).

### .claude/hooks/ Directory

**session-start.sh**
- Fires on fresh session start
- Outputs Work Ledger + Gap Tracker summary
- Shows next task and tier summaries
- Anti-drift mechanism ensuring re-anchoring to project status

**session-resume.sh**
- Fires when resuming previous conversations
- Lighter than startup — assumes conversation context exists
- Re-anchors to Work Ledger status and active Work Orders

**session-compact.sh**
- MOST CRITICAL hook — fires after context compaction
- Re-injects FULL project context
- Warns that pre-compaction memory is unreliable
- Dumps complete Work Ledger + Gap Tracker

**spec-gate.sh**
- PreToolUse hook preventing code writes without frozen specs
- Enforces "no code before specs" principle
- Checks for: PVD OR (Product Brief + PRD), Engineering Spec, Blueprint, Testing Plans
- All must be FROZEN before Code/ writes allowed

**protect-frozen-files.sh**
- Prevents modification of frozen spec files
- Maintains a FROZEN_PATTERNS list (commented by default)
- Scales as project adds specs

**block-dangerous.sh**
- Blocks destructive bash commands:
  - Destructive git: `git push --force`, `git reset --hard`, `git clean -f`, `git branch -D`
  - Mass deletion: `rm -rf /`, `rm -rf *`, `del /s /q`
  - Database destruction: `DROP TABLE`, `DELETE FROM` with no WHERE clause

**pre-commit-reminder.sh**
- Advisory hook reminding to run `/pre-commit` before git commit
- Also reminds to run `/trace-check` if spec files modified

**parse_hook_input.py**
- Utility for all hooks to extract fields from JSON input
- Normalizes Windows backslashes to forward slashes

### .claude/rules/ Directory

**spec-readiness.md** — Guides spec creation sequence, traceability ID system, UX Spec conditional inclusion

**change-control.md** — Scope change protocol, spec revision protocol, Work Order failure handling, Decision Record usage

**quality-gates.md** — Definition of Done (6 gates): no stubs, test coverage, no TODOs, no GPL deps, clean build, performance targets

**problem-solving.md** — 4-tier escalation (max 3 actions per tier): Read & Trace → Internal Resources → External Resources → Escalate to Nathan

**naming-conventions.md** — File naming standards enabling automation (specs use `{Abbrev}_{Topic}_v{N}.md`, code follows language conventions)

### .claude/skills/ Directory

**12 Production Skills + Examples/Scripts:**

1. **spec-lookup** — Load primary and supporting specs before working on a module
2. **code-review** — Post-implementation quality review (correctness, error handling, security, testing)
3. **alignment-check** — Verify code matches spec using grep-based evidence gathering
4. **dep-check** — Check license, security, maintenance of dependencies
5. **security-review** — OWASP-style audit (secrets, input validation, injection prevention, auth, data protection, error handling)
6. **integration-logic** — Verify cross-module wiring and contracts
7. **pre-commit** — Secrets scan, prohibited content, file hygiene, build/test verification
8. **module-complete** — Run all 6 quality gates before marking module done
9. **frontend-design** — Production-grade UI design with bold aesthetic direction
10. **webapp-testing** — Playwright-based web testing with server lifecycle
11. **trace-check** — Validate traceability chains, generate Work Ledger
12. **skill-creator** — Create new project-specific skills following Agent Skills SDK

**trace-check Supporting Files:**
- **scripts/validate_traceability.py** — Python validation engine (parses IDs, validates chains, checks frozen status, generates Work Ledger)

**webapp-testing Supporting Files:**
- **examples/console_logging.py** — Example: capturing browser console messages
- **examples/element_discovery.py** — Example: finding and interacting with elements
- **examples/static_html_automation.py** — Example: automating static HTML pages
- **scripts/with_server.py** — Server lifecycle management for testing

---

## SPECS/ DIRECTORY (Document Templates)

**9 Spec Templates Implementing Full SDD Stack:**

1. **TEMPLATE_PVD.md** — Product Vision Document (collaborative path: what + why)
   - Sections: Executive Summary, Vision & Mission, Problem Statement, Target Users, Product Overview, Feature Specs
   - Assigns PVD-N identifiers (root of traceability chains)
   - Status: FROZEN before proceeding

2. **TEMPLATE_Product_Brief.md** — Lightweight go/no-go gate (autonomous path)
   - Sections: Problem Hypothesis, Target User Sketch, Market Opportunity, Value Proposition, Key Risks, Go/No-Go Decision
   - Gate before PRD investment

3. **TEMPLATE_PRD.md** — Detailed Requirements (autonomous path, follows Brief approval)
   - References Product Brief
   - Assigns PVD-N identifiers (same as PVD path)
   - Feature specs with user stories and acceptance criteria

4. **TEMPLATE_Engineering_Spec.md** — Technical architecture (how to build)
   - Sections: System Architecture, Technology Stack, Module Dependency Graph, Database Schema, Module Specifications
   - Assigns ES-N.M identifiers (trace to PVD-N)
   - Frozen interface contracts

5. **TEMPLATE_UX_Spec.md** — User experience (UI projects only)
   - Sections: Design Principles, Screen Inventory, Navigation Flows, Component Library
   - Assigns UX-N.M identifiers (trace to PVD-N)
   - Describes all user-facing interactions

6. **TEMPLATE_Blueprint.md** — Agent-executable build plan
   - Sections: Build Principles, Dependency Graph, Phase/Wave Schedule, Task Cards
   - Assigns BP-N.M.T identifiers (trace to ES-N.M)
   - Task cards with acceptance criteria and complexity estimates
   - FROZEN — never modified during development

7. **TEMPLATE_Decision_Record.md** — Living log of significant decisions
   - LIVING document (continuously appended, never frozen)
   - Format: DR-NNN entries with Context, Decision, Alternatives Considered, Consequences
   - Prevents re-litigation of settled questions

8. **TEMPLATE_Work_Order.md** — Scoped assignment (carved from Blueprint)
   - Bundles build tasks + tests + acceptance criteria
   - Assigns WO-N.M.T-X identifiers (trace to BP-N.M.T)
   - Lifecycle: PENDING → IN-PROGRESS → VALIDATION → DONE/FAILED
   - Failed WOs archived, new attempt suffix increments (-A → -B)

9. **gap_tracker.md** — Tiered work tracking (Tier 0-3: Critical → Functional → Quality → Enhancement)
   - Single source of truth for "what needs doing and in what order"
   - Mandatory scope guards (don't work Tier 1 while Tier 0 open, etc.)
   - SessionStart hooks read this automatically

10. **Work_Ledger.md** — Auto-generated by `/trace-check` skill
    - Persistent project status snapshot
    - Sections: Spec Readiness, Traceability Chain, Active Work Orders, Progress
    - CLEAN or list of warnings/errors

---

## TESTING/ DIRECTORY

**TEMPLATE_Testing_Plans.md** — Per-module test cases
- Sections: Testing Philosophy & Pyramid, Test Infrastructure & Tools, Per-Module Unit Test Specs, Integration Test Scenarios
- Assigns TP-N.M.T identifiers (mirror BP-N.M.T)
- Every Blueprint task MUST have corresponding TP entry

---

## SESSIONS/ DIRECTORY

**SESSION_TEMPLATE.md** — Reusable session summary template
- Sections: What Was Accomplished, Key Decisions Made, Files Created/Modified, Bug Fixes, Open Questions, Next Steps
- Provides continuity across sessions
- SessionStart hooks surface these on resume

---

## WORKORDERS/ DIRECTORY

- **_Archive/** — Completed/failed Work Orders storage

---

## OTHER DIRECTORIES

- **Code/** — Source code (gated by spec-gate hook)
- **Testing/** — Test plans, QA documentation
- **Quality/** — Feature-level quality assessments
- **Patents/** — Patent briefs, IP documents
- **Processes/** — Project-specific process docs
- **Research/** — Research docs (git-ignored)
- **Notes/** — General notes
- **Investor/** — Investor materials
- **Guides/** — Advanced patterns reference
- **_Archive/** — Archived/superseded files
- **_shared/** — Junction to `_SharedCore` (cross-project shared specs)

---

## TRACEABILITY SYSTEM EXPLAINED

**Hierarchical ID chains ensuring all work traces back to product justification:**

```
PVD-3              → Feature #3 (product vision)
  ES-3.2           → Module #2 implementing PVD-3
    UX-3.2         → Screen/flow for PVD-3
    BP-3.2.4       → Task #4 of ES-3.2
      TP-3.2.4     → Tests for BP-3.2.4 (mirror)
        WO-3.2.4-A → Work Order attempt A
```

**Validation chain:** `/trace-check` validates that:
- PVD features have corresponding ES modules
- ES modules have corresponding BP tasks
- BP tasks have corresponding TP test specs
- WO status tracks execution progress
- No orphan IDs or broken chains

---

## KEY PRINCIPLES & GOVERNANCE

### Gold Rush Doctrine (Immutable)
- No stubs or placeholders
- "What ships is finished, what isn't finished doesn't ship"
- Ship complete features, not complete products
- Quality bar must match or exceed best existing alternative

### Anti-Patterns (NEVER DO)
- No stubs or fake implementations
- No code before frozen specs
- No hardcoded API keys
- No HTTP (TLS everywhere)
- No GPL dependencies (Apache 2.0, MIT, BSD only)
- No TODO/FIXME in shipped code

### Safety Rules
- NEVER delete files (archive to `_Archive/` instead)
- NEVER overwrite without asking
- NEVER commit secrets
- Ask before structural changes

---

## GIT STRATEGY

- **main** — Production-ready releases only
- **dev** — Active development (default working branch)
- **feature branches** — Isolated work, merge to dev

---

## INITIALIZATION STEPS FOR NEW PROJECT

1. Copy entire template folder to `C:\Claude Folder\{YourProjectName}\`
2. Customize `CLAUDE.md` (replace all `{placeholders}`)
3. Create `_shared` junction: `mklink /J _shared C:\Claude Folder\_SharedCore`
4. Initialize git: `git init`, create `main` and `dev` branches
5. Start speccing: copy templates from `Specs/TEMPLATE_*.md`, begin with PVD

---

## ADVANCED PATTERNS (OPTIONAL)

Documented in **Guides/advanced_patterns.md**:

1. **Nested CLAUDE.md Assembly** — Project-wide rules + layer-specific rules for complex projects
2. **Structured Acceptance Criteria** — Verification methods for precise acceptance definitions
3. **Skills Discovery** — Installing additional Anthropic official skills and community skills

---

## CROSS-PROJECT RESOURCES

These live outside this template (in parent directories):

- **_SharedCore/** — Cross-project shared specs, schemas, security foundations
- **_Processes/** — Global skills and process library
- **_TaskQueue/** — Task briefs for future sessions
- **_IP_Pipeline/** — Patent brief queue
- **Memory/** — SQLite memory database (`claude_memory.db`) with `document_index`, `local_sessions`, `project_context` tables

---

## ABSOLUTE PATHS TO ALL KEY FILES

**Configuration & Documentation:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\README.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\CLAUDE.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.gitignore`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.mcp.json`

**Settings:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\settings.json`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\settings.local.json.example`

**Hooks (8 files):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\session-start.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\session-resume.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\session-compact.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\spec-gate.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\protect-frozen-files.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\block-dangerous.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\pre-commit-reminder.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\parse_hook_input.py`

**Rules (5 files):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\spec-readiness.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\change-control.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\quality-gates.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\problem-solving.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\naming-conventions.md`

**Skills (12 + supporting):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\spec-lookup\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\code-review\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\alignment-check\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\dep-check\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\security-review\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\integration-logic\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\pre-commit\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\module-complete\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\frontend-design\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\trace-check\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\skill-creator\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\trace-check\scripts\validate_traceability.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\examples\console_logging.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\examples\element_discovery.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\examples\static_html_automation.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\scripts\with_server.py`

**Spec Templates (9 files):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_PVD.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Product_Brief.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_PRD.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Engineering_Spec.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_UX_Spec.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Blueprint.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Decision_Record.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Work_Order.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\gap_tracker.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\Work_Ledger.md`

**Testing & Sessions:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Testing\TEMPLATE_Testing_Plans.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Sessions\SESSION_TEMPLATE.md`

**Guides:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Guides\advanced_patterns.md`

---

This is a complete, production-ready template for building projects using Spec-Driven Development (SDD) with AI agents as primary implementers. Every system has been architected to prevent drift, enforce quality gates, maintain traceability, and ensure that only complete, finished features ship.

