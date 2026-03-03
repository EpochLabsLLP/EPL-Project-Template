---
name: module-complete
description: Run all 6 quality gates against a module before marking it complete. This is the Definition of Done enforcer. Use before marking any module as done, when checking if a module meets all completion criteria, or when verifying quality gates (no stubs, tests, no TODOs, license compliance, clean build, performance).
argument-hint: <module>
---

# Module Complete

This skill enforces the Definition of Done defined in `/.claude/rules/quality-gates.md`. A module cannot be marked complete unless ALL gates pass.

When invoked with a module name (`$ARGUMENTS`):

1. **Read the quality gates** from `/.claude/rules/quality-gates.md`.

2. **Pre-check: Code Review evidence (Gate 0)**
   - Search the current conversation for evidence that `/code-review` was run for this module.
   - Look for: code-review output tables, "PASS"/"CONDITIONAL"/"FAIL" verdicts, file:line references from code-review.
   - If NO evidence found → **FAIL Gate 0** with message: "Run `/code-review $ARGUMENTS` first, then re-run `/module-complete`. Code review is a prerequisite for module completion."
   - If evidence found → note the verdict and continue.

3. **Run each gate** against the specified module:

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

4. **Post-check: Work Order status (Gate 7)**
   - Search `WorkOrders/` for a WO that corresponds to this module's Blueprint task.
   - If WO found and status is DONE → PASS
   - If WO found and status is VALIDATION → PASS with note: "WO in VALIDATION — set to DONE after all gates pass"
   - If WO found and status is IN-PROGRESS → WARN: "Update WO status to VALIDATION or DONE"
   - If NO corresponding WO found → WARN: "No Work Order found for this module"

5. **Report:**
   | Gate | Requirement | Status | Evidence |
   |------|-------------|--------|----------|
   | 0 | Code review | PASS/FAIL | {/code-review verdict} |
   | 1 | No stubs | PASS/FAIL | {details} |
   | 2 | Tests exist | PASS/FAIL | {count: X/Y methods tested} |
   | 3 | No TODOs | PASS/FAIL | {count found, file:line refs} |
   | 4 | No GPL deps | PASS/FAIL | {flagged deps} |
   | 5 | Clean build | PASS/FAIL | {warnings/errors} |
   | 6 | Performance | PASS/FAIL/N/A | {target vs actual} |
   | 7 | WO status | PASS/WARN | {WO ID and status} |

6. **Verdict:**
   - **ALL PASS** (Gates 0-6, Gate 7 PASS or WARN) -> Module is COMPLETE. Update the gap tracker: check off the item. Set WO status to DONE.
   - **ANY FAIL** (Gates 0-6) -> Module is NOT COMPLETE. List what must be fixed. Do not mark complete.
