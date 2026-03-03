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
PROJECT_DIR="$CLAUDE_PROJECT_DIR"
COMMAND=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.command)

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
  TRACE_OUTPUT=$(PYTHONIOENCODING=utf-8 python "$TRACE_SCRIPT" "$PROJECT_DIR" --quick 2>&1)
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
  ENV_FILES=$(git -C "$PROJECT_DIR" diff --cached --name-only 2>/dev/null | grep -E '\.env($|\.)')
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

echo "{\"systemMessage\":\"$MSG Consider running /code-review if this completes a module.\"}"
exit 0
