#!/bin/bash
# Hook: PreToolUse -> Edit|Write
# Blocks code file writes when required frozen specs are missing.
#
# This is the automated enforcement of the SDD principle:
# "No code before frozen specs."
#
# Checks:
# 1. Is the target file in a code directory? (If not, always ALLOW)
# 2. Are the 4 required frozen specs present?
#    Path A: PVD (FROZEN)
#    Path B: Product Brief (FROZEN) AND PRD (FROZEN)
#    Plus: Engineering Spec (FROZEN), Blueprint (FROZEN), Testing Plans (FROZEN)
# 3. Missing/unfrozen → exit 2 (BLOCK)
# 4. All present and frozen → exit 0 (ALLOW)

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$CLAUDE_PROJECT_DIR"

# Parse the target file path from hook input
FILE_PATH=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.file_path)

if [ -z "$FILE_PATH" ]; then
  exit 0  # No file path = not a file write, allow
fi

# --- Code directory check ---
# Only gate writes to code directories. Spec files, docs, etc. are always allowed.
CODE_DIRS=("Code/" "code/" "src/" "lib/" "app/" "packages/")
IS_CODE=false

for dir in "${CODE_DIRS[@]}"; do
  if echo "$FILE_PATH" | grep -q "$dir"; then
    IS_CODE=true
    break
  fi
done

if [ "$IS_CODE" = false ]; then
  exit 0  # Not a code file, always allow
fi

# --- Spec readiness check ---
MISSING=()

# Check Path A (PVD) or Path B (Product Brief + PRD)
HAS_PVD=false
HAS_BRIEF=false
HAS_PRD=false

for f in "$PROJECT_DIR"/Specs/*PVD*; do
  [ -f "$f" ] || continue
  if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
  if head -15 "$f" | grep -q "FROZEN"; then
    HAS_PVD=true
    break
  fi
done

if [ "$HAS_PVD" = false ]; then
  # Try Path B
  for f in "$PROJECT_DIR"/Specs/*Product_Brief*; do
    [ -f "$f" ] || continue
    if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
    if head -15 "$f" | grep -q "FROZEN"; then
      HAS_BRIEF=true
      break
    fi
  done
  for f in "$PROJECT_DIR"/Specs/*PRD*; do
    [ -f "$f" ] || continue
    if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
    if head -15 "$f" | grep -q "FROZEN"; then
      HAS_PRD=true
      break
    fi
  done

  if [ "$HAS_BRIEF" = false ] || [ "$HAS_PRD" = false ]; then
    MISSING+=("PVD (or Product Brief + PRD)")
  fi
fi

# Check Engineering Spec
HAS_ES=false
for f in "$PROJECT_DIR"/Specs/*Engineering_Spec*; do
  [ -f "$f" ] || continue
  if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
  if head -15 "$f" | grep -q "FROZEN"; then
    HAS_ES=true
    break
  fi
done
[ "$HAS_ES" = false ] && MISSING+=("Engineering Spec")

# Check Blueprint
HAS_BP=false
for f in "$PROJECT_DIR"/Specs/*Blueprint*; do
  [ -f "$f" ] || continue
  if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
  if head -15 "$f" | grep -q "FROZEN"; then
    HAS_BP=true
    break
  fi
done
[ "$HAS_BP" = false ] && MISSING+=("Blueprint")

# Check Testing Plans
HAS_TP=false
for f in "$PROJECT_DIR"/Testing/*Testing_Plans*; do
  [ -f "$f" ] || continue
  if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
  if head -15 "$f" | grep -q "FROZEN"; then
    HAS_TP=true
    break
  fi
done
[ "$HAS_TP" = false ] && MISSING+=("Testing Plans")

# --- Decision ---
if [ ${#MISSING[@]} -gt 0 ]; then
  MISSING_LIST=$(printf ", %s" "${MISSING[@]}")
  MISSING_LIST=${MISSING_LIST:2}  # Remove leading ", "
  echo "SPEC GATE BLOCKED: Cannot write to code files until required specs are frozen."
  echo "Missing/unfrozen: $MISSING_LIST"
  echo "Freeze these specs before writing code, or write to a non-code directory."
  exit 2  # BLOCK
fi

exit 0  # All specs frozen, allow
