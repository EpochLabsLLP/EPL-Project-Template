---
name: integration-logic
description: Verify cross-module integration wiring is complete and correct. Use when connecting two modules together, after implementing interfaces that span module boundaries, or when debugging issues that cross module lines (dependency injection, data contracts, error propagation).
argument-hint: <module-a> <module-b>
---

# Integration Logic

When invoked with two module names (`$0` and `$1`):

1. **Load specs for both modules.** Read their interface contracts, expected inputs/outputs, and dependency declarations.

2. **Identify all integration points** between the two modules:
   - Service calls (A calls B's API/methods)
   - Shared data (database tables, shared state, event buses)
   - Dependency injection (A depends on B's interface)
   - Event/callback wiring (A listens for B's events)

3. **For each integration point, verify the wiring:**

   **Dependency Registration**
   - Is the dependency registered in the DI container / service locator?
   - Is the interface-to-implementation binding correct?
   - Is the lifecycle scope correct (singleton, scoped, transient)?

   **Data Contract**
   - Do the types match across the boundary? (A sends what B expects)
   - Are nullable/optional fields handled on both sides?
   - Are serialization formats compatible?

   **Error Propagation**
   - If B fails, does A handle it gracefully?
   - Are timeouts configured for cross-module calls?
   - Is retry logic appropriate (idempotent operations only)?

4. **Report as a wiring checklist:**
   | Integration Point | From -> To | Registered? | Types Match? | Errors Handled? | Status |
   |-------------------|-----------|:-----------:|:------------:|:---------------:|--------|

5. **Verdict:** WIRED (all points connected), PARTIAL (list gaps), or BROKEN (list failures).
