---
name: module-complete
description: Run all 6 quality gates against a module before marking it complete. This is the Definition of Done enforcer. Use before marking any module as done, when checking if a module meets all completion criteria, or when verifying quality gates (no stubs, tests, no TODOs, license compliance, clean build, performance).
argument-hint: <module>
---

# Module Complete

This skill enforces the Definition of Done defined in `/.claude/rules/quality-gates.md`. A module cannot be marked complete unless ALL gates pass.

When invoked with a module name (`$ARGUMENTS`):

1. **Read the quality gates** from `/.claude/rules/quality-gates.md`.

2. **Run each gate** against the specified module:

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

3. **Report:**
   | Gate | Requirement | Status | Evidence |
   |------|-------------|--------|----------|
   | 1 | No stubs | PASS/FAIL | {details} |
   | 2 | Tests exist | PASS/FAIL | {count: X/Y methods tested} |
   | 3 | No TODOs | PASS/FAIL | {count found, file:line refs} |
   | 4 | No GPL deps | PASS/FAIL | {flagged deps} |
   | 5 | Clean build | PASS/FAIL | {warnings/errors} |
   | 6 | Performance | PASS/FAIL/N/A | {target vs actual} |

4. **Verdict:**
   - **ALL PASS** -> Module is COMPLETE. Update the gap tracker: check off the item.
   - **ANY FAIL** -> Module is NOT COMPLETE. List what must be fixed. Do not mark complete.
