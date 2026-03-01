#!/bin/bash
# Hook: SessionStart -> resume
# Fires when resuming a previous conversation (claude --continue / --resume).
# Lighter than startup — you already have conversation context, so this just
# re-anchors to the mission lock and shows current work items.

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
MISSION_LOCK="$PROJECT_DIR/.claude/rules/mission-lock.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"

echo "[SESSION RESUMED — RE-ANCHORING]"

# --- Active Scope from Mission Lock ---
if [ -f "$MISSION_LOCK" ]; then
  PHASE=$(grep -m1 "Current Phase:" "$MISSION_LOCK" 2>/dev/null | sed 's/.*Current Phase:\s*//' | sed 's/\*//g')
  [ -n "$PHASE" ] && echo "PHASE: $PHASE"

  echo ""
  echo "[ACTIVE SCOPE]"
  sed -n '/## Active Scope/,/## Explicit Out-of-Scope/p' "$MISSION_LOCK" 2>/dev/null | head -20
  echo ""
  echo "[OUT OF SCOPE]"
  sed -n '/## Explicit Out-of-Scope/,/## Success Criteria/p' "$MISSION_LOCK" 2>/dev/null | head -15
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
