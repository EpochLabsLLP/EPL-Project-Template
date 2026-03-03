#!/bin/bash
# Hook: PreToolUse -> Bash
# Blocks destructive commands that could cause irreversible damage.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMAND=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.command)

if [ -z "$COMMAND" ]; then
  exit 0
fi

if echo "$COMMAND" | grep -qE 'git\s+(push\s+--force|push\s+-f|reset\s+--hard|clean\s+-f|branch\s+-D)'; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive git command blocked. Use non-force alternatives or ask Nathan."}}'
  exit 0
fi

if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+[/\.]|rm\s+-rf\s+\*|del\s+/s\s+/q'; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Mass file deletion blocked. Be more specific about what to delete."}}'
  exit 0
fi

if echo "$COMMAND" | grep -qiE 'DROP\s+(TABLE|DATABASE)|DELETE\s+FROM\s+\w+\s*;?\s*$'; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive database command blocked. Use targeted queries or ask Nathan."}}'
  exit 0
fi

exit 0
