---
name: wave-complete
description: Validate that a wave's exit criteria are met before proceeding to the next wave. Checks all module-complete gates, integration verification, and E2E validation capstone for the specified wave.
argument-hint: <wave-number>
user-invocable: true
---

# wave-complete

Validates that a Blueprint wave is fully complete and ready for the next wave to begin.

## When to Use

- After completing all tasks in a wave, before starting the next wave
- When checking if a wave's exit criteria are met
- Per execution-protocol.md: required before proceeding to the next wave

## How to Invoke

/wave-complete <wave-number>

## Execution

When invoked with a wave number ($ARGUMENTS):

1. **Identify all BP tasks in the wave.**
   Read the frozen Blueprint and find all task cards with `**Wave:** $ARGUMENTS`.

2. **Check Work Order existence and status for each task.**
   For each BP task in the wave, find the corresponding WO in `WorkOrders/`.
   - WO file must exist (not just E2E WOs — implementation WOs too)
   - All WOs must be DONE → PASS
   - Any BP task with no WO → FAIL: "BP-{N.M.T} has no Work Order"
   - Any WO not DONE → FAIL (list which tasks are incomplete)

3. **Verify INTEGRATION tasks.**
   For each task with `**Task Type:** INTEGRATION`:
   - Search for evidence that `/integration-logic` was run
   - Verify it reported WIRED
   - FAIL if any integration task is PARTIAL or BROKEN

4. **Verify E2E_VALIDATION capstone.**
   Find the task with `**Task Type:** E2E_VALIDATION` in this wave:
   - Verify its WO is DONE → PASS
   - If no E2E_VALIDATION task exists → WARN: "Wave has no E2E validation capstone"
   - If WO not DONE → FAIL

5. **Verify Validation Evidence in each WO.**
   For each DONE WO in this wave, check that the Validation Evidence section (Section 6) is completed:
   - Grep WO file for `## Validation Evidence` or `## 6. Validation Evidence`
   - Check for at least one checked item (`- [x]`) in the evidence section
   - FAIL if the section is missing or has no checked items: "WO-{N.M.T}-{X} marked DONE but has no validation evidence"
   - Check specifically for:
     - `/code-review` verdict recorded → FAIL if missing
     - `/integration-logic` verdict recorded (for INTEGRATION tasks) → FAIL if missing
     - Test results recorded → WARN if missing

6. **Check Gap Tracker tier state** (per definition-of-done.md Phase Closure Rules):
   - Tier 0 > 0 → FAIL: "Cannot close wave with open Tier 0 items"
   - Tier 1 > 0 → FAIL: "Cannot close wave with open Tier 1 items"
   - Tier 2 > 0 → WARN: "Tier 2 items open — require deferral Decision Record entry"

7. **Run `/trace-check --quick`** to verify traceability chains are intact.

8. **Report:**

   | Check | Status | Details |
   |-------|--------|---------|
   | WO existence | PASS/FAIL | {X/Y BP tasks have WOs} |
   | Tasks complete | PASS/FAIL | {X/Y WOs are DONE} |
   | Validation evidence | PASS/FAIL | {X/Y WOs have recorded evidence} |
   | Integration verified | PASS/FAIL/N/A | {X/Y integration points WIRED with evidence} |
   | E2E capstone | PASS/FAIL/WARN | {capstone WO status} |
   | Gap Tracker tiers | PASS/FAIL/WARN | {Tier 0: N, Tier 1: N, Tier 2: N} |
   | Traceability | PASS/FAIL | {trace-check result} |

9. **Verdict:**
   - **ALL PASS** → Wave $ARGUMENTS is COMPLETE. Proceed to next wave.
   - **ANY FAIL** → Wave $ARGUMENTS is NOT COMPLETE. List what must be resolved.
