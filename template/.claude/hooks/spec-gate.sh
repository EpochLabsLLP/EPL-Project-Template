#!/bin/bash
# Hook: PreToolUse -> Edit|Write
# CODE GATE: Blocks code file writes when governance requirements are not met.
#
# This is the automated enforcement of SDD principles:
# "No code before frozen specs" and "No code without an active Work Order."
#
# Checks:
# 1. Is the target file in a code directory? (If not, always ALLOW)
# 2. Are the 4 required frozen specs present?
#    Path A: PVD (FROZEN)
#    Path B: Product Brief (FROZEN) AND PRD (FROZEN)
#    Plus: Engineering Spec (FROZEN), Blueprint (FROZEN), Testing Plans (FROZEN)
# 3. Is there an active Work Order (status: IN-PROGRESS)?
# 4. Missing/unfrozen/no active WO → exit 2 (BLOCK)
# 5. All present, frozen, and active WO → exit 0 (ALLOW)

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

# --- Work Order check ---
# Require at least one Work Order with status IN-PROGRESS before code writes.
# This enforces the SDD execution protocol: specs → WO → code.
HAS_ACTIVE_WO=false

if [ -d "$PROJECT_DIR/WorkOrders" ]; then
  for f in "$PROJECT_DIR"/WorkOrders/*.md; do
    [ -f "$f" ] || continue
    # Skip templates and archive
    case "$f" in
      *TEMPLATE_*|*_Archive*) continue ;;
    esac
    # Check first 20 lines for IN-PROGRESS status
    if head -20 "$f" | grep -qE '\*\*Status\*\*.*IN-PROGRESS|Status.*IN-PROGRESS'; then
      HAS_ACTIVE_WO=true
      break
    fi
  done
fi

if [ "$HAS_ACTIVE_WO" = false ]; then
  MISSING+=("Active Work Order (create with /init-doc wo, set status to IN-PROGRESS)")
fi

# --- Decision ---
if [ ${#MISSING[@]} -gt 0 ]; then
  MISSING_LIST=$(printf ", %s" "${MISSING[@]}")
  MISSING_LIST=${MISSING_LIST:2}  # Remove leading ", "
  echo "CODE GATE BLOCKED: Cannot write to code files."
  echo "Missing: $MISSING_LIST"
  echo ""
  echo "Required before writing code:"
  echo "  1. Freeze all required specs (PVD/Brief+PRD, Engineering Spec, Blueprint, Testing Plans)"
  echo "  2. Create a Work Order (/init-doc wo WO-N.M.T-X) and set status to IN-PROGRESS"
  exit 2  # BLOCK
fi

exit 0  # All specs frozen + active WO, allow
