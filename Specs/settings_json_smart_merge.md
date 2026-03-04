# Settings.json Smart Merge — Engineering Spec

| Field | Value |
|-------|-------|
| **Version** | 1 |
| **Status** | DRAFT |
| **Date** | 2026-03-03 |
| **Author** | Nathan / Claude |
| **Component** | `template_sync.py` |

---

## 1. Problem Statement

`settings.json` is scaffolding — project-owned, never overwritten by `template_sync.py`. This is correct for the `permissions` block (projects customize Python paths, tool allowlists, etc.), but creates a gap for the `hooks` block.

When a new template version adds a hook (new `.sh` file in `.claude/hooks/`), the sync engine deploys the hook script (infrastructure, overwritten) but **cannot register it** in `settings.json` (scaffolding, untouched). The project gets the engine part but not the wiring.

Result: older projects that sync to a newer template silently miss new hook registrations.

---

## 2. Design Constraints

1. **Never destroy project permissions.** The `permissions` block is fully project-owned. The merge must not touch it.
2. **Never remove hooks.** Projects may have added project-specific hooks alongside template hooks. The merge must be additive only.
3. **Idempotent.** Running the merge twice produces the same result.
4. **Backup before modify.** Same safety model as the rest of `template_sync.py` — back up the original before writing.
5. **Dry-run parity.** The sync report must show what hook registrations would be added/changed before `--apply`.
6. **Preserve formatting.** JSON output should be human-readable (indented, consistent key order).

---

## 3. Proposed Architecture

### 3.1 New Manifest Section: `hook_registrations`

Add a new top-level key to `TEMPLATE_MANIFEST.json`:

```json
{
  "template_version": "2.3.0",
  "hook_registrations": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh\"",
            "timeout": 15
          }
        ]
      },
      {
        "matcher": "resume",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-resume.sh\"",
            "timeout": 15
          }
        ]
      },
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-compact.sh\"",
            "timeout": 15
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/block-dangerous.sh\"",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/commit-gate.sh\"",
            "timeout": 15
          },
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/dep-gate.sh\"",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/protect-frozen-files.sh\"",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/spec-gate.sh\"",
            "timeout": 15
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/template-guard.sh\"",
            "timeout": 5
          }
        ]
      }
    ]
  },
  "categories": { ... }
}
```

**Rationale:** The manifest already declares what files exist in each category. Adding the expected hook registrations makes the manifest the single source of truth for both files *and* wiring.

### 3.2 Merge Algorithm

New function: `merge_settings_json(template_dir, project_dir, manifest) → (changes, merged_json)`

**Merge rules:**

1. Load project's `settings.json`. If missing, start from `{}`.
2. Load `hook_registrations` from manifest.
3. **Preserve all existing keys** in project settings (permissions, any unknown keys).
4. For each hook event type (e.g., `SessionStart`, `PreToolUse`):
   a. For each template matcher entry:
      - **Match by matcher string** (e.g., `"Bash"`, `"Edit|Write"`, `"startup"`).
      - If the project has a matching entry, merge the hooks array:
        - Identify hooks by `command` string (the unique key).
        - Add any template hooks not present in the project.
        - Update `timeout` values if template specifies a different value (template wins for template-owned hooks).
        - **Never remove** hooks that exist in the project but not in the template (project-specific hooks).
      - If no matching entry exists in the project, add the entire matcher block.
   b. **Never remove** matcher entries that exist in the project but not in the template.
5. Return the list of changes made (for reporting) and the merged JSON.

**Hook identity:** A hook is identified by its `command` string. Two hooks with the same command are the same hook. This is safe because all template hooks use `$CLAUDE_PROJECT_DIR/.claude/hooks/{name}.sh` which is unique per hook.

### 3.3 Integration with Sync Flow

Modify `sync_report()` to also report on settings.json merge status:
- New report key: `"settings_hooks"` — list of hook registrations that would be added/updated.

Modify `apply_sync()` to:
1. After file sync, run `merge_settings_json()`.
2. If changes needed, back up `settings.json` to `.template_backup/`, write merged version.

Modify `print_report()` to display settings merge info:
```
SETTINGS.JSON HOOK MERGE (3 changes):
  + PreToolUse/Bash: adding new-hook.sh (timeout 5)
  ~ PreToolUse/Edit|Write: updating spec-gate.sh timeout 10→15
  = SessionStart/startup: up to date
```

### 3.4 Move settings.json to New Category

Change `settings.json` from `scaffolding` to a new category: `"managed_scaffolding"`.

```json
"managed_scaffolding": {
  "description": "Project-owned but with template-managed sections. Hooks block is merged; permissions block is untouched.",
  "files": [
    ".claude/settings.json"
  ]
}
```

This preserves the "never fully overwrite" behavior while signaling that the file has a managed component.

---

## 4. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Project has no `settings.json` | Create from template with full hook registrations + empty permissions block |
| Project added custom hooks under `Bash` matcher | Preserved — template hooks added alongside, custom hooks untouched |
| Project added a custom matcher (e.g., `"NotebookEdit"`) | Preserved — template doesn't know about it, leaves it alone |
| Project modified a template hook's timeout | Template wins (infrastructure-owned). Reported as update. |
| Project removed a template hook intentionally | Re-added on sync. Documented as known limitation. Projects that need to disable a template hook should use an empty `command` override (future enhancement). |
| `settings.json` has malformed JSON | Sync aborts with clear error, no changes made |
| `permissions.allow` has project-specific Python paths | Untouched — merge only operates on `hooks` block |

---

## 5. Reporting Example

```
=== TEMPLATE SYNC REPORT (DRY RUN) ===
Project version: 2.1.0
Template version: 2.3.0

WILL CREATE (2):
  + .claude/hooks/new-hook.sh  (infrastructure)
  + .claude/rules/new-rule.md  (infrastructure)

SETTINGS.JSON HOOK MERGE (2 changes):
  + PreToolUse/Bash: adding new-hook.sh (timeout 5)
  + SessionStart/startup: adding new-hook-2.sh (timeout 10)

SKIPPED — PROJECT-OWNED (2):
  - CLAUDE.md
  - README.md

UP TO DATE (38):
  = .claude/hooks/block-dangerous.sh
  ...

STATUS: 4 action(s) needed.
Run with --apply to execute these changes.
```

---

## 6. Implementation Scope

| File | Change |
|------|--------|
| `template_sync.py` | Add `merge_settings_json()`, update `sync_report()`, `apply_sync()`, `print_report()` |
| `TEMPLATE_MANIFEST.json` | Add `hook_registrations` block, move `settings.json` to `managed_scaffolding` |
| `/template-sync` SKILL.md | Update to mention hook merge in output description |
| `/governance-health` SKILL.md | Add check: "Are all template hook registrations present in settings.json?" |

Estimated additions: ~100 lines to `template_sync.py`, ~40 lines to manifest.

---

## 7. Testing Strategy

1. **Unit test — additive merge:** Project has 8 hooks, template adds 1 → result has 9.
2. **Unit test — idempotent:** Run merge twice → identical output.
3. **Unit test — custom hooks preserved:** Project has custom hook under `Bash` → still present after merge.
4. **Unit test — missing settings.json:** No file → created with full template hooks.
5. **Integration test in EPL-Test-Project:** Sync from v2.2.0 → v2.3.0, verify new hook fires.
6. **Edge case — malformed JSON:** Verify clean error, no partial writes.

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | 2026-03-03 | Initial spec | Nathan / Claude |
