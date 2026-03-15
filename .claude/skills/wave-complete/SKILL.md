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

2. **Check Work Order status for each task.**
   For each BP task in the wave, find the corresponding WO in WorkOrders/.
   - All WOs must be DONE → PASS
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

5. **Run `/trace-check --quick`** to verify traceability chains are intact.

6. **Report:**

   | Check | Status | Details |
   |-------|--------|---------|
   | Tasks complete | PASS/FAIL | {X/Y tasks have DONE WOs} |
   | Integration verified | PASS/FAIL/N/A | {X/Y integration points WIRED} |
   | E2E capstone | PASS/FAIL/WARN | {capstone WO status} |
   | Traceability | PASS/FAIL | {trace-check result} |

7. **Verdict:**
   - **ALL PASS** → Wave $ARGUMENTS is COMPLETE. Proceed to next wave.
   - **ANY FAIL** → Wave $ARGUMENTS is NOT COMPLETE. List what must be resolved.
