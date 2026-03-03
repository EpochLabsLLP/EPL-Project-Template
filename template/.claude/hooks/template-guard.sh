#!/bin/bash
# Hook: PreToolUse -> Write
# Blocks creation of new spec documents that weren't derived from templates.
# Fail-open: if anything goes wrong parsing input, allow the write.
#
# Governed directories: Specs/, Testing/, WorkOrders/
# Governed patterns: PVD, PRD, Product_Brief, Engineering_Spec, UX_Spec,
#                    Blueprint, Testing_Plan, Work_Order, Decision_Record,
#                    gap_tracker, Work_Ledger
#
# Escape hatch: <!-- TEMPLATE_OVERRIDE: reason --> in content bypasses guard.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"

# Capture stdin ONCE (JSON from Claude Code), then pipe to each extraction
INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python "$HOOK_DIR/parse_hook_input.py" tool_input.file_path)
CONTENT=$(echo "$INPUT" | python "$HOOK_DIR/parse_hook_input.py" tool_input.content)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Normalize: get filename and convert backslashes to forward slashes
FILENAME=$(basename "$FILE_PATH")
NORM_PATH=$(echo "$FILE_PATH" | tr '\' '/')

# --- Check 1: Does the file already exist? ---
if [ -f "$FILE_PATH" ]; then
  exit 0
fi

# Also check with CLAUDE_PROJECT_DIR prefix in case path is relative
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
  FULL_PATH="$CLAUDE_PROJECT_DIR/$FILE_PATH"
  if [ -f "$FULL_PATH" ]; then
    exit 0
  fi
fi

# --- Check 2: Is this in a governed directory? ---
IN_GOVERNED=false
if echo "$NORM_PATH" | grep -qiE "(^|/)Specs/"; then
  IN_GOVERNED=true
elif echo "$NORM_PATH" | grep -qiE "(^|/)Testing/"; then
  IN_GOVERNED=true
elif echo "$NORM_PATH" | grep -qiE "(^|/)WorkOrders/"; then
  IN_GOVERNED=true
fi

if [ "$IN_GOVERNED" = false ]; then
  exit 0
fi

# --- Check 3: Does the filename match a governed pattern? ---
MATCHES_PATTERN=false
GOVERNED_PATTERNS=(
  "PVD"
  "PRD"
  "Product_Brief"
  "Engineering_Spec"
  "UX_Spec"
  "Blueprint"
  "Testing_Plan"
  "Work_Order"
  "Decision_Record"
  "gap_tracker"
  "Work_Ledger"
)

for PATTERN in "${GOVERNED_PATTERNS[@]}"; do
  if echo "$FILENAME" | grep -qi "$PATTERN"; then
    MATCHES_PATTERN=true
    break
  fi
done

if [ "$MATCHES_PATTERN" = false ]; then
  exit 0
fi

# --- Check 4: Skip TEMPLATE_ files themselves ---
if echo "$FILENAME" | grep -q "^TEMPLATE_"; then
  exit 0
fi
if echo "$FILENAME" | grep -q "^SESSION_TEMPLATE"; then
  exit 0
fi

# --- Check 5: Does content contain template provenance marker? ---
if echo "$CONTENT" | grep -q "<!-- TEMPLATE_SOURCE:"; then
  exit 0
fi

# --- Check 6: Does content contain override escape hatch? ---
if echo "$CONTENT" | grep -q "<!-- TEMPLATE_OVERRIDE:"; then
  exit 0
fi

# --- DENY: New governed file without template provenance ---
cat <<'DENY_JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"TEMPLATE GUARD: New spec documents must be created from templates.\nUse: /init-doc <type> [abbreviation]\nTypes: pvd, prd, brief, es, ux, bp, tp, wo, dr\nOr add <!-- TEMPLATE_OVERRIDE: reason --> to bypass."}}
DENY_JSON

exit 0
