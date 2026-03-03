<!-- TEMPLATE: Decision Record
     A living log of significant architectural, design, and product decisions.
     Captures the WHY behind decisions so agents (and humans) in future contexts
     don't re-litigate settled questions.

     USAGE:
     1. Copy this file to: Specs/{Abbrev}_Decision_Record.md
     2. Add entries as decisions are made throughout the project lifecycle
     3. This is a LIVING document — append only, never delete entries
     4. Superseded decisions are marked, not removed

     TRACEABILITY: DR-NNN uses flat sequential numbering.
     Decision Records can span multiple PVD features or ES modules.

     STATUS: LIVING — continuously appended. Never frozen. -->

# {ProjectName} — Decision Record

| Field | Value |
|-------|-------|
| **Status** | LIVING |
| **Created** | {YYYY-MM-DD} |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## How to Use This Document

- Add a new entry whenever a significant decision is made
- "Significant" = affects architecture, user experience, dependencies, or scope
- Never delete entries — mark superseded decisions with a reference to the replacement
- Each entry uses flat sequential numbering: DR-001, DR-002, DR-003...

---

## Decisions

### DR-001: {Decision Title}

| Field | Value |
|-------|-------|
| **Date** | {YYYY-MM-DD} |
| **Status** | Active / Superseded by DR-{NNN} |
| **Affects** | {PVD-N, ES-N.M, or "Project-wide"} |

**Context:** {What situation or problem prompted this decision? What constraints were in play?}

**Decision:** {What was decided?}

**Alternatives Considered:**
1. {Alternative 1} — {Why rejected: tradeoffs, risks, or shortcomings}
2. {Alternative 2} — {Why rejected}

**Consequences:** {What are the tradeoffs, risks, or implications of this decision? What does this commit us to? What does it prevent?}

---

### DR-002: {Decision Title}

| Field | Value |
|-------|-------|
| **Date** | {YYYY-MM-DD} |
| **Status** | Active / Superseded by DR-{NNN} |
| **Affects** | {scope} |

**Context:** {context}

**Decision:** {decision}

**Alternatives Considered:**
1. {Alternative 1} — {Why rejected}

**Consequences:** {consequences}

---

<!-- Continue adding entries as decisions are made.
     Keep numbering sequential: DR-003, DR-004, etc. -->
