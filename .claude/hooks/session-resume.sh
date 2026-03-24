#!/bin/bash
# Hook: SessionStart -> resume
# Fires when resuming a previous conversation (claude --continue / --resume).
# Lighter than startup — you already have conversation context, so this just
# re-anchors to the Work Ledger and shows current work items.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/observe.sh" 2>/dev/null
source "$HOOK_DIR/checkpoint.sh" 2>/dev/null
source "$HOOK_DIR/instance-id.sh" 2>/dev/null
source "$HOOK_DIR/progress-log.sh" 2>/dev/null
PROJECT_DIR="$CLAUDE_PROJECT_DIR"
WORK_LEDGER="$PROJECT_DIR/Specs/Work_Ledger.md"
GAP_TRACKER="$PROJECT_DIR/Specs/gap_tracker.md"
TRACE_SCRIPT="$PROJECT_DIR/.claude/skills/trace-check/scripts/validate_traceability.py"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)

# Read existing instance ID (don't regenerate on resume — same session)
INSTANCE_ID=$(get_instance_id 2>/dev/null || echo "unknown")

emit_event "session.resume" "info" "instance_id=$INSTANCE_ID"

# --- Stop Work Check ---
STOP_WORK="$PROJECT_DIR/.claude/stop-work.md"
if [ -f "$STOP_WORK" ]; then
  echo "[STOP WORK ORDER — ALL WORK HALTED]"
  echo ""
  cat "$STOP_WORK"
  echo ""
  echo "DO NOT proceed with any work. Address the stop-work order first."
  log_progress "SESSION RESUME | Stop-work order active — halted"
  exit 0
fi

echo "[SESSION RESUMED — RE-ANCHORING]"
echo "[INSTANCE: $INSTANCE_ID]"

# --- Auto-refresh Work Ledger via trace-check ---
if [ -f "$TRACE_SCRIPT" ]; then
  TRACE_OUTPUT=$(PYTHONIOENCODING=utf-8 $PYTHON "$TRACE_SCRIPT" "$PROJECT_DIR" --quick 2>&1)
  TRACE_EXIT=$?
  # Regenerate the full ledger silently
  PYTHONIOENCODING=utf-8 $PYTHON "$TRACE_SCRIPT" "$PROJECT_DIR" > /dev/null 2>&1
  [ $TRACE_EXIT -eq 0 ] && echo "[$TRACE_OUTPUT]"
  [ $TRACE_EXIT -eq 1 ] && echo "[$TRACE_OUTPUT — run /trace-check for details]"
fi

# --- Work Ledger summary ---
if [ -f "$WORK_LEDGER" ]; then
  # Show status line and active Work Orders
  STATUS=$(grep -m1 "^\*\*Status:\*\*" "$WORK_LEDGER" 2>/dev/null | sed 's/\*\*Status:\*\* //')
  [ -n "$STATUS" ] && echo "LEDGER STATUS: $STATUS"

  echo ""
  echo "[ACTIVE WORK ORDERS]"
  sed -n '/## Active Work Orders/,/^## /p' "$WORK_LEDGER" 2>/dev/null | head -15

  echo ""
  echo "[PROGRESS]"
  sed -n '/## Progress/,/^$/p' "$WORK_LEDGER" 2>/dev/null | head -5
else
  echo "[NO WORK LEDGER] No specs found yet."
fi

# --- Gap Tracker: Just open items ---
if [ -f "$GAP_TRACKER" ]; then
  NEXT_TASK=$(grep -m1 "^- \[ \]" "$GAP_TRACKER" 2>/dev/null | sed 's/^- \[ \] //')
  TOTAL_OPEN=$(grep -c "^- \[ \]" "$GAP_TRACKER" 2>/dev/null || echo "0")
  [ -n "$NEXT_TASK" ] && echo "NEXT TASK: $NEXT_TASK ($TOTAL_OPEN total open)"

  # Scope guard (pipe to grep -c; do NOT use || echo "0" — it doubles output)
  TIER0=$(sed -n '/## Tier 0/,/## Tier [1-9]/p' "$GAP_TRACKER" 2>/dev/null | grep -c "^- \[ \]")
  if [ "$TIER0" != "0" ] && [ "$TIER0" != "" ]; then
    echo "SCOPE GUARD: $TIER0 Tier 0 defect(s) open — resolve these first."
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

# --- Progress Log (cross-instance awareness) ---
show_recent_progress 10

# --- Checkpoint Recovery ---
show_checkpoint "resume"
