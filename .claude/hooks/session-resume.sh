#!/bin/bash
# Hook: SessionStart -> resume
# Fires when resuming a previous conversation (claude --continue / --resume).
# Lighter than startup — you already have conversation context, so this just
# re-anchors to the Work Ledger and shows current work items.

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
WORK_LEDGER="$PROJECT_DIR/Specs/Work_Ledger.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"

echo "[SESSION RESUMED — RE-ANCHORING]"

# --- Work Ledger summary ---
if [ -f "$WORK_LEDGER" ]; then
  # Show status line and active Work Orders
  STATUS=$(grep -m1 "^\*\*Status:\*\*" "$WORK_LEDGER" 2>/dev/null | sed 's/\*\*Status:\*\* //')
  [ -n "$STATUS" ] && echo "LEDGER STATUS: $STATUS"

  echo ""
  echo "[ACTIVE WORK ORDERS]"
  sed -n '/## Active Work Orders/,/^## /p' "$WORK_LEDGER" 2>/dev/null | head -15

  echo ""
  echo "[PROGRESS]"
  sed -n '/## Progress/,/^$/p' "$WORK_LEDGER" 2>/dev/null | head -5
else
  echo "[NO WORK LEDGER] Run \`/trace-check\` to generate."
fi

# --- Gap Tracker: Just open items ---
if [ -f "$GAP_TRACKER" ]; then
  NEXT_TASK=$(grep -m1 "^- \[ \]" "$GAP_TRACKER" 2>/dev/null | sed 's/^- \[ \] //')
  TOTAL_OPEN=$(grep -c "^- \[ \]" "$GAP_TRACKER" 2>/dev/null || echo "0")
  [ -n "$NEXT_TASK" ] && echo "NEXT TASK: $NEXT_TASK ($TOTAL_OPEN total open)"

  # Scope guard (pipe to grep -c; do NOT use || echo "0" — it doubles output)
  TIER0=$(sed -n '/## Tier 0/,/## Tier [1-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  if [ "$TIER0" != "0" ] && [ "$TIER0" != "" ]; then
    echo "SCOPE GUARD: $TIER0 Tier 0 defect(s) open — resolve these first."
  fi
fi
