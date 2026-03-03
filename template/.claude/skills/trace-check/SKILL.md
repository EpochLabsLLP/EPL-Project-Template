---
name: trace-check
description: Validate traceability chains, Work Order status, and spec readiness. Generates the Work Ledger.
user_invocable: true
---

# trace-check

Validates the SDD traceability system and generates the Work Ledger.

## What It Does

1. Parses all spec files (Specs/, Testing/, WorkOrders/) for traceability IDs
2. Validates traceability chains (PVD → ES → BP → TP → WO)
3. Checks spec readiness (which frozen specs exist)
4. Tracks Work Order status (PENDING, IN-PROGRESS, VALIDATION, DONE, FAILED)
5. Generates `Specs/Work_Ledger.md` with full project status
6. Reports orphans, gaps, missing test mirrors, and chain health

## When to Use

- After creating or updating any spec document
- After creating, completing, or failing a Work Order
- Before commits that touch spec files or Work Orders
- At the start of implementation work to understand project state
- When you want to verify the traceability system is healthy

## How to Invoke

```
/trace-check
```

## Execution

Run the validation script:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/trace-check/scripts/validate_traceability.py" "$CLAUDE_PROJECT_DIR"
```

Then read and present the generated Work Ledger at `Specs/Work_Ledger.md`.

## Output

The script writes to `Specs/Work_Ledger.md` AND outputs to stdout. Present the key findings to the user:

1. **Spec Readiness** — Which frozen specs exist
2. **Chain Health** — CLEAN or list of warnings/errors
3. **Active Work Orders** — Current WO status
4. **Project Progress** — How many Blueprint tasks have completed WOs
5. **Issues** — Orphans, gaps, missing TP mirrors

## Interpreting Results

- **CLEAN**: All chains valid, no orphans or gaps
- **Warning**: Non-blocking issues (missing optional specs, incomplete coverage)
- **Error**: Blocking issues (orphan IDs, broken chains, missing required specs)
