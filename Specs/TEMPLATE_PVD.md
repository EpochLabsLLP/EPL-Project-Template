<!-- TEMPLATE: Product Vision Document (PVD)
     The PVD captures the complete "what and why" of the product.
     It combines strategic context (Product Brief) and detailed requirements (PRD)
     into a single document. Use this template for the collaborative authoring path
     (Nathan + Claude). For the autonomous path, use Product Brief + PRD instead.

     USAGE:
     1. Copy this file to: Specs/{Abbrev}_PVD_DRAFT.md
     2. Replace all {placeholders} with real values
     3. Assign PVD-N identifiers to each feature
     4. Iterate with Nathan until all sections are complete
     5. Change Status to FROZEN and rename: {Abbrev}_PVD_v1.md
     6. Proceed to Engineering Spec

     TRACEABILITY: PVD-N identifiers are the ROOT of all traceability chains.
     Every downstream artifact (ES, UX, BP, TP, WO) traces back to a PVD-N. -->

# {ProjectName} — Product Vision Document

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## Document Hierarchy

| # | Document | Status | Location |
|---|----------|--------|----------|
| 1 | **PVD** (this document) | {DRAFT/FROZEN} | `Specs/{Abbrev}_PVD_v{N}.md` |
| 2 | Engineering Spec | {status} | `Specs/{Abbrev}_Engineering_Spec_v{N}.md` |
| 3 | UX Spec | {status / N/A} | `Specs/{Abbrev}_UX_Spec_v{N}.md` |
| 4 | Blueprint | {status} | `Specs/{Abbrev}_Blueprint_v{N}.md` |
| 5 | Testing Plans | {status} | `Testing/{Abbrev}_Testing_Plans_v{N}.md` |
| 6 | Gap Tracker | INITIALIZED | `Specs/gap_tracker.md` |
| 7 | Decision Record | LIVING | `Specs/{Abbrev}_Decision_Record.md` |

---

## 1. Executive Summary

{2-3 paragraphs: What is this product? Who is it for? What problem does it solve? Why does it matter now? What is our competitive advantage?}

---

## 2. Vision & Mission

**Vision:** {One sentence — the aspirational future state this product enables.}

**Mission:** {One sentence — what this product does to move toward that vision.}

### Anti-Vision
{What does the world look like if we DON'T build this? What happens if we build it poorly? This section clarifies the stakes and prevents scope drift by naming what we're avoiding.}

---

## 3. Problem Statement

{Describe the problem from the user's perspective. Include:
- What pain points exist today?
- How are users currently solving this problem (or failing to)?
- Why existing solutions are inadequate
- What evidence supports this problem's existence and severity?}

---

## 4. Target Users & Market

### Primary Users
{Who are the primary users? Be specific — demographics, behaviors, technical sophistication, context of use.}

### Secondary Users
{Who else interacts with or benefits from this product? Administrators, API consumers, etc.}

### Market Opportunity
{Market size (TAM/SAM/SOM if applicable), growth trajectory, timing factors.}

---

## 5. Product Overview

{High-level product description — what does the user experience end-to-end? Think of this as the "elevator pitch" version, expanded to a few paragraphs.}

---

## 6. Feature Specifications

<!-- Assign PVD-N identifiers sequentially. These are the ROOT of all traceability.
     Tag each feature as MVP or POST-MVP. MVP features ship in the first release.
     POST-MVP features are planned but explicitly deferred. -->

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

### PVD-2: {Feature Name}
- **Phase:** MVP / POST-MVP
- **Description:** {What this feature does}
- **User Stories:**
  - As a {user type}, I want to {action} so that {benefit}
- **Acceptance Criteria:**
  - [ ] {Testable criterion 1}
  - [ ] {Testable criterion 2}

### PVD-3: {Feature Name}
{Continue pattern for all features...}

---

## 7. User Flows

{Describe the primary user journeys through the product. Include:
- Happy path flows (the expected, successful journey)
- Error/edge case flows (what happens when things go wrong)
- Entry/exit points

Use numbered steps, diagrams, or flowcharts as appropriate.}

### Flow 1: {Flow Name}
1. {Step 1}
2. {Step 2}
3. {Step 3}

### Flow 2: {Flow Name}
1. {Step 1}
2. {Step 2}

---

## 8. Economics & Business Model

### Revenue Model
{How does this product make money? Subscription, one-time purchase, freemium, usage-based, etc.}

### Pricing Strategy
{Pricing tiers, competitive positioning on price, willingness-to-pay assumptions.}

### Unit Economics
{Key metrics: CAC, LTV, margins, breakeven assumptions.}

---

## 9. Success Metrics

{How do we know this product is succeeding? Define measurable outcomes.}

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| {Metric 1} | {Target value} | {How measured} |
| {Metric 2} | {Target value} | {How measured} |
| {Metric 3} | {Target value} | {How measured} |

---

## 10. Competitive Analysis

| Competitor | Strengths | Weaknesses | Our Differentiation |
|-----------|-----------|------------|---------------------|
| {Competitor 1} | {strengths} | {weaknesses} | {how we're different/better} |
| {Competitor 2} | {strengths} | {weaknesses} | {how we're different/better} |

---

## 11. Risks & Mitigations

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| {Risk 1} | High/Med/Low | High/Med/Low | {How we address it} |
| {Risk 2} | High/Med/Low | High/Med/Low | {How we address it} |

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial draft | {Author} |
