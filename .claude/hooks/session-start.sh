#!/bin/bash
# Hook: SessionStart -> startup
# Fires on fresh session start. Outputs project context to stdout,
# which Claude Code injects as conversation context for the agent.
#
# This is the primary anti-drift mechanism. It forces every new session
# to re-anchor to the project's status, traceability health, and next task.

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
WORK_LEDGER="$PROJECT_DIR/Specs/Work_Ledger.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"
SESSIONS_DIR="$PROJECT_DIR/Sessions"

echo "[SESSION START — MISSION ANCHOR]"

# --- Work Ledger (project status + traceability) ---
if [ -f "$WORK_LEDGER" ]; then
  echo ""
  echo "[WORK LEDGER]"
  cat "$WORK_LEDGER"
else
  echo ""
  echo "[NO WORK LEDGER] Run \`/trace-check\` to generate Specs/Work_Ledger.md."
fi

# --- Gap Tracker ---
if [ -f "$GAP_TRACKER" ]; then
  echo ""
  echo "[GAP TRACKER — OPEN ITEMS]"

  # Count open items per tier (pipe to grep -c; do NOT use || echo "0" — it doubles output)
  TIER0=$(sed -n '/## Tier 0/,/## Tier [1-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  TIER1=$(sed -n '/## Tier 1/,/## Tier [2-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  TIER2=$(sed -n '/## Tier 2/,/## Tier [3-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  TIER3=$(sed -n '/## Tier 3/,/^$/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")

  echo "Tier 0 (Critical): $TIER0 | Tier 1 (Functional): $TIER1 | Tier 2 (Quality): $TIER2 | Tier 3 (Enhancement): $TIER3"

  # First unchecked item = next task
  NEXT_TASK=$(grep -m1 "^- \[ \]" "$GAP_TRACKER" 2>/dev/null | sed 's/^- \[ \] //')
  [ -n "$NEXT_TASK" ] && echo "NEXT TASK: $NEXT_TASK"

  # Scope guard
  if [ "$TIER0" != "0" ] && [ "$TIER0" != "" ]; then
    echo "SCOPE GUARD: Tier 0 defects open. Resolve ALL Tier 0 items before any other work."
  fi
else
  echo ""
  echo "[NO GAP TRACKER] Create Specs/gap_tracker.md to track work items by priority tier."
fi

# --- Last Session Summary ---
if [ -d "$SESSIONS_DIR" ]; then
  LATEST=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | head -1)
  if [ -n "$LATEST" ]; then
    echo ""
    echo "[LAST SESSION: $(basename "$LATEST")]"
    tail -20 "$LATEST"
  fi
fi

echo ""
echo "Read the above context carefully before starting work."
