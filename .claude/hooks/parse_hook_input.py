"""Utility: Parse hook JSON input and extract a field.
Usage: echo '{"tool_input":{"command":"..."}}' | python parse_hook_input.py tool_input.command
Backslashes in values are normalized to forward slashes (Windows path compat).
"""
import sys
import json


def extract(data, path):
    for key in path.split("."):
        if isinstance(data, dict):
            data = data.get(key, "")
        else:
            return ""
    result = str(data)
    return result.replace("\\", "/")


if __name__ == "__main__":
    field_path = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
        print(extract(data, field_path))
    except Exception:
        print("")
