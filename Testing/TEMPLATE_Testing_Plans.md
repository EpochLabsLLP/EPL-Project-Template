<!-- TEMPLATE: Testing Plans
     Per-module test cases, coverage targets, and integration scenarios.
     Tests are the enforcement mechanism for specifications — they verify
     that what was built matches what was specified.

     USAGE:
     1. Ensure PVD, Engineering Spec, and Blueprint are FROZEN
     2. Copy this file to: Testing/{Abbrev}_Testing_Plans_DRAFT.md
     3. Replace all {placeholders} with real values
     4. Assign TP-N.M.T identifiers mirroring BP-N.M.T from the Blueprint
     5. Change Status to FROZEN and rename: {Abbrev}_Testing_Plans_v1.md
     6. Proceed to execution (Work Orders)

     TRACEABILITY: TP-N.M.T mirrors BP-N.M.T.
     Example: TP-3.2.4 contains tests for Blueprint task BP-3.2.4.
     Every Blueprint task MUST have a corresponding Testing Plan entry. -->

# {ProjectName} — Testing Plans

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **Implements** | `Specs/{Abbrev}_Blueprint_v{N}.md` |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## 1. Testing Philosophy & Pyramid

{Describe the testing approach for this project.}

### Test Pyramid Distribution
```
         /  E2E  \        ~5%  — Critical user journeys only
        /----------\
       / Integration \    ~15% — Module boundaries and contracts
      /----------------\
     /    Unit Tests     \  ~80% — Individual functions and methods
    /--------------------\
```

### Guiding Principles
1. **Tests prove specs.** Every test traces to an acceptance criterion in the Blueprint.
2. **Unit tests are exhaustive.** Cover all public methods, edge cases, and error paths.
3. **Integration tests verify contracts.** Focus on module boundaries, not internal logic.
4. **E2E tests verify journeys.** Only the most critical user flows, not comprehensive coverage.

---

## 2. Test Infrastructure & Tools

| Category | Tool | Rationale |
|----------|------|-----------|
| Unit Testing | {e.g., pytest, Jest, JUnit} | {why} |
| Integration Testing | {tool} | {why} |
| E2E Testing | {e.g., Playwright, Cypress} | {why} |
| Mocking | {e.g., unittest.mock, jest.mock} | {why} |
| Coverage | {e.g., coverage.py, istanbul} | {why} |
| Performance | {e.g., k6, locust} | {why} |

---

## 3. Per-Module Unit Test Specs

<!-- TP-N.M.T mirrors BP-N.M.T. Each entry defines:
     - What to test (derived from Blueprint acceptance criteria)
     - Test cases (happy path, edge cases, error cases)
     - Expected coverage -->

### TP-1.1.1: {Test Suite Name} (mirrors BP-1.1.1)
- **Module:** ES-1.1
- **Tests acceptance criteria from:** BP-1.1.1
- **Test Cases:**
  - [ ] **Happy path:** {Test description — input, expected output}
  - [ ] **Edge case:** {Test description}
  - [ ] **Error case:** {Test description — invalid input, expected error}
  - [ ] **Boundary:** {Test description — limits, overflow, empty}
- **Coverage target:** {e.g., 95%}

### TP-1.1.2: {Test Suite Name} (mirrors BP-1.1.2)
- **Module:** ES-1.1
- **Tests acceptance criteria from:** BP-1.1.2
- **Test Cases:**
  - [ ] **Happy path:** {Test description}
  - [ ] **Edge case:** {Test description}
  - [ ] **Error case:** {Test description}
- **Coverage target:** {e.g., 90%}

### TP-2.1.1: {Test Suite Name} (mirrors BP-2.1.1)
- **Module:** ES-2.1
{Continue pattern for all Blueprint tasks...}

---

## 4. Integration Test Scenarios

{Tests that verify module boundaries and interface contracts.}

### Integration: ES-1.1 ↔ ES-1.2
- **Contract tested:** {Reference frozen contract from Engineering Spec}
- **Scenarios:**
  - [ ] {Scenario 1: Normal data flow between modules}
  - [ ] {Scenario 2: Error propagation across boundary}
  - [ ] {Scenario 3: Edge case at interface}

### Integration: ES-2.1 ↔ ES-1.2
- **Contract tested:** {contract reference}
- **Scenarios:**
  - [ ] {Scenario 1}
  - [ ] {Scenario 2}

---

## 5. Performance Testing

| Test | Module | Metric | Target | Method |
|------|--------|--------|--------|--------|
| {Test name} | ES-{N.M} | {e.g., Response time p95} | {e.g., < 200ms} | {tool/approach} |
| {Test name} | ES-{N.M} | {e.g., Throughput} | {e.g., > 1000 req/s} | {tool/approach} |

---

## 6. Security Testing

| Test | Module | OWASP Category | Method |
|------|--------|---------------|--------|
| {Test name} | ES-{N.M} | {e.g., A01: Broken Access Control} | {approach} |
| {Test name} | ES-{N.M} | {e.g., A03: Injection} | {approach} |

---

## 7. Compatibility Testing

{If applicable — browser compatibility, OS compatibility, device testing.}

| Target | Versions | Priority |
|--------|----------|----------|
| {e.g., Chrome} | {versions} | {Must-pass / Should-pass} |
| {e.g., iOS Safari} | {versions} | {Must-pass / Should-pass} |

---

## 8. Accessibility Testing

| Requirement | Standard | Method |
|-------------|----------|--------|
| Keyboard navigation | WCAG 2.1 AA | {manual / automated} |
| Screen reader | WCAG 2.1 AA | {manual with NVDA/VoiceOver} |
| Color contrast | WCAG 2.1 AA | {automated scan} |
| Focus management | WCAG 2.1 AA | {manual} |

---

## 9. Coverage Targets

| Module Tier | Coverage Target | Rationale |
|------------|----------------|-----------|
| Foundation (ES-1.x) | 95% | {Critical infrastructure — failures cascade} |
| Core (ES-2.x, ES-3.x) | 90% | {Primary functionality — must be reliable} |
| UI (ES-{N}.x) | 80% | {Interaction-heavy — some paths best tested manually} |

---

## 10. Regression Strategy

{How do we prevent regressions as new code is added?}

- **Pre-commit:** {what runs before every commit}
- **CI pipeline:** {what runs on every push}
- **Pre-merge:** {what must pass before PR merges}

---

## 11. CI/CD Integration

{How tests integrate with the build pipeline.}

```
{CI pipeline stages}

Example:
  Push → Lint → Unit Tests → Integration Tests → Build → E2E Tests → Deploy (staging)
```

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial testing plans | {Author} |
