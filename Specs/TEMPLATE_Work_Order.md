<!-- TEMPLATE: Work Order
     A scoped assignment carved from the Blueprint. Bundles build tasks
     with their corresponding tests and acceptance criteria.

     USAGE:
     1. Ensure all frozen specs exist (PVD/PRD, Engineering Spec, Blueprint, Testing Plans)
     2. Copy this file to: WorkOrders/WO-{N.M.T}-A.md
        (N.M.T = Blueprint task ID, A = first attempt suffix)
     3. Replace all {placeholders} with real values
     4. Set Status to PENDING
     5. When work begins, update Status to IN-PROGRESS
     6. When implementation is done, update Status to VALIDATION
     7. After validation: DONE (archive to WorkOrders/_Archive/) or FAILED (archive, create -B)

     TRACEABILITY: WO-N.M.T-X traces to BP-N.M.T.
     Example: WO-3.2.4-A = First attempt at Blueprint task BP-3.2.4.

     LIFECYCLE: PENDING → IN-PROGRESS → VALIDATION → DONE / FAILED
     On FAILED: Archive this WO, create WO-N.M.T-B (increment suffix).
     On DONE: Archive to WorkOrders/_Archive/. -->

# Work Order: WO-{N.M.T}-{X}

| Field | Value |
|-------|-------|
| **WO ID** | WO-{N.M.T}-{X} |
| **Status** | PENDING / IN-PROGRESS / VALIDATION / DONE / FAILED |
| **Created** | {YYYY-MM-DD} |
| **Updated** | {YYYY-MM-DD} |
| **Assigned To** | {Agent name or team} |

---

## Traceability Chain

```
WO-{N.M.T}-{X}  →  BP-{N.M.T}  →  ES-{N.M}  →  PVD-{N}
"{WO description}" → "{BP task}" → "{ES module}" → "{PVD feature}"
```

---

## 1. Tasks

<!-- List the specific Blueprint tasks this Work Order covers.
     A WO can cover one or more related BP tasks. -->

### From BP-{N.M.T}: {Task Name}
- **Description:** {What to implement}
- **Interface Contracts:** {Reference frozen contracts from Engineering Spec}
- **Implementation Notes:** {Any guidance, constraints, or context}

### From BP-{N.M.T+1}: {Task Name} (if bundling multiple)
- **Description:** {What to implement}
- **Interface Contracts:** {contracts}

---

## 2. Testing Requirements

<!-- Reference the corresponding Testing Plan entries.
     Tests are executed as part of this Work Order, not separately. -->

### From TP-{N.M.T}: {Test Suite Name}
- [ ] {Test case 1 — description}
- [ ] {Test case 2 — description}
- [ ] {Test case 3 — description}

### From TP-{N.M.T+1}: {Test Suite Name} (if bundling multiple)
- [ ] {Test case 1}
- [ ] {Test case 2}

---

## 3. Acceptance Criteria

<!-- Pulled from Blueprint task cards. ALL must pass for DONE status. -->

- [ ] {Criterion 1 from BP-{N.M.T}}
- [ ] {Criterion 2 from BP-{N.M.T}}
- [ ] {Criterion 3 from BP-{N.M.T}}

---

## 4. Dependencies

<!-- Other Work Orders or conditions that must be satisfied before this WO starts. -->

| Dependency | Status | Notes |
|-----------|--------|-------|
| {WO-X.Y.Z-A or condition} | {DONE / IN-PROGRESS / PENDING} | {notes} |

---

## 5. Validation Checklist

<!-- Completed during VALIDATION phase. -->

- [ ] All acceptance criteria met
- [ ] All test cases pass
- [ ] No TODO/FIXME comments in implemented code
- [ ] No compiler/linter warnings
- [ ] Interface contracts match Engineering Spec exactly
- [ ] Traceability chain is valid (run `/trace-check`)

---

## 6. Validation Result

<!-- Filled in after validation. -->

**Result:** {DONE / FAILED}
**Validated by:** {Name/agent}
**Date:** {YYYY-MM-DD}

### If FAILED:
- **Reason:** {Why it failed}
- **Failed criteria:** {Which acceptance criteria were not met}
- **Next WO:** WO-{N.M.T}-{X+1} (suffix incremented)

### If DONE:
- **Archive to:** `WorkOrders/_Archive/WO-{N.M.T}-{X}.md`
