#!/bin/bash
# Hook: PreToolUse -> Edit|Write
# Prevents accidental modification of frozen spec files.
# Update FROZEN_PATTERNS when specs are finalized for build.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
FILE_PATH=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.file_path)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Add frozen spec files here as they are finalized for build
# Currently no files are frozen (pre-build phase)
FROZEN_PATTERNS=(
  # "Specs/ViviGames_PVD.md"
  # "Specs/ViviGames_Engineering_Spec.md"
)

for PATTERN in "${FROZEN_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qF "$PATTERN"; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"FROZEN FILE: $PATTERN is a frozen spec. Must not be modified. Escalate to Nathan.\"}}"
    exit 0
  fi
done

exit 0
