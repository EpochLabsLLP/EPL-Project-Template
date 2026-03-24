#!/bin/bash
# Shared progress log utility for EPL multi-instance collaboration.
# Source this file from hooks or skills to append entries to .claude/progress.log.
#
# The progress log is an append-only, instance-stamped activity journal.
# It enables cross-session and cross-instance awareness of recent work.
#
# Format: ISO_TIMESTAMP | INSTANCE_ID | MESSAGE
#
# Usage:
#   source "$HOOK_DIR/progress-log.sh"
#   log_progress "WO-1.1.1-A DONE | Built ConfigLoader, 8 tests pass | -> WO-1.1.2-A next"
#   show_recent_progress 20   # Show last 20 lines (default)

log_progress() {
  local MESSAGE="$1"
  local PROGRESS_FILE="$CLAUDE_PROJECT_DIR/.claude/progress.log"
  local INSTANCE_ID
  INSTANCE_ID=$(get_instance_id 2>/dev/null || echo "unknown")
  local TS
  TS=$(date -u +"%Y-%m-%dT%H:%M:%S" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S")

  echo "$TS | $INSTANCE_ID | $MESSAGE" >> "$PROGRESS_FILE" 2>/dev/null
  return 0
}

show_recent_progress() {
  local LINES="${1:-20}"
  local PROGRESS_FILE="$CLAUDE_PROJECT_DIR/.claude/progress.log"

  if [ ! -f "$PROGRESS_FILE" ]; then
    return 0  # No progress log yet — nothing to show
  fi

  local LINE_COUNT
  LINE_COUNT=$(wc -l < "$PROGRESS_FILE" 2>/dev/null | tr -d ' ')
  if [ "$LINE_COUNT" = "0" ]; then
    return 0
  fi

  echo ""
  echo "[PROGRESS LOG — RECENT ACTIVITY (last $LINES entries)]"
  tail -"$LINES" "$PROGRESS_FILE"

  # Flag entries from other instances (different from current instance)
  local CURRENT_ID
  CURRENT_ID=$(get_instance_id 2>/dev/null)
  if [ -n "$CURRENT_ID" ] && [ "$CURRENT_ID" != "unknown" ]; then
    local OTHER_INSTANCES
    OTHER_INSTANCES=$(tail -"$LINES" "$PROGRESS_FILE" | grep -v "| $CURRENT_ID |" | grep -o "| [^ ]* |" | sort -u | tr -d '|' | tr -d ' ' | head -5)
    if [ -n "$OTHER_INSTANCES" ]; then
      echo "[NOTE: Entries from other instance(s) detected. Review before proceeding.]"
    fi
  fi
}
