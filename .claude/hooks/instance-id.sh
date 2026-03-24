#!/bin/bash
# Shared instance identity utility for EPL multi-instance collaboration.
# Source this file from session hooks to generate and read instance IDs.
#
# Instance ID format: {agent}-{env}-{YYYYMMDD}-{HHMM}
#   {agent} — project abbreviation (from .claude/project-abbreviation or dir name)
#   {env}   — "vsc" (VS Code) or "cli" (CLI/headless)
#   {YYYYMMDD}-{HHMM} — session start timestamp
#
# Usage:
#   source "$HOOK_DIR/instance-id.sh"
#   generate_instance_id   # Call once at session start — writes .claude/instance-id
#   ID=$(get_instance_id)  # Read the current instance ID

_detect_agent_name() {
  local ABBREV_FILE="$CLAUDE_PROJECT_DIR/.claude/project-abbreviation"
  if [ -f "$ABBREV_FILE" ]; then
    head -1 "$ABBREV_FILE" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]'
    return
  fi
  # Fall back to directory name, lowercased, first word, max 8 chars
  basename "$CLAUDE_PROJECT_DIR" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9].*//; s/^\(.\{8\}\).*/\1/'
}

_detect_env() {
  # VS Code sets TERM_PROGRAM=vscode or VSCODE_PID
  if [ -n "$VSCODE_PID" ] || [ "$TERM_PROGRAM" = "vscode" ]; then
    echo "vsc"
  else
    echo "cli"
  fi
}

generate_instance_id() {
  local AGENT ENV TIMESTAMP ID
  AGENT=$(_detect_agent_name)
  ENV=$(_detect_env)
  TIMESTAMP=$(date +"%Y%m%d-%H%M" 2>/dev/null || date +"%Y%m%d-0000")
  ID="${AGENT}-${ENV}-${TIMESTAMP}"

  # Write to instance-id file (overwritten each session start)
  echo "$ID" > "$CLAUDE_PROJECT_DIR/.claude/instance-id" 2>/dev/null
  echo "$ID"
}

get_instance_id() {
  local ID_FILE="$CLAUDE_PROJECT_DIR/.claude/instance-id"
  if [ -f "$ID_FILE" ]; then
    cat "$ID_FILE" 2>/dev/null
  else
    echo "unknown"
  fi
}
