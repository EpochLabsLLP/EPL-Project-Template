---
name: deferred-audit
description: Audit all specs for deferred, follow-up, and future-work items that were never picked up by subsequent phases. Finds orphaned commitments buried in completed specs. Use at phase boundaries, during planning, or when session hooks report orphaned items.
user-invocable: true
---

# deferred-audit

Scans all spec files for deferred and follow-up items, then cross-references each against downstream specs, Work Orders, and the Gap Tracker to determine whether the item was ever picked up. Orphaned items — commitments that silently disappeared — are surfaced for action.

## Why This Exists

Every phase produces specs with "Follow-Up Tasks", "Deferred", or "Future Work" sections. Those items are promises to do work later. But without a systematic audit, they disappear into completed specs that nobody re-reads. This skill prevents the pattern of discovering — too late — that critical infrastructure was specced but never scheduled.

## When to Use

- At the **start of a new phase** — verify nothing was left behind from prior phases
- When session hooks report **orphaned deferred items** — dig into the details
- During **phase planning** — ensure the new phase picks up all outstanding commitments
- When something seems missing — "wasn't this supposed to be built?" → run the audit
- Periodically as a **governance health check** alongside `/trace-check` and `/governance-health`

## How to Invoke

```
/deferred-audit
```

## Execution

### Step 1: Run the Scanner

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/deferred-audit/scripts/scan_deferred.py" "$CLAUDE_PROJECT_DIR"
```

This will:
- Scan all spec files in `Specs/` and `Testing/` for deferred-item sections
- Extract individual items from bullet lists, numbered lists, and tables
- Cross-reference each item against subsequent specs, Work Orders, Gap Tracker, and Decision Records
- Generate `Specs/Deferred_Ledger.md` with full results
- Print a summary to stdout

### Step 2: Read and Present the Ledger

Read `Specs/Deferred_Ledger.md` and present the findings to the user.

Focus on **orphaned items** — these are the ones that need action:

For each orphaned item, explain:
1. **What it is:** The deferred item text and which spec it came from
2. **What section it was in:** e.g., "Follow-Up Tasks", "Deferred to Phase F2+"
3. **Why it matters:** Brief assessment of the item's importance to the overall system
4. **Recommended action:** One of:
   - Add to Gap Tracker at the appropriate tier (Tier 0 if it blocks other work, Tier 1 if functional, Tier 2 if quality, Tier 3 if enhancement)
   - Create a Work Order in the current phase
   - Record a formal deferral via Decision Record (with rationale for why it's OK to defer)

### Step 3: Recommend a Path Forward

After presenting orphaned items, recommend:

- **If 0 orphaned items:** Report clean status. No action needed.
- **If 1-3 orphaned items:** Recommend addressing each individually. Suggest specific Gap Tracker entries or WOs.
- **If 4+ orphaned items:** This suggests a systemic gap. Recommend a dedicated remediation wave or phase to address accumulated debt before proceeding with new feature work. Reference the Gold Rush Doctrine — shipping on top of missing infrastructure is shipping something unfinished under the hood.

## Output Format

```
=== DEFERRED ITEMS AUDIT ===
Scanned: N spec files with deferred sections
Total items: N
  Resolved:     N
  Acknowledged: N
  Done:         N
  ORPHANED:     N

Ledger written to: Specs/Deferred_Ledger.md

[Detailed analysis of orphaned items follows]
```

## What the Scanner Detects

The scanner looks for markdown sections with headers matching these patterns:
- Follow-Up Tasks / Follow-Up / Follow Up
- Deferred / Deferrals
- Future Work / Future Implementation
- Post-Phase / Post-Phase N
- Remaining Work / Remaining Items
- Not Yet Done / Not Yet Implemented
- Parking Lot / Backlog
- Open Items / Pending Items / Outstanding Items
- Carry Over / To Be Done

Items marked as `[x]` (checked) in their source are classified as DONE and excluded from the orphan report.

## Status Classifications

| Status | Meaning | Action |
|--------|---------|--------|
| **ORPHANED** | Item was deferred but never picked up by any downstream artifact | Must be addressed — add to Gap Tracker, create WO, or record DR |
| **RESOLVED** | Item's keywords match a downstream spec, Blueprint, or Work Order | No action needed |
| **ACKNOWLEDGED** | Item appears in the Gap Tracker or a Decision Record | Verify the entry is still current |
| **DONE** | Item was marked complete in its source section | No action needed |
