#!/bin/bash
# Hook: PreToolUse -> Edit|Write
# Two responsibilities:
#   1. Auto-discover and protect frozen spec files (files with FROZEN in first 15 lines)
#   2. Protect governance infrastructure (hooks, rules, scripts) from modification
#
# Fail-open: if parsing fails or scan errors, allow the write.
#
# Build mode: set TEMPLATE_BUILD_MODE=1 to bypass governance protection
# (used during initial template construction only).

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$CLAUDE_PROJECT_DIR"
FILE_PATH=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.file_path)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Normalize path separators
NORM_PATH=$(echo "$FILE_PATH" | sed 's|\|/|g')

# --- Part 1: Protect governance infrastructure ---
# These are template-owned files that agents should never modify directly.
# Skip this check during template construction (TEMPLATE_BUILD_MODE=1).
if [ "$TEMPLATE_BUILD_MODE" != "1" ]; then
  GOVERNANCE_PATTERNS=(
    ".claude/hooks/"
    ".claude/rules/"
    ".claude/settings.json"
    "parse_hook_input.py"
    "validate_traceability.py"
    "TEMPLATE_MANIFEST.json"
  )

  for PATTERN in "${GOVERNANCE_PATTERNS[@]}"; do
    if echo "$NORM_PATH" | grep -qF "$PATTERN"; then
      cat <<DENY_JSON
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"GOVERNANCE PROTECTION: $PATTERN is template infrastructure. Do not modify directly. Template updates propagate via /template-sync."}}
DENY_JSON
      exit 0
    fi
  done
fi

# --- Part 2: Auto-discover frozen spec files ---
# Only check if the target file is in Specs/, Testing/, or WorkOrders/
IS_SPEC_FILE=false
if echo "$NORM_PATH" | grep -qiE "(^|/)(Specs|Testing|WorkOrders)/"; then
  IS_SPEC_FILE=true
fi

if [ "$IS_SPEC_FILE" = false ]; then
  exit 0
fi

# Check if the target file itself is frozen
# Resolve to absolute path for the frozen check
if [ -f "$FILE_PATH" ]; then
  CHECK_FILE="$FILE_PATH"
elif [ -n "$PROJECT_DIR" ] && [ -f "$PROJECT_DIR/$FILE_PATH" ]; then
  CHECK_FILE="$PROJECT_DIR/$FILE_PATH"
else
  # File doesn't exist yet — can't be frozen
  exit 0
fi

# Check first 15 lines for FROZEN marker
if head -15 "$CHECK_FILE" 2>/dev/null | grep -qi "FROZEN"; then
  BASENAME=$(basename "$CHECK_FILE")
  cat <<DENY_JSON
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"FROZEN FILE: $BASENAME is a frozen spec. Must not be modified directly. Escalate to Nathan for change control."}}
DENY_JSON
  exit 0
fi

exit 0
