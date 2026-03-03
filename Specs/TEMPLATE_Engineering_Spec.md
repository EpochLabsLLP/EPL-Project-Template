<!-- TEMPLATE: Engineering Spec
     Translates the PVD's "what" into a technical "how."
     Defines architecture, modules, interfaces, and performance budgets.

     USAGE:
     1. Ensure PVD (or Product Brief + PRD) is FROZEN
     2. Copy this file to: Specs/{Abbrev}_Engineering_Spec_DRAFT.md
     3. Replace all {placeholders} with real values
     4. Assign ES-N.M identifiers (N = PVD feature, M = module sequence)
     5. Define frozen interface contracts for every module boundary
     6. Change Status to FROZEN and rename: {Abbrev}_Engineering_Spec_v1.md
     7. Proceed to UX Spec (if UI project) or Blueprint

     TRACEABILITY: ES-N.M traces to PVD-N.
     Example: ES-3.2 = Module #2 implementing PVD Feature #3. -->

# {ProjectName} — Engineering Spec

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **Implements** | `Specs/{Abbrev}_PVD_v{N}.md` (or PRD) |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## 1. System Architecture Overview

{High-level architecture description. Include:
- System boundaries (what's in scope vs external)
- Major subsystems and their responsibilities
- Data flow between subsystems
- Deployment topology}

### Architecture Diagram
```
{ASCII architecture diagram showing major components and their relationships}
```

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| {Language/Runtime} | {choice} | {why} |
| {Framework} | {choice} | {why} |
| {Database} | {choice} | {why} |
| {Infrastructure} | {choice} | {why} |
| {Build/CI} | {choice} | {why} |
| {Testing} | {choice, e.g., pytest, Jest, JUnit} | {why} |

---

## 3. Module Dependency Graph

```
{ASCII dependency graph showing which modules depend on which}

Example:
  PVD-1: Authentication
    ES-1.1: Auth Core ──────► ES-1.2: Session Manager
    ES-1.3: OAuth Provider ──► ES-1.1

  PVD-2: Dashboard
    ES-2.1: Metrics API ────► ES-1.2 (cross-feature dependency)
    ES-2.2: Dashboard UI ───► ES-2.1
```

---

## 4. Database Schema

{If applicable. Include entity relationships, key fields, indexes, and constraints.}

### Tables / Collections

#### {Table/Collection Name}
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| {field} | {type} | {PK/FK/NOT NULL/etc.} | {notes} |

---

## 5. Module Specifications

<!-- Each module gets an ES-N.M identifier.
     N = PVD feature number, M = module sequence within that feature.
     Every module MUST have: purpose, interfaces, dependencies, performance budget. -->

### ES-1.1: {Module Name}
- **Implements:** PVD-1
- **Purpose:** {What this module does}
- **Responsibilities:**
  - {Responsibility 1}
  - {Responsibility 2}
- **Dependencies:** {Other modules this depends on}
- **Performance Budget:** {Latency, throughput, memory constraints}

### ES-1.2: {Module Name}
- **Implements:** PVD-1
- **Purpose:** {What this module does}
- **Responsibilities:**
  - {Responsibility 1}
- **Dependencies:** {ES-1.1}
- **Performance Budget:** {constraints}

### ES-2.1: {Module Name}
- **Implements:** PVD-2
{Continue pattern for all modules...}

---

## 6. Module Integration Matrix

{Which modules talk to which, and how?}

| Source Module | Target Module | Integration Type | Data Exchanged |
|--------------|---------------|-----------------|----------------|
| ES-1.1 | ES-1.2 | {direct call / event / API} | {what data} |
| ES-2.1 | ES-1.2 | {direct call / event / API} | {what data} |

---

## 7. Frozen Interface Contracts

<!-- CRITICAL: These are the load-bearing agreements between modules.
     Each contract specifies exact function signatures, data types,
     error contracts, and behavioral guarantees. Once frozen, changes
     require formal revision with Nathan's approval. -->

### Contract: ES-1.1 ↔ ES-1.2
```
{Exact interface definition in the project's language}

Example (TypeScript):
interface AuthService {
  authenticate(credentials: Credentials): Promise<AuthResult>;
  validateToken(token: string): Promise<TokenPayload | null>;
  revokeToken(token: string): Promise<void>;
}

type AuthResult = { success: true; token: string } | { success: false; error: AuthError };
type AuthError = 'INVALID_CREDENTIALS' | 'ACCOUNT_LOCKED' | 'RATE_LIMITED';
```

### Contract: ES-2.1 ↔ ES-1.2
```
{Interface definition}
```

---

## 8. External API Contracts

{If the system exposes or consumes external APIs.}

### Exposed APIs

#### `{METHOD} {/endpoint}`
- **Purpose:** {what it does}
- **Auth:** {auth mechanism}
- **Request:** {body/params schema}
- **Response:** {response schema}
- **Errors:** {error codes and meanings}

### Consumed APIs

#### {External Service Name}
- **Base URL:** {url}
- **Auth:** {mechanism}
- **Rate Limits:** {limits}
- **Endpoints Used:** {list}

---

## 9. Infrastructure Configuration

{Deployment targets, environment configuration, secrets management, CI/CD pipeline.}

---

## 10. Performance Budgets

| Module | Metric | Target | Measurement |
|--------|--------|--------|-------------|
| ES-1.1 | {e.g., Auth latency} | {e.g., < 200ms p95} | {how measured} |
| ES-2.1 | {e.g., Dashboard load} | {e.g., < 1s p95} | {how measured} |

---

## 11. Security Model

{Authentication mechanism, authorization model, data protection, secrets management, input validation strategy, OWASP considerations.}

---

## 12. Error Handling & Observability

### Error Strategy
{How errors propagate across module boundaries. Error categorization (retryable vs fatal). User-facing error messages vs internal logging.}

### Observability
{Logging strategy, metrics collection, tracing, alerting thresholds.}

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial architecture | {Author} |
