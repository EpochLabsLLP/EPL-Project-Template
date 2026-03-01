#!/bin/bash
# Hook: SessionStart -> compact
# Fires after context compaction (auto-compact at ~95% or manual /compact).
# This is the MOST CRITICAL anti-drift hook. After compaction, Claude has lost
# all in-progress nuance. This script re-injects the full project context.
#
# IMPORTANT: Everything output here becomes Claude's only knowledge of the
# project state. Be thorough — compaction is where drift kills projects.

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
WORK_LEDGER="$PROJECT_DIR/Specs/Work_Ledger.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"
SESSIONS_DIR="$PROJECT_DIR/Sessions"

echo "[COMPACTION RECOVERY — FULL CONTEXT RELOAD]"
echo "Context was just compacted. Pre-compaction memory is UNRELIABLE."
echo "You MUST re-read any files you were working on before making edits."
echo "Do NOT rely on memory for: file contents, line numbers, variable names, partial implementations."

# --- Full Work Ledger ---
if [ -f "$WORK_LEDGER" ]; then
  echo ""
  echo "[WORK LEDGER]"
  cat "$WORK_LEDGER"
else
  echo ""
  echo "[NO WORK LEDGER] Run \`/trace-check\` to generate. Operating without project status."
fi

# --- Full Gap Tracker ---
if [ -f "$GAP_TRACKER" ]; then
  echo ""
  echo "[GAP TRACKER — FULL STATE]"
  cat "$GAP_TRACKER"

  # Highlight next task
  NEXT_TASK=$(grep -m1 "^- \[ \]" "$GAP_TRACKER" 2>/dev/null | sed 's/^- \[ \] //')
  [ -n "$NEXT_TASK" ] && echo "NEXT TASK: $NEXT_TASK"

  # Scope guard (pipe to grep -c; do NOT use || echo "0" — it doubles output)
  TIER0=$(sed -n '/## Tier 0/,/## Tier [1-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  if [ "$TIER0" != "0" ] && [ "$TIER0" != "" ]; then
    echo "SCOPE GUARD: $TIER0 Tier 0 defect(s) open — resolve these before any other work."
  fi
fi

# --- Last Session Summary ---
if [ -d "$SESSIONS_DIR" ]; then
  LATEST=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | head -1)
  if [ -n "$LATEST" ]; then
    echo ""
    echo "[LAST SESSION: $(basename "$LATEST")]"
    tail -25 "$LATEST"
  fi
fi

echo ""
echo "CRITICAL: Re-read source files before making any edits."
