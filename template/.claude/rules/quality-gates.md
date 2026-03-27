<!-- AGENT INSTRUCTION: These gates must ALL pass before any module can be marked complete.
     This is the "Definition of Done" for every module in the project.
     Do not skip gates. Do not mark a module complete with any gate failing.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# Quality Gates — Module Completion Criteria

*Intent: These gates prevent shipping incomplete work. Every gate addresses a specific failure mode observed in past projects.*

## Before Marking ANY Module Complete

1. **All interface contract methods are implemented with real logic (no stubs).**
   *Intent: Stubs create false confidence. Downstream modules call them expecting real behavior.*

2. **Unit tests cover all public methods.**
   *Intent: Untested code is unverified code. Tests are the proof that implementation matches spec.*

3. **No TODO/FIXME comments remain in the module.**
   *Intent: TODOs are deferred decisions. Resolve them now or explicitly defer to the gap tracker.*

4. **No GPL dependencies introduced.**
   *Intent: GPL viral licensing constrains Epoch Labs' commercial options. Apache 2.0, MIT, BSD only.*

5. **Compiles/builds without warnings.**
   *Intent: Warnings are future bugs. A clean build is the minimum quality bar.*

6. **Performance meets targets specified in the Engineering Spec.**
   *Intent: A feature that works but is too slow is a feature that doesn't work.*

7. **Integration points verified (if applicable).**
   *Intent: A module that works in isolation but fails when connected to its neighbors is not complete. Verify the wiring, not just the unit.*
   - Check the Engineering Spec's Module Integration Matrix for integration points involving this module.
   - If integration points exist, `/integration-logic` must have been run for each and reported WIRED.
   - If no integration points exist (standalone module), this gate is N/A.

## Verification Commands

Each gate has a concrete verification method. "No stubs" is unambiguous when backed by a grep pattern.

| Gate | Criterion | Verification | Pass Condition |
|------|-----------|-------------|----------------|
| 1 | No stubs | `grep -rn` for stub patterns (see below) in `src/`/`Code/` | 0 results |
| 2 | Tests exist | Cross-reference public method count with test count; run coverage tool | Coverage >= module target in ES |
| 3 | No deferred work | `grep -rn "TODO\|FIXME\|HACK\|XXX"` in `src/`/`Code/` | 0 results (all moved to Gap Tracker) |
| 4 | License compliance | `npx license-checker --onlyAllow "MIT;Apache-2.0;BSD"` or lang equivalent | 0 violations |
| 5 | Clean build | Build command with stderr captured; grep for warnings | 0 warnings |
| 6 | Performance met | Run perf test suite; compare actual metrics to ES performance budgets | All within budget |
| 7 | Integration verified | `/integration-logic <module>` | Verdict: WIRED |

### Stub Detection Patterns (Gate 1 — expanded)

The following patterns indicate incomplete implementation. ALL must return 0 results.

**JavaScript/TypeScript:**
- `throw new Error('Not implemented')` / `throw new Error('TODO')`
- `// TODO` / `// FIXME`
- `return null // placeholder`
- `() => {}` (empty arrow functions in non-test files)

**Python:**
- `raise NotImplementedError`
- `pass` (as sole function body)
- `# TODO` / `# FIXME`
- `return None  # placeholder`

**All languages:**
- `HACK` / `XXX` / `PLACEHOLDER` / `stub`
- `mock` (in non-test files — real implementations, not test mocks)

## How to Invoke

Run `/module-complete <module>` to verify all gates (Gates 1-7) against a specific module. The skill will check each gate and report pass/fail.
