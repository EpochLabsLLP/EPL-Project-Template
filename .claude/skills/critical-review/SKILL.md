---
name: critical-review
description: Adversarial self-review for spec fidelity. Forces you to re-read the spec and compare it line-by-line against your implementation. Different from /code-review (which checks coding quality) — this checks whether you actually built what the spec says, completely, not just structurally. Required before /module-complete.
argument-hint: <module>
user-invocable: true
---

# critical-review

Adversarial self-review. You are not checking code quality — `/code-review` does that. You are checking whether **what you built actually delivers everything the spec describes**, completely, with no gaps, no shortcuts, and no hollow implementations that pass automated checks but aren't fully fleshed out.

## Why This Exists

Agents routinely pass all 7 quality gates and still produce incomplete work. The gates check for the absence of bad things (no stubs, no TODOs, tests exist) but do not verify the presence of good things (full spec coverage, edge cases handled, behavior matches the spec's intent — not just its surface structure).

The pattern: an agent marks work as DONE, `/module-complete` reports 7/7 PASS, and when forced to go back and critically review, the agent discovers significant gaps it should have caught the first time. Functions that technically exist but don't fully implement the described behavior. Integration points that are wired but don't handle all the cases in the spec. Tests that pass but don't actually exercise the scenarios the Testing Plans describe.

**This skill exists to force the moment of honest confrontation before Nathan has to.**

## When to Use

- **MANDATORY** before `/module-complete` — this is a prerequisite, not optional
- After completing implementation of any module
- When Nathan asks you to "go back and critically review"
- When you suspect your own work might have gaps

## How to Invoke

```
/critical-review <module>
```

Where `<module>` is the ES module identifier (e.g., `ES-1.2`).

## Execution

### Step 0: Set Your Posture

You are not here to confirm your work is good. You are here to find what's wrong with it. Adopt the posture of a skeptical reviewer who assumes the implementation is incomplete until proven otherwise. Every claim of completeness requires evidence. "I believe this is done" is not evidence.

---

### Step 1: Load the Spec (Full, Not Summary)

Read the **complete** Engineering Spec section for this module. Not a summary. Not what you remember. The actual text.

For each of these, read the full content:
1. The ES module section (requirements, interface contracts, behavior descriptions)
2. The corresponding Blueprint task card(s) (acceptance criteria — every GIVEN/WHEN/THEN)
3. The corresponding Testing Plans section (test scenarios, edge cases, coverage targets)
4. Any integration contracts involving this module (Module Integration Matrix rows)

**Do not skip this step. Do not rely on memory. Re-read the actual files.**

---

### Step 2: Section-by-Section Confrontation

For each requirement, interface contract, behavior description, and acceptance criterion in the spec:

1. **Quote the spec requirement** (exact text or paraphrase with section reference)
2. **Locate the implementation** (file path + line number or function name)
3. **Assess fidelity** — Does the implementation fully deliver what the spec describes?
   - **FULL** — Implementation covers the complete described behavior, including edge cases
   - **PARTIAL** — Implementation exists but is missing aspects described in the spec
   - **SURFACE** — Implementation structurally exists (function signature, basic flow) but lacks the depth or completeness the spec describes. This is the most dangerous status — it passes automated checks while being hollow.
   - **MISSING** — No implementation found for this spec requirement

For each PARTIAL or SURFACE finding, describe specifically what's missing. Not "needs more work" — what behavior, edge case, or integration path is absent.

---

### Step 3: Test Fidelity Check

For each test scenario in the Testing Plans:

1. **Quote the test scenario** (TP reference + description)
2. **Find the corresponding test** (file path + test name)
3. **Assess coverage:**
   - **COVERED** — Test exists and exercises the described scenario meaningfully
   - **SHALLOW** — Test exists but only checks the happy path / basic assertion, not the full scenario described in the TP
   - **MISSING** — No test found for this scenario

A test that asserts `expect(result).toBeTruthy()` for a scenario that describes specific behavioral requirements is SHALLOW, not COVERED.

---

### Step 4: Integration Fidelity Check

If this module has integration points (check the Module Integration Matrix):

For each integration contract:
1. **Quote the integration requirement** (which modules, what data flows, what protocol)
2. **Trace the actual wiring** (follow the code path from source to destination)
3. **Assess completeness:**
   - **WIRED** — Full bidirectional contract honored, error paths handled
   - **PARTIAL** — Happy path works but error propagation, edge cases, or fallback behavior described in the spec is missing
   - **STRUCTURAL** — The import/call exists but the actual data transformation or protocol described in the spec isn't implemented

---

### Step 5: The Honest Question

Answer this question directly and honestly:

> **"If Nathan told me to go back and critically review this module, what would I find?"**

Write your answer. Do not soften it. Do not frame findings as minor. If there are gaps, they are gaps — the Gold Rush Doctrine says what ships is finished.

---

### Step 6: Report

```
=== CRITICAL REVIEW: {module} ===

## Spec Fidelity

| Spec Requirement | Location | Status | Gap (if any) |
|-----------------|----------|--------|--------------|
| {requirement} | {file:line} | FULL/PARTIAL/SURFACE/MISSING | {specific gap} |
| ... | ... | ... | ... |

## Test Fidelity

| Test Scenario | Test Location | Status | Gap (if any) |
|--------------|---------------|--------|--------------|
| {TP reference} | {file:test} | COVERED/SHALLOW/MISSING | {specific gap} |
| ... | ... | ... | ... |

## Integration Fidelity

| Integration | Code Path | Status | Gap (if any) |
|------------|-----------|--------|--------------|
| {ES-X.Y → ES-A.B} | {trace} | WIRED/PARTIAL/STRUCTURAL | {specific gap} |
| ... | ... | ... | ... |

## Honest Assessment
{Your answer to the Step 5 question}

## Verdict
- **FIDELITY: HIGH** — All requirements FULL, all tests COVERED, all integrations WIRED. Ready for /module-complete.
- **FIDELITY: GAPS FOUND** — {N} PARTIAL/SURFACE/SHALLOW/MISSING findings. List each. These must be fixed before /module-complete.
```

---

## Verdicts and What Happens Next

- **FIDELITY: HIGH** → Proceed to `/module-complete`. Record this verdict in the Work Order's Validation Evidence section.
- **FIDELITY: GAPS FOUND** → Fix every gap. Then re-run `/critical-review`. Do not proceed to `/module-complete` until the verdict is HIGH. Record all findings and fixes in the Work Order.

**`/module-complete` will FAIL if `/critical-review` has not been run or if the most recent verdict was not HIGH.** This is enforced by checking for the critical-review verdict in the Work Order's Validation Evidence section.

## What This Is NOT

- This is NOT `/code-review`. Code-review checks coding quality (error handling, security, patterns, readability). Critical-review checks spec fidelity (did you build what was specified, completely).
- This is NOT a checkbox exercise. If you find yourself writing "FULL" for every row without re-reading the spec, you are doing it wrong. The entire point is the confrontation between spec and implementation.
- This is NOT optional. It is a mandatory prerequisite for `/module-complete`, which is a mandatory prerequisite for marking a WO as DONE.
