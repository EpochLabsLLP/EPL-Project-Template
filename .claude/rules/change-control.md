<!-- AGENT INSTRUCTION: This rule governs scope changes, spec revisions,
     and Work Order failure handling. It replaces the Mission Lock's change
     control protocol with a more comprehensive governance system.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# Change Control Protocol

*Intent: Prevents unauthorized scope changes and ensures spec modifications follow a formal process. Changes to frozen artifacts require human approval.*

## Scope Change Protocol

When new work is proposed that isn't covered by existing specs or Work Orders:

1. **STOP** current work immediately
2. **Present** the proposed change to Nathan with:
   - What the change is
   - Why it's needed
   - What it affects (which specs, modules, WOs)
   - Impact on timeline/scope
3. **Wait** for explicit approval
4. **Record** the decision in the Decision Record (DR-NNN entry)
5. **Update** affected specs through the spec revision protocol below
6. **Run** `/trace-check` to verify traceability integrity

Any scope change without Nathan's approval is a violation of project governance.

## Spec Revision Protocol

Frozen specs are **immutable**. When a frozen spec needs to change:

1. **Do NOT modify the existing file**
2. **Get Nathan's approval** for the revision
3. **Create a new version:** `{Abbrev}_{Spec}_v{N+1}.md`
4. **Archive the old version:** Move to `Specs/_Archive/`
5. **Record** the change in the Decision Record with:
   - Context: why the original spec was insufficient
   - Decision: what changed
   - Consequences: what downstream artifacts are affected
6. **Update downstream artifacts** as needed (cascade through the traceability chain)
7. **Run** `/trace-check` to verify no broken chains

## Work Order Failure Protocol

When a Work Order fails validation:

1. **Archive** the failed WO to `WorkOrders/_Archive/`
2. **Create** a new WO with incremented suffix: WO-N.M.T-A → WO-N.M.T-B
3. **Document** the failure reason in the new WO (what was tried, why it failed)
4. **Run** `/trace-check` to update the Work Ledger

## Decision Record Usage

The Decision Record (DR) replaces the Mission Lock's deviation log. Record any:
- Architectural decisions with non-obvious tradeoffs
- Scope additions or removals
- Technology choices
- Process changes
- Failed approaches worth documenting (to prevent repeats)

Format: DR-NNN entries in `Specs/{Abbrev}_Decision_Record.md`

## Escalation

STOP and escalate to Nathan when:
- A frozen spec appears to contain an error
- New work is needed that no existing spec covers
- A Work Order has failed twice (WO-N.M.T-C means two prior failures)
- A security concern is discovered
- A dependency needs to be added or changed
