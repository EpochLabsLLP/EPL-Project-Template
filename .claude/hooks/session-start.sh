#!/bin/bash
# Hook: SessionStart -> startup
# Fires on fresh session start. Outputs project context to stdout,
# which Claude Code injects as conversation context for the agent.
#
# This is the primary anti-drift mechanism. It forces every new session
# to re-anchor to the project's status, traceability health, and next task.

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
WORK_LEDGER="$PROJECT_DIR/Specs/Work_Ledger.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"
SESSIONS_DIR="$PROJECT_DIR/Sessions"
TRACE_SCRIPT="$PROJECT_DIR/.claude/skills/trace-check/scripts/validate_traceability.py"

echo "[SESSION START — MISSION ANCHOR]"

# --- Auto-refresh Work Ledger via trace-check ---
TRACE_STATUS=""
if [ -f "$TRACE_SCRIPT" ]; then
  TRACE_OUTPUT=$(PYTHONIOENCODING=utf-8 python "$TRACE_SCRIPT" "$PROJECT_DIR" --quick 2>&1)
  TRACE_EXIT=$?
  # Regenerate the full ledger silently
  PYTHONIOENCODING=utf-8 python "$TRACE_SCRIPT" "$PROJECT_DIR" > /dev/null 2>&1
  if [ $TRACE_EXIT -eq 0 ]; then
    TRACE_STATUS="$TRACE_OUTPUT"
  elif [ $TRACE_EXIT -eq 1 ]; then
    TRACE_STATUS="$TRACE_OUTPUT — run /trace-check for details"
  else
    TRACE_STATUS="Traceability check failed (non-blocking)"
  fi
fi

# --- Work Ledger (project status + traceability) ---
if [ -f "$WORK_LEDGER" ]; then
  echo ""
  [ -n "$TRACE_STATUS" ] && echo "[$TRACE_STATUS]"
  echo "[WORK LEDGER]"
  cat "$WORK_LEDGER"
else
  echo ""
  echo "[NO WORK LEDGER] No specs found yet. Start with: /init-doc pvd"
fi

# --- Gap Tracker ---
if [ -f "$GAP_TRACKER" ]; then
  echo ""
  echo "[GAP TRACKER — OPEN ITEMS]"

  # Count open items per tier (pipe to grep -c; do NOT use || echo "0" — it doubles output)
  TIER0=$(sed -n '/## Tier 0/,/## Tier [1-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  TIER1=$(sed -n '/## Tier 1/,/## Tier [2-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  TIER2=$(sed -n '/## Tier 2/,/## Tier [3-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  TIER3=$(sed -n '/## Tier 3/,/^$/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")

  echo "Tier 0 (Critical): $TIER0 | Tier 1 (Functional): $TIER1 | Tier 2 (Quality): $TIER2 | Tier 3 (Enhancement): $TIER3"

  # First unchecked item = next task
  NEXT_TASK=$(grep -m1 "^- \[ \]" "$GAP_TRACKER" 2>/dev/null | sed 's/^- \[ \] //')
  [ -n "$NEXT_TASK" ] && echo "NEXT TASK: $NEXT_TASK"

  # Scope guard
  if [ "$TIER0" != "0" ] && [ "$TIER0" != "" ]; then
    echo "SCOPE GUARD: Tier 0 defects open. Resolve ALL Tier 0 items before any other work."
  fi
else
  echo ""
  echo "[NO GAP TRACKER] Create Specs/gap_tracker.md to track work items by priority tier."
fi

# --- Last Session Summary ---
if [ -d "$SESSIONS_DIR" ]; then
  LATEST=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | head -1)
  if [ -n "$LATEST" ]; then
    echo ""
    echo "[LAST SESSION: $(basename "$LATEST")]"
    tail -20 "$LATEST"
  fi
fi

# --- Template Awareness (only when something is missing) ---
SPECS_DIR="$PROJECT_DIR/Specs"
HAS_PRODUCT_SPEC=false
for f in "$SPECS_DIR"/*PVD* "$SPECS_DIR"/*PRD* "$SPECS_DIR"/*Product_Brief* ; do
  if [ -f "$f" ]; then
    BNAME=$(basename "$f")
    if ! echo "$BNAME" | grep -q "^TEMPLATE_"; then
      HAS_PRODUCT_SPEC=true
      break
    fi
  fi
done

if [ "$HAS_PRODUCT_SPEC" = false ]; then
  echo ""
  echo "[TEMPLATE AWARENESS] No product spec found. Start with: /init-doc pvd"
  echo "Available types: pvd, prd, brief, es, ux, bp, tp, wo, dr"
fi

if [ ! -f "$PROJECT_DIR/.claude/settings.local.json" ]; then
  echo ""
  echo "[WARNING] settings.local.json missing. Copy from .claude/settings.local.json.example for optimized permissions."
fi

echo ""
echo "Read the above context carefully before starting work."
