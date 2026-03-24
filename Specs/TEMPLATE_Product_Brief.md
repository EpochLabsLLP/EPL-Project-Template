<!-- TEMPLATE: Product Brief (Separate Authoring Path)
     The Product Brief is a lightweight "should we spec this?" gate.
     Use this for the autonomous path (Orchestration Engine) where a
     cheap Go/No-Go decision precedes the full PRD investment.

     For the collaborative path (Nathan + Claude), use the PVD template
     instead — it combines Brief + PRD into a single document.

     USAGE:
     1. Copy this file to: Specs/{Abbrev}_Product_Brief.md
     2. Replace all {placeholders} with real values
     3. Present for Go/No-Go decision
     4. If Go: proceed to PRD (TEMPLATE_PRD.md)
     5. If No-Go: archive to Specs/_Archive/
     6. Change Status to FROZEN after approval

     TRACEABILITY: Product Brief + PRD together serve the same role as PVD.
     PVD-N identifiers are assigned in the PRD, not here. -->

# {ProjectName} — Product Brief

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## 1. Problem Hypothesis

{1-2 paragraphs: What problem are we solving? Who has this problem? How do we know it's real? What's the cost of the problem remaining unsolved?}

---

## 2. Target User Sketch

{Who is the primary user? Be specific enough to evaluate feasibility, but this isn't the full persona — that comes in the PRD.}

- **Who:** {description}
- **Context:** {when/where do they encounter this problem?}
- **Current workaround:** {how do they solve it today?}

---

## 3. Market Opportunity

{Is this market big enough to matter? Growing or shrinking? Any timing factors?}

- **Market size estimate:** {TAM/SAM rough numbers}
- **Growth trajectory:** {growing/stable/shrinking}
- **Timing factor:** {why now? what's changed?}

---

## 4. Value Proposition

{One paragraph: What does this product do for the user that nothing else does? Why would they switch from their current solution?}

---

## 5. Key Risks

{What could kill this product? List the top 3-5 risks.}

1. {Risk 1 — and why it might be fatal}
2. {Risk 2}
3. {Risk 3}

---

## 6. Go/No-Go Decision

| Criterion | Assessment |
|-----------|------------|
| Problem is real and validated | {Yes/No/Needs research} |
| Market is large enough | {Yes/No/Needs research} |
| We have a defensible angle | {Yes/No/Uncertain} |
| Aligns with Epoch Labs strategy | {Yes/No} |
| Technical feasibility is reasonable | {Yes/No/Needs spike} |

**Decision:** {GO / NO-GO / NEEDS MORE RESEARCH}

**Decision made by:** {Name}
**Date:** {YYYY-MM-DD}

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial brief | {Author} |
