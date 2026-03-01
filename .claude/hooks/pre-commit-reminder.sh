#!/bin/bash
# Hook: PreToolUse -> Bash
# Advisory reminder to run /pre-commit before git commit.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMAND=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.command)

if [ -z "$COMMAND" ]; then
  exit 0
fi

if echo "$COMMAND" | grep -qE 'git\s+commit'; then
  echo '{"systemMessage":"REMINDER: Run /pre-commit before committing to check for secrets, .gitignore violations, and file hygiene issues."}'
  exit 0
fi

exit 0
