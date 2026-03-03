---
name: code-review
description: Post-implementation quality review before marking work complete. Use after implementing a module or file, before marking it done, when you want to verify correctness against specs, or when checking code quality, security, error handling, and test coverage.
argument-hint: <module|file>
---

# Code Review

When invoked with a module or file path (`$ARGUMENTS`):

1. **Load the relevant spec.** Use the module-to-spec lookup (or search Specs/) to understand what this code SHOULD do.

2. **Read all source files** in the module or the specified file.

3. **Review against these criteria** (report pass/fail for each):

   **Correctness**
   - Does the implementation match the spec requirements exactly?
   - Are all interface contract methods implemented with real logic (no stubs)?
   - Are edge cases handled?

   **Error Handling**
   - Are errors caught and handled appropriately?
   - Are error messages useful for debugging?
   - Do failures degrade gracefully?

   **Code Quality**
   - Does the code follow the project's established patterns?
   - Are names clear and consistent with the codebase?
   - Is there unnecessary complexity that could be simplified?

   **Security**
   - No hardcoded secrets, keys, or tokens?
   - Input validated before use?
   - No SQL injection, XSS, or command injection vectors?

   **Testing**
   - Do unit tests exist for all public methods?
   - Do tests cover the happy path AND error paths?
   - Are test assertions meaningful (not just "doesn't throw")?

4. **Report findings** as a table:
   | Category | Status | Notes |
   |----------|--------|-------|

5. **List specific issues** with file:line references and suggested fixes.

6. **Give a verdict:** PASS (ready to ship), CONDITIONAL (fixable issues), or FAIL (significant rework needed).
