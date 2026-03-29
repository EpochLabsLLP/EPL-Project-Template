#!/bin/bash
# Hook: PreToolUse -> Bash
# COMMIT GATE: Blocks git commits when traceability is broken or secrets are detected.
#
# Replaces the advisory pre-commit-reminder.sh with hard enforcement.
#
# Checks (in order):
# 1. Is this a git commit command? (If not, exit 0 — allow)
# 2. Traceability validation (--quick mode): broken chains → BLOCK
# 3. Secrets scan on staged diff: any secrets → BLOCK
# 4. All clear → exit 0 with advisory systemMessage
#
# Exit codes:
#   0 = allow (with optional systemMessage)
#   2 = block (traceability errors or secrets found)
#
# Fail-open: If validate_traceability.py crashes or is missing, WARN but allow.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/observe.sh" 2>/dev/null
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$HOOK_DIR/../.." && pwd)}"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
COMMAND=$($PYTHON "$HOOK_DIR/parse_hook_input.py" tool_input.command 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Only gate git commit commands
if ! echo "$COMMAND" | grep -qE 'git\s+commit'; then
  exit 0
fi

BLOCKED=false
BLOCK_REASONS=""
WARNINGS=""

# --- Check 1: Traceability validation ---
TRACE_SCRIPT="$PROJECT_DIR/.claude/skills/trace-check/scripts/validate_traceability.py"

if [ -f "$TRACE_SCRIPT" ]; then
  TRACE_OUTPUT=$(PYTHONIOENCODING=utf-8 $PYTHON "$TRACE_SCRIPT" "$PROJECT_DIR" --quick 2>&1)
  TRACE_EXIT=$?

  if [ $TRACE_EXIT -eq 1 ]; then
    BLOCKED=true
    BLOCK_REASONS="TRACEABILITY ERRORS: Broken chains detected. Run /trace-check to see details.\n$TRACE_OUTPUT"
  elif [ $TRACE_EXIT -eq 2 ]; then
    # Script crashed — fail-open with warning
    WARNINGS="Traceability check encountered an error (non-blocking): $TRACE_OUTPUT"
  fi
  # Exit 0 = clean, continue
else
  WARNINGS="validate_traceability.py not found — traceability check skipped"
fi

# --- Check 2: Secrets scan on staged diff ---
STAGED_DIFF=$(git -C "$PROJECT_DIR" diff --cached --diff-filter=d 2>/dev/null)

if [ -n "$STAGED_DIFF" ]; then
  # Check for common secret patterns
  SECRET_PATTERNS='(sk-[a-zA-Z0-9]{20,}|pk_live_|pk_test_|password\s*[=:]\s*["\x27][^"\x27]+["\x27]|token\s*[=:]\s*["\x27][^"\x27]+["\x27]|Bearer\s+[a-zA-Z0-9._\-]+|PRIVATE\s+KEY|-----BEGIN\s+(RSA|EC|DSA|OPENSSH)\s+PRIVATE\s+KEY)'

  SECRET_HITS=$(echo "$STAGED_DIFF" | grep -nE "$SECRET_PATTERNS" 2>/dev/null | grep -v 'SECRET_PATTERNS=' | head -5)

  if [ -n "$SECRET_HITS" ]; then
    BLOCKED=true
    BLOCK_REASONS="${BLOCK_REASONS}\nSECRETS DETECTED in staged changes:\n$SECRET_HITS\n\nRemove secrets before committing. API keys belong server-side, never in code."
  fi

  # Check for .env files being committed
  ENV_FILES=$(git -C "$PROJECT_DIR" diff --cached --name-only 2>/dev/null | grep -E '\.env($|\.)' | grep -v '\.example$')
  if [ -n "$ENV_FILES" ]; then
    BLOCKED=true
    BLOCK_REASONS="${BLOCK_REASONS}\n.ENV FILES staged for commit:\n$ENV_FILES\n\nAdd .env to .gitignore and unstage these files."
  fi
fi

# --- Decision ---
if [ "$BLOCKED" = true ]; then
  echo "COMMIT GATE BLOCKED"
  echo ""
  echo -e "$BLOCK_REASONS"
  echo ""
  echo "Fix the issues above before committing."
  emit_event "gate.commit" "block" "reason=traceability_or_secrets"
  exit 2  # BLOCK
fi

# --- Advisory (non-blocking) ---
MSG="Commit gate passed."
if [ -n "$WARNINGS" ]; then
  MSG="$MSG Warning: $WARNINGS."
fi

# Check if spec/WO files are in staged changes — remind about trace-check
SPEC_FILES=$(git -C "$PROJECT_DIR" diff --cached --name-only 2>/dev/null | grep -E '(Specs/|Testing/|WorkOrders/)' | head -3)
if [ -n "$SPEC_FILES" ]; then
  MSG="$MSG Spec/WO files modified — Work Ledger will be regenerated on next session start."
fi

# --- Advisory: WO coverage for code changes ---
# Check if code files are staged but no WO references them in the commit message
CODE_STAGED=$(git -C "$PROJECT_DIR" diff --cached --name-only 2>/dev/null | grep -E '(Code/|code/|src/|lib/|app/|packages/)' | head -1)
if [ -n "$CODE_STAGED" ]; then
  # Check if any WO is IN-PROGRESS (should be, if spec-gate allowed the writes)
  HAS_WO=false
  if [ -d "$PROJECT_DIR/WorkOrders" ]; then
    for wof in "$PROJECT_DIR"/WorkOrders/*.md; do
      [ -f "$wof" ] || continue
      case "$wof" in *TEMPLATE_*|*_Archive*) continue ;; esac
      if head -20 "$wof" | grep -qE 'IN-PROGRESS'; then
        HAS_WO=true
        break
      fi
    done
  fi
  if [ "$HAS_WO" = false ]; then
    MSG="$MSG WARNING: Code files staged but no Work Order is IN-PROGRESS. Create a WO for traceability."
  fi
fi

emit_event "gate.commit" "allow"
echo "{\"systemMessage\":\"$MSG Consider running /code-review if this completes a module.\"}"
exit 0
