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
source "$HOOK_DIR/observe.sh" 2>/dev/null
PROJECT_DIR="$CLAUDE_PROJECT_DIR"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
FILE_PATH=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.file_path)

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
      emit_event "gate.frozen" "block" "file_path=$NORM_PATH" "reason=governance_infra"
      cat <<DENY_JSON
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"GOVERNANCE PROTECTION: $PATTERN is template infrastructure. Do not modify directly. Template updates propagate via /template-sync."}}
DENY_JSON
      exit 0
    fi
  done
fi

# --- Part 1.5: One-cycle frozen bypass ---
# If /unlock-frozen has granted a one-shot bypass for a specific file,
# allow the edit and consume the marker. The audit trail is preserved
# in .claude/frozen-edit-log.md (written by the skill before this runs).
BYPASS_FILE="$PROJECT_DIR/.claude/frozen-bypass"
if [ -f "$BYPASS_FILE" ]; then
  BYPASS_TARGET=$(grep '^FILE=' "$BYPASS_FILE" 2>/dev/null | head -1 | cut -d= -f2-)
  if [ -n "$BYPASS_TARGET" ]; then
    # Normalize bypass target path
    NORM_BYPASS=$(echo "$BYPASS_TARGET" | sed 's|\\|/|g')
    # Match: exact match OR NORM_PATH ends with NORM_BYPASS
    if [ "$NORM_PATH" = "$NORM_BYPASS" ] || echo "$NORM_PATH" | grep -qF "$NORM_BYPASS"; then
      # Consume the bypass (one-shot) and allow the edit
      rm -f "$BYPASS_FILE"
      exit 0
    fi
  fi
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
if head -25 "$CHECK_FILE" 2>/dev/null | grep -qi "FROZEN"; then
  BASENAME=$(basename "$CHECK_FILE")
  emit_event "gate.frozen" "block" "file_path=$NORM_PATH" "reason=frozen_spec"
  cat <<DENY_JSON
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"FROZEN FILE: $BASENAME is a frozen spec. Must not be modified directly. Escalate to Nathan for change control."}}
DENY_JSON
  exit 0
fi

emit_event "gate.frozen" "allow" "file_path=$NORM_PATH"
exit 0
