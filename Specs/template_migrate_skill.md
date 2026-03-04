# /template-migrate Skill — Engineering Spec

| Field | Value |
|-------|-------|
| **Version** | 1 |
| **Status** | DRAFT |
| **Date** | 2026-03-03 |
| **Author** | Nathan / Claude |
| **Component** | `.claude/skills/template-migrate/SKILL.md` |

---

## 1. Problem Statement

`template_sync.py` handles routine upgrades (v2.x → v2.y) where the CLAUDE.md structure hasn't changed. But two scenarios fall outside its scope:

1. **Legacy migration:** A project predates the template entirely, or uses a v1.x CLAUDE.md that was monolithic (governance logic embedded directly in CLAUDE.md rather than in rules/hooks).
2. **Major version migration:** The CLAUDE.md scaffolding structure itself changes (e.g., new required sections, reorganized layout) between major template versions.

Both scenarios require touching the one file that `template_sync.py` explicitly protects: `CLAUDE.md`.

This is a **guided, human-in-the-loop** operation — not an automatic sync.

---

## 2. Design Constraints

1. **Human-in-the-loop.** Never overwrite CLAUDE.md without showing the user what will change and getting explicit confirmation.
2. **Extract, don't guess.** Parse project-specific data from the existing CLAUDE.md where possible; prompt the user to fill gaps rather than inventing values.
3. **Preserve project customizations.** If a project added custom sections to CLAUDE.md beyond the template structure, surface them for the user to decide what to keep.
4. **Idempotent.** Running `/template-migrate` on an already-current project is a no-op with a clean status message.
5. **Backup always.** Archive the old CLAUDE.md before writing the new one.
6. **Orchestrate full deployment.** After CLAUDE.md migration, run `template_sync.py` for everything else (hooks, rules, skills, settings.json merge).

---

## 3. Invocation

```
/template-migrate [--dry-run]
```

- Default: interactive guided migration.
- `--dry-run`: show what would change without modifying anything.

---

## 4. Migration Flow

### Phase 1: Detection

1. Read `.template_version` (or `0.0.0` if missing).
2. Read `claude_md_version` from CLAUDE.md metadata line (see companion spec).
3. Read template's current version from `TEMPLATE_MANIFEST.json`.
4. Determine migration type:

| Project State | Migration Type | Action |
|--------------|----------------|--------|
| No `.template_version`, no CLAUDE.md | **Fresh install** | Full scaffolding creation |
| No `.template_version`, has CLAUDE.md | **Legacy migration** | Extract + rebuild CLAUDE.md |
| `.template_version` < template, `claude_md_version` current | **Routine sync** | Delegate to `template_sync.py` (no CLAUDE.md work needed) |
| `.template_version` < template, `claude_md_version` outdated | **Major version migration** | Extract + rebuild CLAUDE.md, then sync |
| `.template_version` == template | **Up to date** | No-op, report clean status |

### Phase 2: Extraction (Legacy and Major Version Migrations Only)

Parse the existing CLAUDE.md and extract project-specific data into a structured object:

```json
{
  "project_name": "extracted or null",
  "project_description": "extracted or null",
  "load_bearing_walls": [
    {"decision": "text", "choice": "text", "rationale": "text"}
  ],
  "gold_rush_custom_bullet": "extracted or null",
  "custom_anti_patterns": ["any beyond the template defaults"],
  "custom_sections": [
    {"heading": "text", "content": "text"}
  ],
  "key_specs": ["list of spec references found"],
  "escalation_contacts": ["names found"],
  "cross_project_notes": "extracted or null"
}
```

**Extraction strategy by section:**

| CLAUDE.md Section | Extraction Method |
|-------------------|-------------------|
| Identity (project name, description) | Regex on `# {name} —` header and first paragraph |
| Load-bearing walls | Parse numbered list under `## Architecture — Load-Bearing Walls` |
| Gold Rush custom bullet | Find the project-specific bullet (differs from template defaults) |
| Anti-patterns | Compare against template defaults; flag any additions |
| Key specs | Parse the ordered list; note any project-added entries |
| Custom sections | Any `##` headings not in the template structure |
| Escalation rules | Parse the bullet list under `## Escalation Rules` |

**For unrecognized CLAUDE.md formats** (legacy v1.x or heavily customized):
- Do NOT attempt to parse. Instead, display the full existing CLAUDE.md to the user and present the new template with blank placeholders.
- Ask: "I can't automatically extract your project data from this format. Please review both versions and tell me what to carry forward."

### Phase 3: Review & Confirmation

Present the user with a migration report:

```
=== TEMPLATE MIGRATION REPORT ===

Migration type: Legacy → v2.2.0
Current CLAUDE.md: unversioned (legacy format)
Target CLAUDE.md: v2.2.0 structure

EXTRACTED PROJECT DATA:
  Project name: CallMe
  Description: AI-powered communication platform
  Load-bearing walls: 4 found
  Custom anti-patterns: 1 found (beyond template defaults)
  Custom sections: 2 found
    - "## Voice Pipeline Architecture"
    - "## Third-Party Integrations"

PROPOSED CHANGES:
  1. Rebuild CLAUDE.md using v2.2.0 template structure
  2. Populate with extracted project data (shown above)
  3. Append 2 custom sections at the end
  4. Archive old CLAUDE.md to _Archive/CLAUDE_pre_migration.md

REQUIRES YOUR INPUT:
  - Gold Rush custom bullet: not found (needs writing)
  - Verify load-bearing walls are complete

Proceed? (y/n/edit)
```

- `y` — apply migration
- `n` — abort
- `edit` — open the draft CLAUDE.md for manual editing before applying

### Phase 4: Application

1. Archive existing CLAUDE.md → `_Archive/CLAUDE_pre_migration_{timestamp}.md`
2. Write new CLAUDE.md with:
   - Template structure (v2.x format)
   - Extracted project data populated
   - `claude_md_version` metadata line set to current version
   - Custom sections appended at the end with a separator comment
3. Run `template_sync.py --apply` for all other files (hooks, rules, skills, settings.json merge).
4. Report results.

### Phase 5: Post-Migration Verification

1. Run `/governance-health` to verify all hooks/rules/skills are intact.
2. Confirm CLAUDE.md loads correctly (no syntax issues).
3. Show summary of what was migrated.

---

## 5. Custom Sections Handling

Projects may have added sections to CLAUDE.md that don't exist in the template. These are valuable project-specific context.

**Strategy:**

1. Identify all `##` headings in the project's CLAUDE.md.
2. Compare against the template's `##` headings.
3. Any unrecognized headings + their content = "custom sections."
4. Append custom sections at the end of the new CLAUDE.md under a separator:

```markdown
## Project-Specific Notes
<!-- Migrated from pre-v2.x CLAUDE.md. Review and reorganize as needed. -->

### Voice Pipeline Architecture
{original content preserved verbatim}

### Third-Party Integrations
{original content preserved verbatim}
```

5. Flag in the migration report: "2 custom sections migrated — review for relevance."

---

## 6. Fresh Install Flow

When there's no existing CLAUDE.md (brand new project):

1. Copy template CLAUDE.md verbatim.
2. Prompt user for required fields:
   - Project name
   - One-sentence description
   - Load-bearing wall decisions (minimum 1)
   - Gold Rush custom bullet
3. Write populated CLAUDE.md.
4. Run `template_sync.py --apply` for everything else.
5. Initialize `.template_version`.

---

## 7. Error Handling

| Scenario | Behavior |
|----------|----------|
| CLAUDE.md parse failure | Fall back to manual mode (show both versions, let user decide) |
| `_Archive/` doesn't exist | Create it |
| Template directory not found | Abort with clear error |
| User aborts mid-migration | No changes made (all writes happen after confirmation) |
| `template_sync.py` fails after CLAUDE.md written | CLAUDE.md change stands, sync failure reported separately. User runs `/template-sync --apply` to retry. |

---

## 8. Implementation Scope

| File | Change |
|------|--------|
| `.claude/skills/template-migrate/SKILL.md` | New skill definition |
| `template_sync.py` | No changes (this skill orchestrates it, doesn't modify it) |
| `TEMPLATE_MANIFEST.json` | Add `template-migrate` skill to infrastructure files |

The skill itself is a SKILL.md that instructs the Claude Code agent on the migration flow. It does not require a standalone script — the agent executes the extraction, presentation, and file operations using its standard tools (Read, Write, Bash for `template_sync.py`).

---

## 9. Testing Strategy

1. **Legacy migration — EPL-Test-Project:** Strip it back to a v1.x-style monolithic CLAUDE.md. Run `/template-migrate`. Verify extraction, rebuild, and full governance system works afterward.
2. **Major version migration:** Simulate a CLAUDE.md structure change (add a new required section). Run against a project with the old structure. Verify the new section appears, old data preserved.
3. **Fresh install:** Empty directory with only a `.git`. Run `/template-migrate`. Verify full scaffolding + infrastructure deployed.
4. **Up-to-date project:** Run on a current project. Verify clean no-op.
5. **Abort test:** Start migration, abort at confirmation. Verify zero files changed.
6. **Unrecognizable CLAUDE.md:** Heavily customized format. Verify graceful fallback to manual mode.

---

## 10. Relationship to Other Specs

- **Depends on:** [settings_json_smart_merge.md](settings_json_smart_merge.md) — migration runs `template_sync.py` which includes settings.json merge.
- **Depends on:** [claude_md_version_marker.md](claude_md_version_marker.md) — the `claude_md_version` metadata line that enables version detection.
- **Consumed by:** `/template-sync` skill (which should detect "needs migration" and recommend `/template-migrate` instead of proceeding with a routine sync).

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | 2026-03-03 | Initial spec | Nathan / Claude |
