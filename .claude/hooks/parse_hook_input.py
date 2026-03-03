"""Utility: Parse hook JSON input and extract a field.
Usage: echo '{"tool_input":{"command":"..."}}' | python parse_hook_input.py tool_input.command
       python parse_hook_input.py --check-frozen <file_path>

Backslashes in values are normalized to forward slashes (Windows path compat).
Errors are reported to stderr (visible in Claude Code hook output) but never block.
"""
import sys
import json
import os
import re


def extract(data, path):
    """Extract a nested field from a dict using dot notation."""
    for key in path.split("."):
        if isinstance(data, dict):
            data = data.get(key, "")
        else:
            return ""
    result = str(data)
    return result.replace("\\", "/")


def check_frozen(file_path):
    """Check if a file has FROZEN status in its first 15 lines.

    Checks for ACTUAL status declarations, not just mentions of the word:
      1. Explicit marker: <!-- STATUS: FROZEN -->
      2. Markdown status line: **Status:** FROZEN or **Status**: FROZEN
      3. Status field: Status: FROZEN (at line start or after whitespace)

    Does NOT match instructional text like "Change Status to FROZEN".
    Returns 'true' or 'false' as string (for bash consumption).
    """
    if not file_path or not os.path.isfile(file_path):
        return "false"

    # Skip TEMPLATE_ files — they contain FROZEN in instructions, not as status
    basename = os.path.basename(file_path)
    if basename.startswith("TEMPLATE_") or basename.startswith("SESSION_TEMPLATE"):
        return "false"

    frozen_patterns = [
        r'<!--\s*STATUS:\s*FROZEN\s*-->',          # HTML comment marker
        r'\*\*Status:?\*\*:?\s*FROZEN',              # Bold markdown: **Status:** FROZEN
        r'^\s*Status:\s*FROZEN',                     # Plain: Status: FROZEN
        r'^\s*\|\s*Status\s*\|\s*FROZEN\s*\|',      # Table: | Status | FROZEN |
    ]

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= 15:
                    break
                for pattern in frozen_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        return "true"
        return "false"
    except Exception as e:
        print(f"[parse_hook_input] Warning: Could not check frozen status of {file_path}: {e}", file=sys.stderr)
        return "false"


if __name__ == "__main__":
    args = sys.argv[1:]

    # Mode: --check-frozen <file_path>
    if args and args[0] == "--check-frozen":
        if len(args) > 1:
            print(check_frozen(args[1]))
        else:
            print("false")
        sys.exit(0)

    # Default mode: extract field from JSON stdin
    field_path = args[0] if args else ""
    try:
        data = json.load(sys.stdin)
        print(extract(data, field_path))
    except Exception as e:
        print(f"[parse_hook_input] Warning: Failed to parse hook input: {e}", file=sys.stderr)
        print("")
