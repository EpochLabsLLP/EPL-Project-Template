#!/bin/bash
# Shared observability function for EPL governance hooks.
# Source this file from any hook to emit events to the JSONL log.
#
# Usage:
#   source "$HOOK_DIR/observe.sh"
#   emit_event "gate.spec" "block" "file_path=Code/main.py" "missing=Active WO"
#
# Events are appended to .claude/observability/events.jsonl (one JSON line per event).
# Fail-open: if emit fails, the calling hook is unaffected.

emit_event() {
  local EVENT_TYPE="$1"
  local DECISION="$2"
  shift 2

  local OBS_DIR="$CLAUDE_PROJECT_DIR/.claude/observability"
  local LOG_FILE="$OBS_DIR/events.jsonl"

  # Ensure directory exists (first call creates it)
  [ -d "$OBS_DIR" ] || mkdir -p "$OBS_DIR" 2>/dev/null

  # Build metadata JSON fragment from remaining key=value args
  local META=""
  for kv in "$@"; do
    local key="${kv%%=*}"
    local val="${kv#*=}"
    # Escape quotes in value
    val=$(echo "$val" | sed 's/"/\\"/g')
    [ -n "$META" ] && META="$META,"
    META="$META\"$key\":\"$val\""
  done

  # Get caller hook name
  local HOOK_NAME
  HOOK_NAME=$(basename "${BASH_SOURCE[1]}" 2>/dev/null || echo "unknown")

  # ISO timestamp
  local TS
  TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S")

  # Append JSONL line (atomic-ish via single echo)
  echo "{\"ts\":\"$TS\",\"event\":\"$EVENT_TYPE\",\"decision\":\"$DECISION\",\"hook\":\"$HOOK_NAME\",\"meta\":{$META}}" >> "$LOG_FILE" 2>/dev/null

  # Always succeed — observability must never block the calling hook
  return 0
}
