<!-- AGENT INSTRUCTION: This rule defines the mandatory execution workflow.
     It governs how Work Orders drive implementation, when checkpoints run,
     and what the agent must do before, during, and after coding.

     All enforcement mechanisms listed here are backed by hooks.
     "Enforced" means a hook will BLOCK the action if the requirement is not met.
     "Required" means the rule mandates it and the agent must comply.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# Execution Protocol — Mandatory Workflow

*Intent: Ensures every line of code traces to a spec, every commit is validated, and every module meets quality gates before being marked complete. This is the heartbeat of the governance system.*

## The Heartbeat

These checkpoints run automatically. You do not invoke them — they invoke themselves.

| Checkpoint | When | What Runs | Enforcement |
|-----------|------|-----------|-------------|
| **Session Start** | Every new/resumed session | `validate_traceability.py` auto-refreshes Work Ledger | Informational (displays fresh status) |
| **Code Write** | Every Edit/Write to code directories | `spec-gate.sh` checks frozen specs + active WO | **BLOCKS** if specs missing or no active WO |
| **Git Commit** | Every `git commit` | `commit-gate.sh` validates traceability + scans for secrets | **BLOCKS** on broken chains or secrets |
| **Package Install** | Every `npm/pip/cargo/go install` | `dep-gate.sh` checks for /dep-check | **BLOCKS** until dependency is vetted |

## Work Order Lifecycle

Work Orders are the execution unit of the SDD framework. Every implementation task flows through a Work Order.

### State Machine

```
PENDING ──→ IN-PROGRESS ──→ VALIDATION ──→ DONE
                │
                └──→ FAILED ──→ (archive, create next attempt)
```

### State Definitions

| State | Meaning | What's Allowed |
|-------|---------|---------------|
| **PENDING** | WO created, not yet started | Spec review, planning |
| **IN-PROGRESS** | Active implementation | Code writes (code-gate checks for this) |
| **VALIDATION** | Implementation complete, under review | /code-review, /module-complete, testing |
| **DONE** | All quality gates passed | Archive or reference only |
| **FAILED** | Implementation failed validation | Archive, create next attempt (WO-N.M.T-B) |

### Enforcement

- **Code writes require IN-PROGRESS:** The code-gate hook checks for at least one WO with status IN-PROGRESS before allowing writes to code directories. Create a WO with `/init-doc wo WO-N.M.T-X` and set its status to IN-PROGRESS before coding.
- **DONE requires quality gates:** Before setting a WO to DONE, run `/code-review` and `/module-complete` for the module. All 6 quality gates must pass.
- **FAILED triggers archive protocol:** Failed WOs must be archived to `WorkOrders/_Archive/` before creating the next attempt. See change-control.md for the WO Failure Protocol.

## Mandatory Checkpoints (Agent Responsibilities)

These are not auto-enforced by hooks but are REQUIRED by project governance. Skipping them is a governance violation.

### Before Implementation

1. **Run `/spec-lookup <module>`** — Load the spec context for the module you're implementing.
2. **Verify Work Order exists** — If no WO covers this work, create one with `/init-doc wo`.
3. **Set WO status to IN-PROGRESS** — The code-gate will block code writes otherwise.

### During Implementation

4. **Follow the Problem-Solving Protocol** — Tiers 1→4, max 3 actions per tier (see problem-solving.md).
5. **No stubs, no TODOs** — Every method must contain real logic. Defer incomplete work to the Gap Tracker.
6. **Run `/dep-check <pkg>`** before adding any dependency — The dep-gate will block installs otherwise.

### After Implementation

7. **Run `/code-review <module>`** — Post-implementation quality review. Required before module-complete.
8. **Run `/module-complete <module>`** — Verify all 6 quality gates pass. Required before marking WO as DONE.
9. **Update WO status** — Set to VALIDATION (if awaiting review) or DONE (if all gates pass).
10. **Run `/trace-check`** — Verify traceability chains are intact after changes. (Also runs automatically at session start and before commits.)

### Before Commit

11. **Commit-gate runs automatically** — Validates traceability and scans for secrets.
12. **Run `/pre-commit`** for full hygiene — The commit-gate covers traceability and secrets; `/pre-commit` also checks TODOs, debug statements, file hygiene, build, and tests.

## Traceability is Continuous

- The Work Ledger auto-refreshes at every session start, resume, and compaction recovery.
- Broken traceability chains (orphan IDs, missing parents) are errors that block commits.
- The traceability chain for every piece of work must be traceable: `WO → BP → ES → PVD`.
- If `/trace-check` reports errors, fix them before continuing implementation.
