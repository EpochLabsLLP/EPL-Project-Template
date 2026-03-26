#!/bin/bash
# Hook: PreToolUse -> Edit|Write AND PreToolUse -> Bash
# CODE GATE: Blocks code file writes when governance requirements are not met.
#
# This is the automated enforcement of SDD principles:
# "No code before frozen specs" and "No code without an active Work Order."
# "Constraint > Documentation" (Harness Engineering principle)
#
# Triggers on TWO tool types:
#   - Edit/Write: extracts file_path directly
#   - Bash: detects file-writing commands (cat/echo/tee/cp/mv + redirect) targeting code dirs
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
source "$HOOK_DIR/observe.sh" 2>/dev/null
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$HOOK_DIR/../.." && pwd)}"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)

# --- Determine file path from Edit/Write or Bash ---
FILE_PATH=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.file_path 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  # Not an Edit/Write — check if it's a Bash command writing to code directories
  COMMAND=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.command 2>/dev/null)

  if [ -z "$COMMAND" ]; then
    exit 0  # No file path and no command = nothing to gate
  fi

  # Detect file-writing Bash patterns targeting code directories
  # Patterns: cat/echo/printf > path, tee path, cp/mv to path, heredoc > path, mkdir -p + write
  CODE_DIR_PATTERN='(Code/|code/|src/|lib/|app/|packages/)'
  WRITE_PATTERN='(>\s*|>>\s*|tee\s+|cp\s+.*\s|mv\s+.*\s)'

  if echo "$COMMAND" | grep -qE "${WRITE_PATTERN}.*${CODE_DIR_PATTERN}|${CODE_DIR_PATTERN}.*${WRITE_PATTERN}"; then
    # Bash command writes to a code directory — extract the path for governance check
    FILE_PATH=$(echo "$COMMAND" | grep -oE "(Code|code|src|lib|app|packages)/[^ \"']*" | head -1)
  fi

  if [ -z "$FILE_PATH" ]; then
    # Also catch mkdir -p in code dirs (precursor to writing)
    if echo "$COMMAND" | grep -qE 'mkdir\s+(-p\s+)?.*'"$CODE_DIR_PATTERN"; then
      FILE_PATH=$(echo "$COMMAND" | grep -oE "(Code|code|src|lib|app|packages)/[^ \"']*" | head -1)
    fi
  fi

  if [ -z "$FILE_PATH" ]; then
    exit 0  # Bash command doesn't write to code directories, allow
  fi
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
  if head -25 "$f" | grep -q "FROZEN"; then
    HAS_PVD=true
    break
  fi
done

if [ "$HAS_PVD" = false ]; then
  # Try Path B
  for f in "$PROJECT_DIR"/Specs/*Product_Brief*; do
    [ -f "$f" ] || continue
    if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
    if head -25 "$f" | grep -q "FROZEN"; then
      HAS_BRIEF=true
      break
    fi
  done
  for f in "$PROJECT_DIR"/Specs/*PRD*; do
    [ -f "$f" ] || continue
    if echo "$f" | grep -qi "TEMPLATE"; then continue; fi
    if head -25 "$f" | grep -q "FROZEN"; then
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
  if head -25 "$f" | grep -q "FROZEN"; then
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
  if head -25 "$f" | grep -q "FROZEN"; then
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
  if head -25 "$f" | grep -q "FROZEN"; then
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
  emit_event "gate.spec" "block" "file_path=$FILE_PATH" "missing=$MISSING_LIST"
  exit 2  # BLOCK
fi

emit_event "gate.spec" "allow" "file_path=$FILE_PATH"
exit 0  # All specs frozen + active WO, allow
