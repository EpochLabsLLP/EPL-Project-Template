#!/bin/bash
# Hook: PreToolUse -> Bash|Edit|Write
# PHASE SCOPE: Advisory system that tells agents when a tool is unusual
# for the current SDD workflow phase.
#
# v2.7.0: Advisory only (systemMessage). No tool calls blocked.
# v2.8.0: Will convert validated advisories to hard blocks.
#
# Phases are DERIVED from project state via detect_phase.py:
#   SPEC -> PLANNING -> IMPLEMENTATION -> VALIDATION -> MAINTENANCE
#
# Fail-open: if detection fails, allow silently.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/observe.sh" 2>/dev/null
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$HOOK_DIR/../.." && pwd)}"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)

# --- Detect current phase ---
PHASE_SCRIPT="$HOOK_DIR/detect_phase.py"
if [ ! -f "$PHASE_SCRIPT" ]; then
  exit 0  # No phase detection = no scoping
fi

PHASE=$($PYTHON "$PHASE_SCRIPT" "$PROJECT_DIR" 2>/dev/null)
if [ -z "$PHASE" ] || [ "$PHASE" = "UNKNOWN" ]; then
  exit 0  # Detection failed = fail-open
fi

# --- Determine what tool is being used and on what target ---
FILE_PATH=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.file_path 2>/dev/null)
COMMAND=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.command 2>/dev/null)

# Build a tool descriptor for matching
TOOL_DESC=""
if [ -n "$FILE_PATH" ]; then
  # Edit or Write tool
  if echo "$FILE_PATH" | grep -qE '(Code/|code/|src/|lib/|app/|packages/)'; then
    TOOL_DESC="Edit:Code/"
  elif echo "$FILE_PATH" | grep -qE '(Specs/)'; then
    TOOL_DESC="Edit:Specs/"
  fi
elif [ -n "$COMMAND" ]; then
  # Bash tool — check for code-writing patterns
  CODE_DIR_PATTERN='(Code/|code/|src/|lib/|app/|packages/)'
  if echo "$COMMAND" | grep -qE "(>|>>|tee|cp |mv |mkdir).*$CODE_DIR_PATTERN"; then
    TOOL_DESC="Bash:write-to-code"
  fi
fi

if [ -z "$TOOL_DESC" ]; then
  exit 0  # Not a restricted tool pattern
fi

# --- Check restrictions ---
RESTRICTIONS_FILE="$PROJECT_DIR/.claude/phase-restrictions.json"
if [ ! -f "$RESTRICTIONS_FILE" ]; then
  exit 0
fi

# Use Python to check the restriction (JSON parsing in bash is painful)
ADVISORY=$($PYTHON -c "
import json, sys
try:
    with open('$RESTRICTIONS_FILE', 'r') as f:
        data = json.load(f)
    phase_rules = data.get('$PHASE', {})
    for entry in phase_rules.get('advisory', []):
        if entry['pattern'] == '$TOOL_DESC':
            print(entry['message'])
            break
except Exception:
    pass
" 2>/dev/null)

if [ -n "$ADVISORY" ]; then
  emit_event "phase.advisory" "warn" "phase=$PHASE" "tool=$TOOL_DESC"
  echo "{\"systemMessage\":\"[PHASE AWARENESS] Current phase: $PHASE. $ADVISORY\"}"
fi

exit 0  # Advisory only — never block in v2.7.0
