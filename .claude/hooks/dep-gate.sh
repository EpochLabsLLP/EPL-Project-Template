#!/bin/bash
# Hook: PreToolUse -> Bash
# DEPENDENCY GATE: Blocks package installations without prior /dep-check vetting.
#
# Detects package install commands (npm, pip, cargo, go, yarn, pnpm) and blocks
# them with instructions to run /dep-check first.
#
# Allows safe commands:
#   - npm install (no args) — installs from lockfile
#   - pip install -r requirements.txt — installs from requirements file
#   - pip install -e . — editable install of current project
#   - npm ci — clean install from lockfile
#
# Exit codes:
#   0 = allow (not a package install, or a safe install pattern)
#   2 = block (package install detected without /dep-check)

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMAND=$(python "$HOOK_DIR/parse_hook_input.py" tool_input.command)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# --- Safe patterns (allow without /dep-check) ---

# npm install / npm ci with no package argument (installs from lockfile)
if echo "$COMMAND" | grep -qE '^npm\s+(install|ci)\s*$'; then
  exit 0
fi

# yarn install with no package argument
if echo "$COMMAND" | grep -qE '^yarn\s+(install)?\s*$'; then
  exit 0
fi

# pnpm install with no package argument
if echo "$COMMAND" | grep -qE '^pnpm\s+install\s*$'; then
  exit 0
fi

# pip install -r (from requirements file)
if echo "$COMMAND" | grep -qE 'pip\s+install\s+(-r|--requirement)\s'; then
  exit 0
fi

# pip install -e . (editable current project)
if echo "$COMMAND" | grep -qE 'pip\s+install\s+-e\s+\.'; then
  exit 0
fi

# pip install . (current project)
if echo "$COMMAND" | grep -qE 'pip\s+install\s+\.\s*$'; then
  exit 0
fi

# --- Detect package install commands ---

# npm/yarn/pnpm install/add with a package name
if echo "$COMMAND" | grep -qE '(npm|yarn|pnpm)\s+(install|add|i)\s+[a-zA-Z@]'; then
  PACKAGE=$(echo "$COMMAND" | grep -oE '(npm|yarn|pnpm)\s+(install|add|i)\s+\S+' | awk '{print $NF}')
  echo "DEPENDENCY GATE BLOCKED: Package install detected."
  echo ""
  echo "Run /dep-check $PACKAGE before installing."
  echo "This checks: license compliance (no GPL), security advisories,"
  echo "maintenance status, and compatibility."
  echo ""
  echo "Only proceed after /dep-check approves the dependency."
  exit 2
fi

# pip install with a package name
if echo "$COMMAND" | grep -qE 'pip3?\s+install\s+[a-zA-Z]'; then
  PACKAGE=$(echo "$COMMAND" | grep -oE 'pip3?\s+install\s+\S+' | awk '{print $NF}')
  echo "DEPENDENCY GATE BLOCKED: Package install detected."
  echo ""
  echo "Run /dep-check $PACKAGE before installing."
  echo "This checks: license compliance (no GPL), security advisories,"
  echo "maintenance status, and compatibility."
  echo ""
  echo "Only proceed after /dep-check approves the dependency."
  exit 2
fi

# cargo add
if echo "$COMMAND" | grep -qE 'cargo\s+add\s+[a-zA-Z]'; then
  PACKAGE=$(echo "$COMMAND" | grep -oE 'cargo\s+add\s+\S+' | awk '{print $NF}')
  echo "DEPENDENCY GATE BLOCKED: Package install detected."
  echo ""
  echo "Run /dep-check $PACKAGE before installing."
  echo "This checks: license compliance (no GPL), security advisories,"
  echo "maintenance status, and compatibility."
  echo ""
  echo "Only proceed after /dep-check approves the dependency."
  exit 2
fi

# go get
if echo "$COMMAND" | grep -qE 'go\s+get\s+[a-zA-Z]'; then
  PACKAGE=$(echo "$COMMAND" | grep -oE 'go\s+get\s+\S+' | awk '{print $NF}')
  echo "DEPENDENCY GATE BLOCKED: Package install detected."
  echo ""
  echo "Run /dep-check $PACKAGE before installing."
  echo "This checks: license compliance (no GPL), security advisories,"
  echo "maintenance status, and compatibility."
  echo ""
  echo "Only proceed after /dep-check approves the dependency."
  exit 2
fi

# Not a package install command
exit 0
