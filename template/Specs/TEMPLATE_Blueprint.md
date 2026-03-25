<!-- TEMPLATE: Blueprint
     The agent-executable build plan. Decomposes the Engineering Spec into
     discrete, assignable task cards organized into waves with dependencies
     and acceptance criteria.

     USAGE:
     1. Ensure PVD, Engineering Spec, and (if UI) UX Spec are FROZEN
     2. Copy this file to: Specs/{Abbrev}_Blueprint_DRAFT.md
     3. Replace all {placeholders} with real values
     4. Assign BP-N.M.T identifiers (N.M = ES module, T = task sequence)
     5. Change Status to FROZEN and rename: {Abbrev}_Blueprint_v1.md
     6. Proceed to Testing Plans

     TRACEABILITY: BP-N.M.T traces to ES-N.M.
     Example: BP-3.2.4 = Task #4 under ES Module 3.2 (which implements PVD-3).

     IMPORTANT: The Blueprint is NEVER modified during development.
     Divergence is recorded in the Gap Tracker and Decision Record. -->

# {ProjectName} — Blueprint

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **Implements** | `Specs/{Abbrev}_Engineering_Spec_v{N}.md` |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## 1. Build Principles

{3-5 project-specific principles governing how this project is built. These are operational
rules that agents follow during execution.}

1. **Build vertically, not horizontally.** Each wave delivers a complete feature slice — from data layer through UI — not a technical layer. A working vertical slice proves more than a perfect horizontal layer that can't be demonstrated.
2. **Integration is a task, not a phase.** Every module boundary gets an explicit INTEGRATION task in the Blueprint. If Module A talks to Module B, someone must explicitly build and verify that wiring.
3. **{Principle 3}:** {e.g., "Tests accompany every implementation task"}
4. **{Principle 4}:** {e.g., "Interface contracts verified before downstream work begins"}
5. **{Principle 5}:** {e.g., "No stubs — every method contains real logic"}

---

## 2. Dependency Graph

```
{ASCII dependency graph showing task dependencies.
 Use arrows to show "must complete before" relationships.
 Include INTEGRATION and E2E_VALIDATION tasks explicitly.}

Example:
  Wave 0 (Skeleton):
    BP-0.0.1 ──► BP-0.0.2 ──► BP-0.0.3 (E2E_VALIDATION)

  Wave 1 (Feature: PVD-1):
    BP-1.1.1 ──► BP-1.2.1 ──► BP-1.1.2 (INTEGRATION) ──► BP-1.0.99 (E2E_VALIDATION)

  Wave 2 (Feature: PVD-2):
    BP-2.1.1 ──► BP-2.1.2 ──► BP-2.1.3 (INTEGRATION) ──► BP-2.0.99 (E2E_VALIDATION)

  Final Wave (System Integration):
    BP-1.0.99 + BP-2.0.99 ──► BP-0.0.99 (cross-feature E2E_VALIDATION)
```

---

## 3. Phase / Wave Schedule

<!-- Waves are organized as VERTICAL slices, not horizontal layers.
     Wave 0 is always the Walking Skeleton. Waves 1-N are feature threads.
     The final wave handles cross-feature integration and polish.
     Run /wave-complete <N> before proceeding to the next wave. -->

### Wave 0: Walking Skeleton (MANDATORY)
- **Objective:** Prove architecture with the thinnest possible end-to-end thread
- **Prerequisites:** None
- **Tasks:** SKELETON-type tasks only (BP-0.x.x)
- **Exit criteria:** One complete request/response through all architectural layers; builds, runs, passes at least one E2E test
- **NOTE:** Wave 0 deliberately cuts corners on features — it proves the plumbing, not the product. Minimal business logic.

### Wave {N}: {PVD Feature Name} (Feature Thread)
- **Objective:** Deliver one complete, user-facing feature end-to-end
- **Prerequisites:** Wave 0 + {any cross-feature dependencies}
- **Tasks:** BP-{list task IDs} — mix of IMPLEMENTATION + INTEGRATION + E2E_VALIDATION
- **Exit criteria:** Feature's E2E scenarios pass, all `/module-complete` gates pass, all integration points verified via `/integration-logic`
- **RULE:** The LAST task in every feature wave MUST be an E2E_VALIDATION capstone

{Repeat for each PVD feature. One wave per feature or vertical slice.}

### Final Wave: System Integration & Polish
- **Objective:** Cross-feature integration, performance tuning, security hardening
- **Prerequisites:** All feature waves complete
- **Tasks:** Cross-feature INTEGRATION + system-level E2E_VALIDATION
- **Exit criteria:** Full system integration tests pass, performance budgets met, security review complete

---

## 4. Task Cards

<!-- Each task gets a BP-N.M.T identifier.
     N.M = ES module ID, T = task sequence within that module.
     Every task MUST have: Task Type, dependencies, acceptance criteria, interface contracts,
     and complexity estimate.

     TASK TYPES:
     - SKELETON: Walking Skeleton tasks (Wave 0 only) — thinnest vertical slice
     - IMPLEMENTATION: Standard build tasks — real logic, real tests
     - INTEGRATION: Wiring tasks — connects two modules per the Integration Matrix
     - E2E_VALIDATION: End-to-end validation — proves a complete feature flow works

     Every wave's LAST task must be E2E_VALIDATION.
     Every row in the Integration Matrix should have a corresponding INTEGRATION task. -->

### BP-0.0.1: {Walking Skeleton Task}
- **Module:** ES-{N.M}
- **Wave:** 0
- **Task Type:** SKELETON
- **Complexity:** {Low / Medium / High}
- **Dependencies:** {None / list}
- **Description:** {Thinnest end-to-end slice proving this layer works}
- **Acceptance Criteria:**
  - [ ] Request travels through this layer end-to-end
  - [ ] At least one integration test passes

### BP-0.0.{last}: {Walking Skeleton E2E Validation}
- **Module:** (cross-module)
- **Wave:** 0
- **Task Type:** E2E_VALIDATION
- **Complexity:** Medium
- **Dependencies:** All other Wave 0 tasks
- **Description:** Validate the skeleton runs end-to-end: build, launch, one complete request/response
- **Acceptance Criteria:**
  - [ ] Application builds and launches
  - [ ] One request flows through all architectural layers
  - [ ] At least one E2E test passes

### BP-1.1.1: {Implementation Task}
- **Module:** ES-1.1
- **Wave:** 1
- **Task Type:** IMPLEMENTATION
- **Complexity:** {Low / Medium / High}
- **Dependencies:** {None / list of BP IDs}
- **Description:** {What this task implements}
- **Interface Contracts:**
  - {Which frozen contracts from Engineering Spec apply}
- **Acceptance Criteria:**
  - [ ] {Testable criterion 1}
  - [ ] {Testable criterion 2}
  - [ ] {Testable criterion 3}
- **Notes:** {Any implementation guidance or constraints}

### BP-1.1.2: {Integration Task — Wires ES-1.1 to ES-1.2}
- **Module:** ES-1.1 ↔ ES-1.2
- **Wave:** 1
- **Task Type:** INTEGRATION
- **Complexity:** {complexity}
- **Dependencies:** BP-1.1.1, BP-1.2.1
- **Description:** {Wire module A to module B per Integration Matrix}
- **Integrates:** ES-1.1 → ES-1.2 (from Module Integration Matrix)
- **Interface Contracts:**
  - Contract: ES-1.1 ↔ ES-1.2 (from Engineering Spec Section 7)
- **Acceptance Criteria:**
  - [ ] `/integration-logic ES-1.1 ES-1.2` reports WIRED
  - [ ] Integration test for this boundary passes
  - [ ] Data flows correctly across the module boundary
  - [ ] **Behavioral wiring verified:** All event handlers, message handlers, and callback registrations for this wiring are present in bootstrap/main entry point. Grep for: `.onMessage(`, `.on(`, `.addEventListener(`, `.registerHandler(`, `.registerRoute(`, `.subscribe(`, `.listen(`

### BP-1.0.99: {E2E Validation — Feature 1 Complete}
- **Module:** (cross-module)
- **Wave:** 1
- **Task Type:** E2E_VALIDATION
- **Complexity:** Medium
- **Dependencies:** All other Wave 1 tasks
- **Description:** Validate the complete PVD-1 feature flow end-to-end
- **Acceptance Criteria:**
  - [ ] User can complete the PVD-1 journey from entry to result
  - [ ] All E2E test scenarios for this feature pass
  - [ ] `/feature-complete PVD-1` reports COMPLETE

{Continue pattern for all waves. Each wave includes IMPLEMENTATION + INTEGRATION + E2E_VALIDATION tasks.}

---

## 5. Agent Operating Rules

{Rules that govern agent behavior during Blueprint execution.}

1. **Read before write.** Always read the Engineering Spec module and relevant interface contracts before implementing.
2. **Test with build.** Every implementation task includes its corresponding tests.
3. **No modifications to frozen specs.** If the spec seems wrong, log in Gap Tracker and escalate.
4. **Interface contracts are sacred.** Match signatures, types, and error contracts exactly.
5. **One Work Order at a time.** Complete current WO before requesting next.
6. **Verify integration after wiring.** After completing an INTEGRATION task, run `/integration-logic` for the integrated modules and include the WIRED verdict in the WO.

---

## 6. Integration Checkpoints

<!-- Every row in the Engineering Spec's Module Integration Matrix (Section 6) should have
     a corresponding INTEGRATION-type task card in Section 4 above. If Module A talks to
     Module B, there must be a BP task that explicitly builds and verifies that wiring.

     Wave exit requires /wave-complete to pass before proceeding to the next wave. -->

{Points in the build where cross-module integration is verified.}

| Checkpoint | After Wave | Verification |
|-----------|-----------|-------------|
| Walking Skeleton | Wave 0 | {End-to-end plumbing works: build, launch, one request/response} |
| {Feature 1} | Wave 1 | {All integration points WIRED, E2E capstone passes} |
| {Feature N} | Wave N | {All integration points WIRED, E2E capstone passes} |
| {Full system} | Final | {Cross-feature integration, performance, security} |

---

## 7. Quality Gates Checklist

Before marking the Blueprint as fully executed:

- [ ] All task cards have completed Work Orders
- [ ] All acceptance criteria met
- [ ] All INTEGRATION tasks report WIRED (via `/integration-logic`)
- [ ] Each wave's E2E_VALIDATION capstone passed
- [ ] `/feature-complete` passed for each PVD feature
- [ ] Integration checkpoints passed
- [ ] No Tier 0 or Tier 1 items in Gap Tracker
- [ ] Performance budgets from Engineering Spec met
- [ ] Security review complete for sensitive modules

---

## 8. Risk Escalation Protocol

| Situation | Action |
|-----------|--------|
| Acceptance criteria can't be met as written | Log in Gap Tracker, escalate to Nathan |
| Interface contract seems wrong | Log in Gap Tracker, DO NOT modify spec |
| Performance budget can't be met | Log in Gap Tracker with profiling data |
| Dependency on unfinished Work Order | Wait or request re-sequencing from Nathan |
| Discovered security concern | Stop work, escalate immediately |

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial build plan | {Author} |
