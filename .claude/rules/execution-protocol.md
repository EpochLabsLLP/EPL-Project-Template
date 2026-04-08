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
| **Deferred Audit** | Every new/resumed session | `scan_deferred.py` checks for orphaned deferred items | Informational (surfaces orphan count) |
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
- **DONE requires quality gates:** Before setting a WO to DONE, run `/code-review` and `/module-complete` for the module. All 7 quality gates must pass.
- **FAILED triggers archive protocol:** Failed WOs must be archived to `WorkOrders/_Archive/` before creating the next attempt. See change-control.md for the WO Failure Protocol.

## Mandatory Checkpoints (Agent Responsibilities)

These are not auto-enforced by hooks but are REQUIRED by project governance. Skipping them is a governance violation.

### Before Implementation

1. **Read the upstream PVD** (not just the ES/BP) — Understand the *intent* behind the requirements, not just the requirements themselves. Engineering Specs describe *what* to build; the PVD describes *why* and for *whom*. If you skip this, you will build structurally correct code that misses the point.
2. **Check for a Work Context Document** — If `WorkContexts/{BP-id}_context.md` exists (from `/prepare-work`), read it. It contains the pre-extracted spec chain for this task. If it doesn't exist, run `/spec-lookup <module>` to load context.
3. **Verify Work Order exists** — If no WO covers this work, create one with `/init-doc wo`.
4. **Set WO status to IN-PROGRESS** — The code-gate will block code writes otherwise.

### During Implementation

5. **Follow the Problem-Solving Protocol** — Tiers 1→4, max 3 actions per tier (see problem-solving.md).
6. **No stubs, no TODOs** — Every method must contain real logic. Defer incomplete work to the Gap Tracker.
7. **No silent deferral** — If you do not implement a spec requirement, you MUST either add it to the Gap Tracker or get a Decision Record entry. Silently dropping requirements — building the infrastructure but not the behavior, matching the spec's nouns but not its verbs — is a governance violation. "Compiles and tests pass" is a prerequisite, not evidence of completion.
8. **Run `/dep-check <pkg>`** before adding any dependency — The dep-gate will block installs otherwise.

### After Implementation

9. **Run `/critical-review <module>`** — Adversarial spec fidelity review. Re-read the spec and verify your implementation actually delivers everything it describes, completely, not just structurally. Must reach FIDELITY: HIGH before proceeding. This is not optional. This is the gate that prevents hollow implementations from passing automated checks.
10. **Run `/code-review <module>`** — Post-implementation code quality review. Required before module-complete.
11. **Run `/module-complete <module>`** — Verify all 8 quality gates pass (including spec fidelity from critical-review). Required before marking WO as DONE.
11b. **If INTEGRATION task: Run `/integration-logic <module-a> <module-b>`** — Verify the wiring is complete. Include the verdict (WIRED/PARTIAL/BROKEN) in the Work Order validation notes.
12. **Update WO status** — Set to VALIDATION (if awaiting review) or DONE (if all gates pass).
13. **Run `/trace-check`** — Verify traceability chains are intact after changes. (Also runs automatically at session start and before commits.)

### Commit After Each Work Order

14. **When a WO reaches DONE, commit and push immediately.** Each WO is a self-contained unit of traceable work and a natural commit boundary. Do not batch multiple completed WOs into a single commit.
15. **Commit message must reference the WO ID.** Format: `WO-N.M.T-X: <description of what was implemented>`. For INTEGRATION tasks, append the integration verdict: `WO-N.M.T-X: Wire ES-1.1 → ES-1.2 [WIRED]`. This ties the git history to the traceability chain.
16. **Stage only files related to the WO.** Include the module source, tests, the WO file itself, and the updated Work Ledger. Do not stage unrelated changes.
17. **Commit-gate runs automatically** — Validates traceability and scans for secrets.
18. **Run `/pre-commit`** for full hygiene — The commit-gate covers traceability and secrets; `/pre-commit` also checks TODOs, debug statements, file hygiene, build, and tests.

## Wave Completion Gate

Before proceeding to the next wave, the current wave must pass its exit criteria:

1. **All tasks in the wave have DONE Work Orders** — every BP task card assigned to the wave.
2. **All INTEGRATION tasks report WIRED** — `/integration-logic` was run for each integration task and reported WIRED.
3. **The wave's E2E_VALIDATION capstone passed** — the final task in the wave validates the end-to-end feature flow.
4. **Run `/wave-complete <wave>`** — aggregates all checks and reports PASS or lists gaps.

Do not begin the next wave until the current wave passes. If blocked, escalate per the Risk Escalation Protocol.

## Checkpoint Protocol

The checkpoint file at `.claude/checkpoint.md` is your insurance against context loss. When a session crashes or compacts, the next version of you reads this file to understand what was happening. The checkpoint you write now is what saves your successor from starting blind.

### When to Write/Update the Checkpoint

Update `.claude/checkpoint.md` at these moments:

1. **When setting a WO to IN-PROGRESS** — Write the initial checkpoint: WO ID, planned approach, files you expect to modify.
2. **After completing a significant milestone** — A function, a module, a test suite passing. Update the "Completed Steps" and "Current Task" sections.
3. **Before running quality gates** — Update to show Phase: VALIDATING, list which gates you're about to run.
4. **After a quality gate passes or fails** — Update the Quality Gates checklist.
5. **When a WO reaches DONE** — Clear the checkpoint by overwriting with: `<!-- No active work. Last WO: WO-X.Y.Z-A, completed YYYY-MM-DD -->`

### Checkpoint Format

```markdown
<!-- EPL Checkpoint — Updated: {ISO timestamp} -->

## Active Work Order
- **WO ID:** WO-N.M.T-X
- **WO File:** WorkOrders/WO-N.M.T-X.md
- **Status:** IN-PROGRESS
- **Phase:** {PLANNING | IMPLEMENTING | TESTING | FIXING | VALIDATING}

## Files In Progress
- `Code/path/to/file1.ts` — {brief description}
- `Code/path/to/file2.ts` — {brief description}

## Quality Gates
- [ ] Gate 1: Interface contracts implemented
- [ ] Gate 2: Unit tests cover public methods
- [ ] Gate 3: No TODO/FIXME comments
- [ ] Gate 4: No GPL dependencies
- [ ] Gate 5: Builds without warnings
- [ ] Gate 6: Performance meets targets
- [ ] Gate 7: Integration points verified

## Completed Steps
- {What you've finished}

## Current Task
{What you're actively doing right now}

## Remaining Work
- {What's left}

## Blockers
{Any issues, or "None"}
```

### Why This Matters

Session hooks read this file automatically on startup, resume, and compaction. The compact hook (the most critical recovery point) displays the full checkpoint with a staleness indicator. Without a checkpoint, the next agent starts blind and may duplicate or contradict your work.

## Traceability is Continuous

- The Work Ledger auto-refreshes at every session start, resume, and compaction recovery.
- Broken traceability chains (orphan IDs, missing parents) are errors that block commits.
- The traceability chain for every piece of work must be traceable: `WO → BP → ES → PVD`.
- If `/trace-check` reports errors, fix them before continuing implementation.
