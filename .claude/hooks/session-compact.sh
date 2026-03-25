#!/bin/bash
# Hook: SessionStart -> compact
# Fires after context compaction (auto-compact at ~95% or manual /compact).
# This is the MOST CRITICAL anti-drift hook. After compaction, Claude has lost
# all in-progress nuance. This script re-injects the full project context.
#
# IMPORTANT: Everything output here becomes Claude's only knowledge of the
# project state. Be thorough — compaction is where drift kills projects.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/observe.sh" 2>/dev/null
source "$HOOK_DIR/checkpoint.sh" 2>/dev/null
source "$HOOK_DIR/instance-id.sh" 2>/dev/null
source "$HOOK_DIR/progress-log.sh" 2>/dev/null
PROJECT_DIR="$CLAUDE_PROJECT_DIR"
WORK_LEDGER="$PROJECT_DIR/Specs/Work_Ledger.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"
SESSIONS_DIR="$PROJECT_DIR/Sessions"
TRACE_SCRIPT="$PROJECT_DIR/.claude/skills/trace-check/scripts/validate_traceability.py"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)

# Read existing instance ID (don't regenerate on compact — same session)
INSTANCE_ID=$(get_instance_id 2>/dev/null || echo "unknown")

emit_event "session.compact" "info" "instance_id=$INSTANCE_ID"

# --- Stop Work Check ---
STOP_WORK="$PROJECT_DIR/.claude/stop-work.md"
if [ -f "$STOP_WORK" ]; then
  echo "[STOP WORK ORDER — ALL WORK HALTED]"
  echo ""
  cat "$STOP_WORK"
  echo ""
  echo "DO NOT proceed with any work. Address the stop-work order first."
  log_progress "SESSION COMPACT | Stop-work order active — halted"
  exit 0
fi

echo "[COMPACTION RECOVERY — FULL CONTEXT RELOAD]"
echo "[INSTANCE: $INSTANCE_ID]"
echo "Context was just compacted. Pre-compaction memory is UNRELIABLE."
echo "You MUST re-read any files you were working on before making edits."
echo "Do NOT rely on memory for: file contents, line numbers, variable names, partial implementations."

# --- Auto-refresh Work Ledger via trace-check ---
if [ -f "$TRACE_SCRIPT" ]; then
  TRACE_OUTPUT=$(PYTHONIOENCODING=utf-8 $PYTHON "$TRACE_SCRIPT" "$PROJECT_DIR" --quick 2>&1)
  TRACE_EXIT=$?
  # Regenerate the full ledger silently
  PYTHONIOENCODING=utf-8 $PYTHON "$TRACE_SCRIPT" "$PROJECT_DIR" > /dev/null 2>&1
  echo ""
  if [ $TRACE_EXIT -eq 0 ]; then
    echo "[$TRACE_OUTPUT]"
  elif [ $TRACE_EXIT -eq 1 ]; then
    echo "[$TRACE_OUTPUT — ERRORS DETECTED, run /trace-check for details]"
  else
    echo "[Traceability check failed — run /trace-check manually]"
  fi
fi

# --- Full Work Ledger ---
if [ -f "$WORK_LEDGER" ]; then
  echo ""
  echo "[WORK LEDGER]"
  cat "$WORK_LEDGER"
else
  echo ""
  echo "[NO WORK LEDGER] No specs found yet. Operating without project status."
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

# --- Agent Mail: Inbox Check ---
INBOX_DIR="$PROJECT_DIR/.claude/inbox"
if [ -d "$INBOX_DIR" ]; then
  MAIL_COUNT=$(find "$INBOX_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$MAIL_COUNT" -gt 0 ]; then
    URGENT_COUNT=$(grep -rl "^priority: urgent" "$INBOX_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
    echo ""
    if [ "$URGENT_COUNT" -gt 0 ]; then
      echo "[INBOX: $MAIL_COUNT message(s), $URGENT_COUNT URGENT]"
      echo "URGENT MAIL — read and address before other work."
    else
      echo "[INBOX: $MAIL_COUNT message(s)]"
    fi
    echo "Run /mail --check to read messages."
  fi
fi

# --- Mail Ledger: Pending Actions ---
MAIL_LEDGER="$PROJECT_DIR/.claude/mail-ledger.md"
if [ -f "$MAIL_LEDGER" ]; then
  PENDING_COUNT=$(grep -c "status:pending" "$MAIL_LEDGER" 2>/dev/null || echo 0)
  if [ "$PENDING_COUNT" -gt 0 ]; then
    echo "[MAIL LEDGER: $PENDING_COUNT message(s) pending action]"
  fi
fi

# --- Progress Log (cross-instance awareness — full history after compact) ---
show_recent_progress 20

# --- Checkpoint Recovery (highest value here — agent lost all context) ---
show_checkpoint "compact"

log_progress "SESSION COMPACT | Context compacted — re-anchoring"

echo ""
echo "CRITICAL: Re-read source files before making any edits."
