#!/bin/bash
# Shared checkpoint reader for EPL session hooks.
# Source this file from session-start/resume/compact to display checkpoint state.
#
# Usage:
#   source "$HOOK_DIR/checkpoint.sh"
#   show_checkpoint "compact"   # or "resume" or "start"

show_checkpoint() {
  local CONTEXT="$1"  # "compact", "resume", or "start"
  local _CPD="${CLAUDE_PROJECT_DIR:-$PROJECT_DIR}"
  local CHECKPOINT_FILE="$_CPD/.claude/checkpoint.md"

  if [ ! -f "$CHECKPOINT_FILE" ]; then
    return 0  # No checkpoint — nothing to show
  fi

  # Check if checkpoint has content (not just a "no active work" clear)
  if grep -q "No active work" "$CHECKPOINT_FILE" 2>/dev/null; then
    return 0  # Cleared checkpoint — nothing to resume
  fi

  # Calculate staleness
  local NOW
  NOW=$(date +%s 2>/dev/null || echo 0)
  local FILE_TIME
  FILE_TIME=$(date -r "$CHECKPOINT_FILE" +%s 2>/dev/null || echo 0)
  local AGE_SECONDS=$(( NOW - FILE_TIME ))
  local AGE_MINUTES=$(( AGE_SECONDS / 60 ))
  local AGE_HOURS=$(( AGE_SECONDS / 3600 ))

  local STALENESS=""
  if [ "$AGE_HOURS" -gt 24 ]; then
    STALENESS="(${AGE_HOURS}h old — likely stale, previous session may have ended normally)"
  elif [ "$AGE_HOURS" -gt 1 ]; then
    STALENESS="(${AGE_HOURS}h old)"
  elif [ "$AGE_MINUTES" -gt 0 ]; then
    STALENESS="(${AGE_MINUTES}m old — likely current)"
  else
    STALENESS="(just updated)"
  fi

  echo ""
  if [ "$CONTEXT" = "compact" ]; then
    echo "[CHECKPOINT — IN-PROGRESS WORK RECOVERY] $STALENESS"
    echo "CRITICAL: Resume from this checkpoint. Re-read the listed files before editing."
    echo ""
    cat "$CHECKPOINT_FILE"
  elif [ "$CONTEXT" = "resume" ]; then
    echo "[CHECKPOINT — RESUME STATE] $STALENESS"
    # Show abbreviated version: Active WO + Current Task + Files In Progress
    sed -n '/## Active Work Order/,/## Quality Gates/p' "$CHECKPOINT_FILE" | head -20
    sed -n '/## Current Task/,/## Remaining Work/p' "$CHECKPOINT_FILE" | head -5
    sed -n '/## Files In Progress/,/## Quality Gates/p' "$CHECKPOINT_FILE" | head -10
  else
    # start — show with staleness warning
    if [ "$AGE_HOURS" -gt 24 ]; then
      echo "[CHECKPOINT — STALE] $STALENESS"
      echo "A checkpoint exists but is old. The previous session may have ended without clearing it."
      echo "Verify if this work is still relevant before resuming."
    else
      echo "[CHECKPOINT — PRIOR WORK STATE] $STALENESS"
    fi
    echo ""
    cat "$CHECKPOINT_FILE"
  fi
}
