#!/bin/bash
# Hook: PreToolUse -> Bash
# Blocks destructive commands that could cause irreversible damage.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/observe.sh" 2>/dev/null
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
COMMAND=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.command 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

if echo "$COMMAND" | grep -qE 'git\s+(push\s+--force|push\s+-f|reset\s+--hard|clean\s+-f|branch\s+-D)'; then
  emit_event "gate.dangerous" "block" "pattern=destructive_git"
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive git command blocked. Use non-force alternatives or ask Nathan."}}'
  exit 0
fi

if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+[/\.]|rm\s+-rf\s+\*|del\s+/s\s+/q'; then
  emit_event "gate.dangerous" "block" "pattern=mass_delete"
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Mass file deletion blocked. Be more specific about what to delete."}}'
  exit 0
fi

if echo "$COMMAND" | grep -qiE 'DROP\s+(TABLE|DATABASE)|DELETE\s+FROM\s+\w+\s*;?\s*$'; then
  emit_event "gate.dangerous" "block" "pattern=destructive_sql"
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive database command blocked. Use targeted queries or ask Nathan."}}'
  exit 0
fi

emit_event "gate.dangerous" "allow"
exit 0
