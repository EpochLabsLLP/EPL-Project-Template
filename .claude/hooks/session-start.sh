#!/bin/bash
# Hook: SessionStart -> startup
# Fires on fresh session start. Outputs mission context to stdout,
# which Claude Code injects as conversation context for the agent.
#
# This is the primary anti-drift mechanism. It forces every new session
# to re-anchor to the project's mission, current phase, and next task.

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
MISSION_LOCK="$PROJECT_DIR/.claude/rules/mission-lock.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"
SESSIONS_DIR="$PROJECT_DIR/Sessions"

echo "[SESSION START — MISSION ANCHOR]"

# --- Mission Lock ---
if [ -f "$MISSION_LOCK" ]; then
  echo ""
  echo "[MISSION LOCK]"
  cat "$MISSION_LOCK"

  # Extract one-line summary for quick reference
  PHASE=$(grep -m1 "Current Phase:" "$MISSION_LOCK" 2>/dev/null | sed 's/.*Current Phase:\s*//' | sed 's/\*//g')
  OBJECTIVE=$(grep -m1 "Phase Objective:" "$MISSION_LOCK" 2>/dev/null | sed 's/.*Phase Objective:\s*//' | sed 's/\*//g')
  if [ -n "$PHASE" ]; then
    echo ""
    echo "ACTIVE PHASE: $PHASE"
    [ -n "$OBJECTIVE" ] && echo "OBJECTIVE: $OBJECTIVE"
  fi
else
  echo ""
  echo "[NO MISSION LOCK] Create .claude/rules/mission-lock.md before starting implementation work."
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
