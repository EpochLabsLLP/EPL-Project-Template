---
name: integration-logic
description: Verify cross-module integration wiring is complete and correct. Use after implementing interfaces that span module boundaries, when debugging cross-module issues, or to audit all completed module integrations at once. Invoke with no arguments to check ALL completed modules.
user-invocable: true
argument-hint: module-a module-b OR all
---

# Integration Logic

## When to Use

- **Required** for every INTEGRATION-type Blueprint task (per execution-protocol.md)
- **Required** before `/module-complete` if the module appears in the Integration Matrix
- **Required** before `/wave-complete` — run with `all` to verify all wave integrations
- After implementing interfaces that span module boundaries
- When debugging cross-module issues (dependency injection, data contracts, error propagation)

## Execution Modes

### Mode 1: All Completed Modules (default — no arguments or `all`)

When `$ARGUMENTS` is empty or `all`:

1. **Load the Engineering Spec** — Find the Module Integration Matrix (typically in a "Module Integration" or "Integration" section). This matrix defines which modules connect to which.

2. **Identify completed modules** — Scan `WorkOrders/` for WOs with status DONE or VALIDATION. Extract the ES module IDs they reference (from the Blueprint → ES traceability chain). These are the modules with completed implementation.

3. **Build the integration pair list** — From the Integration Matrix, find all pairs where BOTH modules have completed WOs. These are the integrations that should be wired.

4. **For each pair, run the integration check** (same as Mode 2, Step 3 below).

5. **Report a summary matrix:**
   ```
   INTEGRATION AUDIT — {N} pairs checked

   | Module A | Module B | Points | Wired | Partial | Broken | Verdict |
   |----------|----------|--------|-------|---------|--------|---------|

   Overall: {X}/{N} WIRED, {Y} PARTIAL, {Z} BROKEN
   ```

6. **If any pair is BROKEN or PARTIAL**, list the specific gaps with file paths and line numbers.

### Mode 2: Specific Pair (two module names)

When `$ARGUMENTS` contains two module names:

1. **Load specs for both modules.** Read their interface contracts, expected inputs/outputs, and dependency declarations.

2. **Identify all integration points** between the two modules:
   - Service calls (A calls B's API/methods)
   - Shared data (database tables, shared state, event buses)
   - Dependency injection (A depends on B's interface)
   - Event/callback wiring (A listens for B's events, registers handlers, subscribes to messages)

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

   **Behavioral Wiring** *(check this even if the other three pass)*
   - For every event, message type, or route that module B exposes: is there a registered handler in the consuming module?
   - Grep for registration patterns: `.onMessage(`, `.on(`, `.addEventListener(`, `.registerHandler(`, `.registerRoute(`, `.subscribe(`, `.listen(`
   - For each expected event/message type in the spec, confirm a handler is registered for that specific type — not just that the pattern exists somewhere.
   - A structural dependency (constructor injection, `connect*()` method) is NOT sufficient if the consuming module never registers a handler for the events it needs to receive.

4. **Report as a wiring checklist:**
   | Integration Point | From -> To | Registered? | Types Match? | Errors Handled? | Handlers Wired? | Status |
   |-------------------|-----------|:-----------:|:------------:|:---------------:|:---------------:|--------|

5. **Verdict:** WIRED (all points connected), PARTIAL (list gaps), or BROKEN (list failures).

   > **Behavioral wiring failures are BROKEN, not PARTIAL.** A module that is structurally connected but never receives events it depends on is not wired — it will silently fail at runtime with no structural trace.

## Important

- Use `/spec-lookup` first if you're unsure about module interface contracts
- The Integration Matrix in the Engineering Spec is the source of truth for which modules connect
- WIRED means verified with evidence (grep, file reads) — not assumed from code structure
- Include file paths and line numbers for every verified integration point
- **Behavioral wiring is the most common silent failure mode.** Structural wiring (constructor injection, connect methods) is visible in architecture diagrams. Event handler registration is not — it only fails at runtime when the first message goes unhandled. Check it explicitly every time.
