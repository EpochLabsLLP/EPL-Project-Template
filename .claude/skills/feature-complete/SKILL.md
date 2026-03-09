---
name: feature-complete
description: Validate that a PVD feature is fully implemented end-to-end. Checks all Blueprint tasks, integration wiring, and E2E test scenarios for a specific PVD feature. Use after completing a feature's wave to verify the full vertical slice works.
argument-hint: <PVD-N>
user-invokable: true
---

# feature-complete

Validates that a PVD feature is fully implemented, integrated, and tested end-to-end.

## When to Use

- After completing all Blueprint tasks for a PVD feature
- Before declaring a feature "shippable"
- When verifying that a vertical slice is genuinely complete (not just individual modules)

## How to Invoke

/feature-complete <PVD-N>

## Execution

When invoked with a PVD feature ID ($ARGUMENTS, e.g., "PVD-3"):

1. **Identify all modules for this feature.**
   Read the Engineering Spec and find all ES-N.M modules where N matches the PVD feature number.

2. **Identify all Blueprint tasks for this feature.**
   Read the Blueprint and find all BP-N.M.T tasks where N matches. Include all task types
   (IMPLEMENTATION, INTEGRATION, SKELETON, E2E_VALIDATION).

3. **Check Work Order completion.**
   For each BP task, find the corresponding WO:
   - Count DONE, IN-PROGRESS, PENDING, FAILED
   - PASS only if all WOs are DONE

4. **Check integration wiring.**
   Read the Module Integration Matrix (Engineering Spec Section 6):
   - Find all rows where Source or Target is an ES-N.M module for this feature
   - For each integration point, verify an INTEGRATION task exists in the Blueprint
   - Verify each INTEGRATION task has a DONE WO with WIRED verdict
   - FAIL if any integration point is unwired

5. **Check E2E test coverage.**
   Read the Testing Plans:
   - Find E2E/integration test scenarios for this feature
   - Verify they have corresponding test implementations
   - PASS if E2E tests exist and pass; WARN if no E2E tests defined

6. **Verify feature flow.**
   Describe the user journey for this PVD feature (from PVD description):
   - Can a user complete the journey from entry point to expected outcome?
   - Are all UI elements connected to their backend services?
   - Does data flow correctly through the full chain?

7. **Report:**

   | Check | Status | Details |
   |-------|--------|---------|
   | Modules | — | {list ES-N.M modules for this feature} |
   | BP tasks complete | PASS/FAIL | {X/Y tasks have DONE WOs} |
   | Integration wired | PASS/FAIL | {X/Y integration points verified WIRED} |
   | E2E tests | PASS/WARN | {E2E test status} |
   | Feature flow | PASS/FAIL | {can user complete the journey?} |

8. **Verdict:**
   - **FEATURE COMPLETE** → All checks pass. This PVD feature is shippable.
   - **FEATURE INCOMPLETE** → List specific gaps preventing completion.
