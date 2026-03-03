---
name: governance-health
description: Validate that the governance system (hooks, rules, skills, scripts) is intact and functional. Use to diagnose governance failures, verify setup after template sync, or audit a project's template compliance.
user_invocable: true
---

# governance-health

Validates the integrity of the project's governance system. No changes are made — this is a read-only health check.

## When to Use

- After running `/template-sync` to verify everything landed correctly
- When hooks seem to not be firing (diagnosis)
- When setting up a new project from the template
- Periodically to ensure nothing has drifted

## How to Invoke

```
/governance-health
```

## Execution

Run through each check below. Report results as a health card with pass/warn/fail indicators.

### Check 1: Hook Files Exist

Read `.claude/settings.json` and extract all hook command paths. For each:
- Verify the referenced `.sh` or `.py` file exists on disk
- Report: `[PASS]` if exists, `[FAIL]` if missing

### Check 2: parse_hook_input.py Functional

Run a quick test:
```bash
echo '{"tool_input":{"file_path":"test.md"}}' | python "$CLAUDE_PROJECT_DIR/.claude/hooks/parse_hook_input.py" tool_input.file_path
```
Expected output: `test.md`
- Report: `[PASS]` if correct output, `[FAIL]` if error or wrong output

### Check 3: Python Available

```bash
python --version
```
- Report: `[PASS]` with version, `[FAIL]` if not found

### Check 4: Skills Have SKILL.md

For each skill referenced in CLAUDE.md's skill table:
- Check `.claude/skills/{name}/SKILL.md` exists
- Report: `[PASS]` per skill, `[WARN]` if missing

### Check 5: Rules Files Exist

For each rule referenced in CLAUDE.md or loaded by `.claude/rules/`:
- Check the file exists
- Report: `[PASS]` per rule, `[WARN]` if missing

### Check 6: TEMPLATE_MANIFEST.json Consistent

If `TEMPLATE_MANIFEST.json` exists:
- For each file listed in infrastructure and template categories, verify it exists
- Report: `[PASS]` if all present, `[WARN]` with list of missing files

### Check 7: settings.local.json Exists

- Check `.claude/settings.local.json` exists
- Report: `[PASS]` if exists, `[WARN]` with instruction to copy from `.example`

### Check 8: Template Version Tracked

- Check `.template_version` exists
- Report: `[PASS]` with version, `[WARN]` if missing (project may predate versioning)

### Check 9: Governance Files Unmodified

If template repo path is known (from `/template-sync` or ask Nathan):
- Compare infrastructure file hashes between template and project
- Report: `[PASS]` if identical, `[WARN]` with list of drifted files

## Output Format

```
=== GOVERNANCE HEALTH CHECK ===

[PASS] Hook files: All 9 hooks present
[PASS] parse_hook_input.py: Functional (Python 3.14)
[PASS] Python: 3.14.0
[PASS] Skills: 15/15 SKILL.md files present
[PASS] Rules: 6/6 rule files present
[WARN] Manifest: 2 infrastructure files missing (.claude/skills/new-skill/SKILL.md)
[WARN] settings.local.json: Missing — copy from .claude/settings.local.json.example
[PASS] Template version: 2.2.0
[PASS] Governance integrity: All files match template

RESULT: 7 PASS, 2 WARN, 0 FAIL
```

Keep the output concise. Do not dump file contents — just report status.
