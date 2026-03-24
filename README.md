# Epoch Labs — Project Template

**Version:** 2.0
**Last Updated:** 2026-03-01

---

## Purpose

This is the standard project template for all Epoch Labs projects. It provides a complete development infrastructure built on **Spec-Driven Development (SDD)** — Epoch Labs' methodology for moving from product concept to shipped software using AI agents as primary implementers.

Copy this entire folder to start a new project with document templates, traceability automation, quality gates, and anti-drift hooks pre-configured.

## Quick Start

1. **Copy** this folder to `C:\Claude Folder\{YourProjectName}\`
2. **Customize** `CLAUDE.md` — fill in all `{placeholder}` values
3. **Create _shared junction** (connects to cross-project shared specs):
   ```cmd
   mklink /J "C:\Claude Folder\{YourProjectName}\_shared" "C:\Claude Folder\_SharedCore"
   ```
4. **Initialize git** — `git init`, create `main` and `dev` branches
5. **Start speccing** — copy templates from `Specs/TEMPLATE_*.md` and begin with the PVD

---

## What's Included

### Document Templates (SDD Stack)

Nine templates implementing the full Spec-Driven Development document stack:

| # | Template | Location | Purpose | Status Type |
|---|----------|----------|---------|-------------|
| 1a | `TEMPLATE_PVD.md` | Specs/ | Product Vision Document — what we build, why it matters | FROZEN |
| 1b | `TEMPLATE_Product_Brief.md` | Specs/ | Lightweight "should we spec this?" gate (autonomous path) | FROZEN |
| 1c | `TEMPLATE_PRD.md` | Specs/ | Detailed requirements (autonomous path) | FROZEN |
| 2 | `TEMPLATE_Engineering_Spec.md` | Specs/ | Architecture, modules, interfaces, performance budgets | FROZEN |
| 3 | `TEMPLATE_UX_Spec.md` | Specs/ | Screens, flows, design tokens (UI projects only) | FROZEN |
| 4 | `TEMPLATE_Blueprint.md` | Specs/ | Agent-executable build plan with task cards | FROZEN |
| 5 | `TEMPLATE_Testing_Plans.md` | Testing/ | Per-module test cases, coverage targets | FROZEN |
| 6 | `TEMPLATE_Work_Order.md` | Specs/ | Scoped build+test assignment carved from Blueprint | ACTIVE |
| 7 | `TEMPLATE_Decision_Record.md` | Specs/ | Living log of significant decisions | LIVING |

**Two authoring paths:**
- **Path A (Collaborative):** PVD template — Nathan and Claude iterate together
- **Path B (Autonomous):** Product Brief → PRD — for orchestration engine use

### Traceability System

Hierarchical ID system linking every piece of work back to the product requirement that justifies it:

```
PVD-3       →  Feature #3 in the PVD
  ES-3.2    →  Module #2 implementing PVD Feature #3
    BP-3.2.4  →  Task #4 under ES Module 3.2
      TP-3.2.4  →  Tests for Blueprint task 3.2.4
        WO-3.2.4-A  →  Work Order A for task 3.2.4
```

**`/trace-check`** — Skill that validates all chains and generates the Work Ledger (`Specs/Work_Ledger.md`), a persistent project status showing spec readiness, chain health, Work Order status, and project progress.

### Automated Enforcement

| Hook/Rule | What It Does |
|-----------|-------------|
| **spec-gate.sh** | Blocks code writes (`Code/`, `src/`) until 4 required specs are FROZEN |
| **protect-frozen-files.sh** | Prevents modification of frozen spec files |
| **block-dangerous.sh** | Blocks destructive bash commands (`rm -rf`, `--force`, etc.) |
| **session-start.sh** | Injects Work Ledger + Gap Tracker at session start |
| **session-resume.sh** | Re-anchors to active Work Orders on resume |
| **session-compact.sh** | Full context recovery after compaction |
| **pre-commit-reminder.sh** | Reminds to run `/pre-commit` and `/trace-check` |
| **spec-readiness.md** | Guides spec creation sequence and traceability IDs |
| **change-control.md** | Scope change, spec revision, and WO failure protocols |
| **quality-gates.md** | 6 gates that must pass before marking any module complete |
| **problem-solving.md** | 4-tier escalation protocol (max 3 actions per tier) |
| **naming-conventions.md** | File naming standards for automation compatibility |

### Claude Code Skills (13)

| Skill | Invocation | Purpose |
|-------|-----------|---------|
| spec-lookup | `/spec-lookup <module>` | Load specs before working on a module |
| code-review | `/code-review <module>` | Post-implementation quality review |
| alignment-check | `/alignment-check <module>` | Verify code matches spec with evidence |
| dep-check | `/dep-check <dependency>` | Check license, security, maintenance |
| security-review | `/security-review <module>` | OWASP-style security audit |
| integration-logic | `/integration-logic <mod-a> <mod-b>` | Verify cross-module wiring |
| pre-commit | `/pre-commit` | Secrets scan, file hygiene, build check |
| module-complete | `/module-complete <module>` | Run all 6 quality gates |
| frontend-design | `/frontend-design` | Production-grade frontend UI design |
| webapp-testing | `/webapp-testing` | Playwright-based web app testing |
| trace-check | `/trace-check` | Validate traceability chains, generate Work Ledger |
| skill-creator | `/skill-creator <name>` | Create a new project-specific skill |

---

## Folder Structure

```
{ProjectName}/
  CLAUDE.md                  — Project constitution (auto-loads, is LAW)
  Specs/                     — Specifications, templates, Work Ledger
    TEMPLATE_*.md            — Document templates (copy, don't edit)
    Work_Ledger.md           — Auto-generated project status
    gap_tracker.md           — Tiered work items
  Research/                  — Research docs, analysis (git-ignored)
  Code/                      — Source code (gated by spec-gate hook)
  Testing/                   — Test plans, QA documentation
    TEMPLATE_Testing_Plans.md
  WorkOrders/                — Active Work Orders
    _Archive/                — Completed/failed Work Orders
  Quality/                   — Feature-level quality assessments
  Patents/                   — Patent briefs, IP documents
  Processes/                 — Project-specific process docs
  Sessions/                  — Session summaries (git-ignored)
  Notes/                     — General notes
  Investor/                  — Investor materials
  _shared/                   — Junction to _SharedCore
  _Archive/                  — Archived/superseded files
  .claude/
    hooks/                   — Automated enforcement hooks
    rules/                   — Auto-loading governance rules
    skills/                  — Custom Claude Code skills
    settings.json            — Hook registrations
```

---

## Document Lifecycle

### Spec Creation Sequence
1. **PVD** (or Product Brief + PRD) → Assign PVD-N identifiers → FREEZE
2. **Engineering Spec** → Assign ES-N.M identifiers → FREEZE
3. **UX Spec** (if UI project) → Assign UX-N.M identifiers → FREEZE
4. **Blueprint** → Assign BP-N.M.T identifiers → FREEZE
5. **Testing Plans** → Assign TP-N.M.T identifiers → FREEZE
6. **Gap Tracker** → Initialize tier structure
7. **Decision Record** → Log spec-phase decisions
8. **Work Orders** → Carve from Blueprint, begin execution

### Work Order Lifecycle
```
PENDING → IN-PROGRESS → VALIDATION → DONE (archive to WorkOrders/_Archive/)
                                    → FAILED (archive, create new WO with incremented suffix)
```

### Document Status Types
- **FROZEN** — Finalized, immutable. Changes require formal revision + Nathan's approval.
- **ACTIVE** — Operational artifacts with lifecycle state (Work Orders).
- **LIVING** — Continuously appended, never frozen (Gap Tracker, Decision Record).
- **DRAFT** — Work in progress, suffix `_DRAFT` until finalized.

---

## Key Principles

### The Gold Rush Doctrine
- No stubs. No placeholder features. No "coming soon" UI.
- "What ships is finished, what isn't finished doesn't ship."
- Ship complete features, not complete products.

### Anti-Patterns (NEVER DO)
- No stubs or fake implementations
- No code before frozen specs
- No hardcoded API keys
- No HTTP (TLS everywhere)
- No GPL dependencies
- No TODO/FIXME in shipped code

### Safety Rules
- **NEVER delete files** — archive to `_Archive/`
- **NEVER overwrite** without asking
- **NEVER commit secrets**
- **Ask before** structural changes

---

## Cross-Project Resources

| Directory | Purpose |
|-----------|---------|
| `_SharedCore/` | Cross-project shared specs, schemas, security |
| `_Processes/` | Global skills and process library |
| `_TaskQueue/` | Task briefs for future sessions |
| `_IP_Pipeline/` | Patent brief queue |
| `Memory/` | Memory database and knowledge infrastructure |

---

## Git Strategy

- **main** — Production-ready releases only
- **dev** — Active development (default working branch)
- **feature branches** — For isolated work, merge to dev

---

*Epoch Labs, LLP — Building with the Gold Rush Doctrine*
