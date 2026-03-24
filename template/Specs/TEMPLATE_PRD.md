<!-- TEMPLATE: Product Requirements Document (PRD)
     The PRD captures detailed requirements for the separate authoring path.
     It references the Product Brief for strategic context and adds the full
     feature specifications, user stories, and acceptance criteria.

     Use this when: Product Brief has been approved (Go decision).
     For the collaborative path, use the PVD template instead.

     USAGE:
     1. Ensure Product Brief exists and is FROZEN
     2. Copy this file to: Specs/{Abbrev}_PRD_DRAFT.md
     3. Replace all {placeholders} with real values
     4. Assign PVD-N identifiers to each feature (same IDs used in PVD path)
     5. Change Status to FROZEN and rename: {Abbrev}_PRD_v1.md
     6. Proceed to Engineering Spec

     TRACEABILITY: PVD-N identifiers assigned here are the ROOT of all
     traceability chains, same as in the PVD path. -->

# {ProjectName} — Product Requirements Document

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **References** | Product Brief: `Specs/{Abbrev}_Product_Brief.md` |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## Document Hierarchy

| # | Document | Status | Location |
|---|----------|--------|----------|
| 1a | Product Brief | FROZEN | `Specs/{Abbrev}_Product_Brief.md` |
| 1b | **PRD** (this document) | {DRAFT/FROZEN} | `Specs/{Abbrev}_PRD_v{N}.md` |
| 2 | Engineering Spec | {status} | `Specs/{Abbrev}_Engineering_Spec_v{N}.md` |
| 3 | UX Spec | {status / N/A} | `Specs/{Abbrev}_UX_Spec_v{N}.md` |
| 4 | Blueprint | {status} | `Specs/{Abbrev}_Blueprint_v{N}.md` |
| 5 | Testing Plans | {status} | `Testing/{Abbrev}_Testing_Plans_v{N}.md` |
| 6 | Gap Tracker | INITIALIZED | `Specs/gap_tracker.md` |
| 7 | Decision Record | LIVING | `Specs/{Abbrev}_Decision_Record.md` |

---

## 1. Product Overview

{Expand on the Product Brief's value proposition. What does the full product look like? End-to-end user experience in 2-3 paragraphs.}

---

## 2. Target Users

### Primary Persona
- **Name/Archetype:** {e.g., "Solo Developer Dave"}
- **Demographics:** {age range, role, technical level}
- **Goals:** {what they're trying to accomplish}
- **Pain points:** {specific frustrations with current solutions}
- **Context of use:** {when, where, how they'll use this product}

### Secondary Personas
{Additional user types, if any. Same format but briefer.}

---

## 3. Feature Specifications

<!-- Assign PVD-N identifiers sequentially. Same ID system as PVD path.
     Tag each feature as MVP or POST-MVP. -->

### PVD-1: {Feature Name}
- **Phase:** MVP / POST-MVP
- **Description:** {What this feature does from the user's perspective}
- **User Stories:**
  - As a {user type}, I want to {action} so that {benefit}
  - As a {user type}, I want to {action} so that {benefit}
- **Acceptance Criteria:**
  - [ ] {Testable criterion 1}
  - [ ] {Testable criterion 2}
  - [ ] {Testable criterion 3}
- **Priority:** {Must-have / Should-have / Nice-to-have}

### PVD-2: {Feature Name}
- **Phase:** MVP / POST-MVP
- **Description:** {What this feature does}
- **User Stories:**
  - As a {user type}, I want to {action} so that {benefit}
- **Acceptance Criteria:**
  - [ ] {Testable criterion 1}
  - [ ] {Testable criterion 2}
- **Priority:** {Must-have / Should-have / Nice-to-have}

### PVD-3: {Feature Name}
{Continue pattern for all features...}

---

## 4. User Flows

### Flow 1: {Flow Name}
1. {Step 1}
2. {Step 2}
3. {Step 3}
- **Happy path:** {expected outcome}
- **Error case:** {what happens when something goes wrong}

### Flow 2: {Flow Name}
1. {Step 1}
2. {Step 2}

---

## 5. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| {Metric 1} | {Target value} | {How measured} |
| {Metric 2} | {Target value} | {How measured} |

---

## 6. Constraints & Assumptions

### Constraints
- {Technical constraint — e.g., "Must run on iOS 16+"}
- {Business constraint — e.g., "Launch before Q3 2026"}

### Assumptions
- {Assumption 1 — and what happens if it's wrong}
- {Assumption 2}

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial requirements | {Author} |
