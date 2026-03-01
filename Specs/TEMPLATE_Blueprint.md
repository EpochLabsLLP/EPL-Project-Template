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

{3-5 principles governing how this project is built. These are operational
rules that agents follow during execution.}

1. **{Principle 1}:** {e.g., "Foundation modules before feature modules"}
2. **{Principle 2}:** {e.g., "Tests accompany every implementation task"}
3. **{Principle 3}:** {e.g., "Interface contracts verified before downstream work begins"}

---

## 2. Dependency Graph

```
{ASCII dependency graph showing task dependencies.
 Use arrows to show "must complete before" relationships.}

Example:
  Wave 1 (Foundation):
    BP-1.1.1 ──► BP-1.1.2
    BP-1.2.1 ──► BP-1.2.2
                     │
  Wave 2 (Core):     ▼
    BP-2.1.1 ──► BP-2.1.2 ──► BP-2.1.3
    BP-3.1.1 ────────────────► BP-3.1.2

  Wave 3 (Integration):
    BP-2.1.3 + BP-3.1.2 ──► BP-4.1.1 (integration)
```

---

## 3. Phase / Wave Schedule

### Wave 1: {Wave Name} (e.g., Foundation)
- **Objective:** {What this wave delivers}
- **Prerequisites:** None (first wave)
- **Tasks:** BP-{list task IDs}
- **Exit criteria:** {What must be true before proceeding to Wave 2}

### Wave 2: {Wave Name} (e.g., Core Features)
- **Objective:** {What this wave delivers}
- **Prerequisites:** Wave 1 complete
- **Tasks:** BP-{list task IDs}
- **Exit criteria:** {What must be true before proceeding to Wave 3}

### Wave 3: {Wave Name} (e.g., Integration & Polish)
- **Objective:** {What this wave delivers}
- **Prerequisites:** Wave 2 complete
- **Tasks:** BP-{list task IDs}
- **Exit criteria:** {All acceptance criteria met, integration tests pass}

---

## 4. Task Cards

<!-- Each task gets a BP-N.M.T identifier.
     N.M = ES module ID, T = task sequence within that module.
     Every task MUST have: dependencies, acceptance criteria, interface contracts,
     and complexity estimate. -->

### BP-1.1.1: {Task Name}
- **Module:** ES-1.1
- **Wave:** 1
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

### BP-1.1.2: {Task Name}
- **Module:** ES-1.1
- **Wave:** 1
- **Complexity:** {Low / Medium / High}
- **Dependencies:** BP-1.1.1
- **Description:** {What this task implements}
- **Interface Contracts:**
  - {contracts}
- **Acceptance Criteria:**
  - [ ] {criterion 1}
  - [ ] {criterion 2}

### BP-2.1.1: {Task Name}
- **Module:** ES-2.1
- **Wave:** 2
{Continue pattern for all tasks...}

---

## 5. Agent Operating Rules

{Rules that govern agent behavior during Blueprint execution.}

1. **Read before write.** Always read the Engineering Spec module and relevant interface contracts before implementing.
2. **Test with build.** Every implementation task includes its corresponding tests.
3. **No modifications to frozen specs.** If the spec seems wrong, log in Gap Tracker and escalate.
4. **Interface contracts are sacred.** Match signatures, types, and error contracts exactly.
5. **One Work Order at a time.** Complete current WO before requesting next.

---

## 6. Integration Checkpoints

{Points in the build where cross-module integration is verified.}

| Checkpoint | After Wave | Verification |
|-----------|-----------|-------------|
| {Checkpoint 1} | Wave 1 | {What's tested: e.g., "Foundation modules communicate correctly"} |
| {Checkpoint 2} | Wave 2 | {What's tested} |
| {Final integration} | Wave 3 | {Full system integration test} |

---

## 7. Quality Gates Checklist

Before marking the Blueprint as fully executed:

- [ ] All task cards have completed Work Orders
- [ ] All acceptance criteria met
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
