---
name: alignment-check
description: Verify code actually implements what the spec says, using grep-based evidence gathering. Use when you need to prove that code matches spec requirements, when verifying flow paths from trigger to action, or when checking for spec-code drift after changes.
argument-hint: <module>
---

# Alignment Check

This skill performs flow-path verification — grep-based evidence gathering that code matches specs. It does NOT trust that code is correct by reading it; it PROVES alignment by tracing from spec requirements to code paths.

When invoked with a module name (`$ARGUMENTS`):

1. **Load the spec** for this module (use /spec-lookup logic).

2. **Extract verifiable requirements.** From the spec, list every concrete behavior:
   - "Button X triggers action Y"
   - "Service A calls Service B when condition C"
   - "Data flows from Source -> Transform -> Destination"
   - "Error condition X produces response Y"

3. **For each requirement, gather evidence:**
   - Grep for the trigger/entry point in code
   - Trace the call chain from trigger to action
   - Confirm the wiring is complete (no broken links)
   - Check that the behavior matches spec (not just "something happens")

4. **Report as an evidence table:**
   | Spec Requirement | Entry Point | Code Path | Verified? | Notes |
   |-----------------|-------------|-----------|:---------:|-------|

5. **Flag any discrepancies:**
   - Spec says X but code does Y
   - Spec requires behavior but no code path exists
   - Code has behavior not described in spec (scope creep?)

6. **Summary verdict:** ALIGNED, PARTIALLY ALIGNED (list gaps), or MISALIGNED (list conflicts).
