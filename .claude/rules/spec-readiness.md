<!-- AGENT INSTRUCTION: This rule guides spec creation and traceability.
     It documents both authoring paths, the traceability ID system, and
     the document creation sequence. It replaces the Mission Lock's role
     as the "what should I do next?" guide for spec work.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# Spec Readiness & Traceability Guide

*Intent: Ensures specs are complete and frozen before coding begins. Guides agents through the document stack and traceability system.*

## Authoring Paths

Two paths exist for product specification. Both produce the same downstream artifacts.

### Path A — Collaborative (Nathan + Claude)
1. Create PVD from `Specs/TEMPLATE_PVD.md`
2. Iterate until Nathan approves → Status: FROZEN
3. Continue to Engineering Spec

### Path B — Autonomous (Orchestration Engine)
1. Create Product Brief from `Specs/TEMPLATE_Product_Brief.md`
2. Review → Go/No-Go decision
3. If Go: Create PRD from `Specs/TEMPLATE_PRD.md`
4. Review → Status: FROZEN
5. Continue to Engineering Spec

The spec-gate hook accepts either path: a frozen PVD, or both a frozen Product Brief and frozen PRD.

## Document Creation Sequence

Create documents in this order. Each must be FROZEN before the next begins.

1. **PVD** (or Product Brief + PRD) → Assign PVD-N identifiers
2. **Engineering Spec** → Assign ES-N.M identifiers (trace to PVD-N)
3. **UX Spec** (if project has UI) → Assign UX-N.M identifiers (trace to PVD-N)
4. **Blueprint** → Assign BP-N.M.T identifiers (trace to ES-N.M)
5. **Testing Plans** → Assign TP-N.M.T identifiers (mirror BP-N.M.T)
6. **Gap Tracker** → Initialize tier structure
7. **Decision Record** → Log any decisions made during spec phase

After all frozen specs exist, execution begins via Work Orders.

## UX Spec Guidance

The UX Spec is **required for projects with a user interface** and **omitted for backend/API/CLI projects**.

When starting implementation work on a new project:
1. Check if a UX Spec exists
2. If not, ask Nathan: "Does this project have a user interface?"
3. If yes → create UX Spec from template before proceeding to Blueprint
4. If no → note "UX Spec: N/A" and proceed

The spec-gate hook does NOT enforce UX Spec presence (it's conditional), but the trace-check skill will note its absence as a warning for UI projects.

## Traceability ID System

| Prefix | Document | Format | Example | Traces To |
|--------|----------|--------|---------|-----------|
| PVD | Product Vision / PRD | PVD-N | PVD-3 | (root) |
| ES | Engineering Spec | ES-N.M | ES-3.2 | PVD-N |
| UX | UX Spec | UX-N.M | UX-3.1 | PVD-N |
| BP | Blueprint | BP-N.M.T | BP-3.2.4 | ES-N.M |
| TP | Testing Plans | TP-N.M.T | TP-3.2.4 | BP-N.M.T (mirror) |
| WO | Work Order | WO-N.M.T-X | WO-3.2.4-A | BP-N.M.T |
| DR | Decision Record | DR-NNN | DR-007 | (flat sequential) |
| GT | Gap Tracker | GT-TN-NNN | GT-T2-003 | (flat per tier) |

### Reading a Chain

```
WO-3.2.4-A  →  Work Order A for Blueprint task 3.2.4
BP-3.2.4    →  Task 4 under ES module 3.2
ES-3.2      →  Module 2 under PVD feature 3
PVD-3       →  Feature 3
```

The "3" in every ID tells you which PVD feature justifies the work.

## Run /trace-check

After creating or updating any spec, run `/trace-check` to:
- Validate all traceability chains
- Update the Work Ledger
- Surface orphans, gaps, and missing test mirrors
