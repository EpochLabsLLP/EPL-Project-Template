<!-- AGENT INSTRUCTION: This is the consolidated Definition of Done reference.
     It defines completion criteria at every level: Work Order, Module, Feature,
     Wave, and Release. When unsure if something is "done," check here first.

     THIS FILE IS ALWAYS LOADED (no path scope). It survives compaction.
     It is the single source of truth for what "done" means. -->

# Definition of Done — Quick Reference

*Intent: Agents must cross-reference CLAUDE.md, quality-gates.md, execution-protocol.md, and individual templates to understand "done." This card consolidates all completion criteria into one authoritative reference. Check here first.*

## Work Order → DONE

- [ ] All acceptance criteria met (GIVEN/WHEN/THEN — each verified and recorded)
- [ ] `/code-review` PASS (output recorded in WO Validation Evidence)
- [ ] `/module-complete` 7/7 gates (if this WO completes a module)
- [ ] `/integration-logic` WIRED (if this is an INTEGRATION task)
- [ ] All tests passing (unit + E2E if applicable)
- [ ] Validation Evidence section fully completed in WO file (actual output, not just "PASS")
- [ ] One clean commit with WO ID in message
- [ ] WO file updated: Status → DONE, Validation Result filled
- [ ] WO archived to `WorkOrders/_Archive/`

## Module → Complete

- [ ] All WOs for this module have status DONE
- [ ] 7 quality gates passed (`/module-complete` output clean)
  - Gate 1: No stubs (`grep -rn` returns 0 results for stub patterns)
  - Gate 2: Tests exist for all public methods (coverage >= module target in ES)
  - Gate 3: No TODO/FIXME/HACK/XXX in source (all deferred to Gap Tracker)
  - Gate 4: No GPL dependencies (permissive licenses only)
  - Gate 5: Clean build (0 warnings)
  - Gate 6: Performance budget met (actual vs ES target)
  - Gate 7: Integration verified (WIRED via `/integration-logic`)
- [ ] Entry points verified (if module has external triggers per ES):
  - Handler registration confirmed via grep of bootstrap/entry point
  - Transport-level happy path test exists and passes
  - Transport-level error path test exists and passes
- [ ] Per-module Done Criteria in Engineering Spec all checked off

## Feature (PVD-N) → Complete

- [ ] All ES modules for this feature have completed modules (above)
- [ ] All rows in Module Integration Matrix for this feature report WIRED
- [ ] E2E test scenarios pass through actual transport layer
- [ ] User can complete the full feature journey end-to-end
  (entry → processing → output → persistence → confirmation)
- [ ] `/feature-complete PVD-N` reports COMPLETE
- [ ] Gap Tracker: Tier 0 empty, Tier 1 empty for this feature

## Wave → Complete

- [ ] All BP tasks in this wave have DONE Work Orders
- [ ] All INTEGRATION-type tasks report WIRED
- [ ] Wave's E2E_VALIDATION capstone task passed
- [ ] `/trace-check` reports CLEAN (no orphans, no gaps, no broken chains)
- [ ] Gap Tracker: Tier 0 empty, Tier 1 empty
- [ ] Gap Tracker: Any Tier 2 items explicitly deferred with Decision Record entry
- [ ] `/wave-complete <wave-number>` reports PASS
- [ ] Session summary written with wave completion noted

## Release → Ready

- [ ] All Blueprint waves complete (Wave 0 through Final Wave)
- [ ] All PVD features complete (`/feature-complete` for each)
- [ ] Gap Tracker: Tier 0 empty, Tier 1 empty, Tier 2 empty
- [ ] All performance budgets met across all modules
- [ ] Security review complete (`/security-review` for sensitive modules)
- [ ] No stubs, TODOs, FIXMEs, or HACKs in entire codebase
- [ ] All traceability chains valid (`/trace-check` CLEAN)
- [ ] All integration points WIRED (`/integration-logic all` clean)
- [ ] Final build succeeds with 0 warnings
- [ ] Gold Rush Doctrine check: Does this meet or exceed the best existing alternative?

## Gap Tracker — Phase Closure Rules

These rules are enforced by `/wave-complete` and `/feature-complete`. Violations block PASS.

| Phase Transition | Tier 0 (Critical) | Tier 1 (Functional) | Tier 2 (Quality) | Tier 3 (Enhancement) |
|-----------------|-------------------|--------------------|--------------------|---------------------|
| Wave complete | MUST be empty | MUST be empty | May defer with approval* | Expected to have items |
| Feature complete | MUST be empty | MUST be empty | May defer with approval* | Expected to have items |
| Release ready | MUST be empty | MUST be empty | MUST be empty | May defer with approval* |

*Deferral requires: Nathan's explicit approval + Decision Record entry with rationale + target phase for resolution.

### Tier State Verification

Before any phase transition:
1. Count items at each tier
2. Tier 0 > 0: **BLOCK.** Cannot proceed.
3. Tier 1 > 0: **BLOCK.** Cannot proceed.
4. Tier 2 > 0 and transition is release: **BLOCK.** Cannot proceed.
5. Tier 2 > 0 and transition is wave/feature: **WARN.** Require deferral record.
