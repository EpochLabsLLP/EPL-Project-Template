---
name: module-complete
description: Run all 8 quality gates against a module before marking it complete. This is the Definition of Done enforcer. Requires /critical-review (spec fidelity) and /code-review (code quality) as prerequisites. Use before marking any module as done.
argument-hint: <module>
---

# Module Complete

This skill enforces the Definition of Done defined in `/.claude/rules/quality-gates.md`. A module cannot be marked complete unless ALL gates pass.

When invoked with a module name (`$ARGUMENTS`):

1. **Read the quality gates** from `/.claude/rules/quality-gates.md`.

2. **Pre-check A: Critical Review evidence (Gate 0a)**
   - Search the current conversation AND the Work Order's Validation Evidence section for evidence that `/critical-review` was run for this module.
   - Look for: critical-review output tables, "FIDELITY: HIGH" or "FIDELITY: GAPS FOUND" verdicts, spec-requirement-to-implementation mappings.
   - If NO evidence found → **FAIL Gate 0a** with message: "Run `/critical-review $ARGUMENTS` first. Critical review (spec fidelity) is a prerequisite for module completion."
   - If evidence found but verdict is GAPS FOUND → **FAIL Gate 0a** with message: "Critical review found spec fidelity gaps. Fix all gaps and re-run `/critical-review` until FIDELITY: HIGH."
   - If FIDELITY: HIGH → PASS, continue.

3. **Pre-check B: Code Review evidence (Gate 0b)**
   - Search the current conversation for evidence that `/code-review` was run for this module.
   - Look for: code-review output tables, "PASS"/"CONDITIONAL"/"FAIL" verdicts, file:line references from code-review.
   - If NO evidence found → **FAIL Gate 0b** with message: "Run `/code-review $ARGUMENTS` first, then re-run `/module-complete`. Code review is a prerequisite for module completion."
   - If evidence found → note the verdict and continue.

4. **Run each gate** against the specified module:

   **Gate 1: No stubs**
   - Read all source files in the module
   - Search for stub patterns: `throw NotImplementedError`, `TODO`, `pass` with no logic,
     empty method bodies, `return null` placeholders
   - PASS only if every interface method contains real logic

   **Gate 2: Test coverage**
   - Identify all public methods/functions in the module
   - Search for corresponding test files
   - Verify each public method has at least one test
   - PASS only if all public methods are tested

   **Gate 3: No TODO/FIXME**
   - Grep the module for TODO, FIXME, HACK, XXX, TEMP comments
   - PASS only if zero found

   **Gate 4: No GPL dependencies**
   - Check the module's imports/dependencies against known GPL packages
   - If unsure about a dependency's license, run `/dep-check` on it
   - PASS only if all dependencies are permissively licensed

   **Gate 5: Clean build**
   - Build/compile the module (if applicable to the tech stack)
   - PASS only if zero warnings and zero errors

   **Gate 6: Performance targets**
   - Check the Engineering Spec for performance requirements on this module
   - If targets exist, verify they're met (or document how to verify)
   - If no targets specified, PASS with note "no performance targets in spec"

   **Gate 7: Integration verified**
   - Read the Engineering Spec's Module Integration Matrix (Section 6)
   - Identify all rows where this module is Source or Target
   - If integration points exist:
     - Search for evidence that `/integration-logic` was run for each integration point
     - Check that each reported WIRED (not PARTIAL or BROKEN)
     - PASS only if all integration points verified as WIRED
   - If NO integration points exist (standalone module):
     - PASS with note "no integration points in Module Integration Matrix"

5. **Post-check: Work Order status (Gate 9)**
   - Search `WorkOrders/` for a WO that corresponds to this module's Blueprint task.
   - If WO found and status is DONE → PASS
   - If WO found and status is VALIDATION → PASS with note: "WO in VALIDATION — set to DONE after all gates pass"
   - If WO found and status is IN-PROGRESS → WARN: "Update WO status to VALIDATION or DONE"
   - If NO corresponding WO found → WARN: "No Work Order found for this module"

6. **Report:**
   | Gate | Requirement | Status | Evidence |
   |------|-------------|--------|----------|
   | 0a | Critical review | PASS/FAIL | {/critical-review verdict — FIDELITY: HIGH required} |
   | 0b | Code review | PASS/FAIL | {/code-review verdict} |
   | 1 | No stubs | PASS/FAIL | {details} |
   | 2 | Tests exist | PASS/FAIL | {count: X/Y methods tested} |
   | 3 | No TODOs | PASS/FAIL | {count found, file:line refs} |
   | 4 | No GPL deps | PASS/FAIL | {flagged deps} |
   | 5 | Clean build | PASS/FAIL | {warnings/errors} |
   | 6 | Performance | PASS/FAIL/N/A | {target vs actual} |
   | 7 | Integration | PASS/FAIL/N/A | {X/Y integration points WIRED} |
   | 8 | Spec fidelity | PASS/FAIL | {/critical-review FIDELITY: HIGH with evidence} |
   | 9 | WO status | PASS/WARN | {WO ID and status} |

7. **Verdict:**
   - **ALL PASS** (Gates 0a-8, Gate 9 PASS or WARN) -> Module is COMPLETE. Update the gap tracker: check off the item. Set WO status to DONE.
   - **ANY FAIL** (Gates 0a-8) -> Module is NOT COMPLETE. List what must be fixed. Do not mark complete.
