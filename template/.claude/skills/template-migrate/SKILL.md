---
name: template-migrate
description: Guided migration for projects with outdated or missing CLAUDE.md structure. Handles legacy projects, major version upgrades, and fresh installs. Human-in-the-loop — always confirms before writing.
argument-hint: "--dry-run"
user-invocable: true
---

# template-migrate

Guided migration skill for deploying the EPL template to projects with outdated, legacy, or missing governance infrastructure. This is the complement to `/template-sync` — use this when the CLAUDE.md structure itself needs updating.

## When to Use

- `/template-sync` reports "CLAUDE.MD STRUCTURE OUTDATED"
- A project has no `.template_version` (predates the template)
- A project has a monolithic CLAUDE.md (pre-v2.x style with governance logic embedded)
- Setting up a brand new project from scratch
- A major template version changes the CLAUDE.md scaffolding structure

## When NOT to Use

- Routine template updates (v2.x → v2.y with no CLAUDE.md structure change) → use `/template-sync` instead
- The project is already up to date → this skill will detect it and report "no migration needed"

## How to Invoke

```
/template-migrate              # Interactive guided migration
/template-migrate --dry-run    # Show what would change without modifying anything
```

## Execution

### Phase 1: Detection

1. **Locate the template repo.** Search for `TEMPLATE_MANIFEST.json` in:
   - `$CLAUDE_PROJECT_DIR/../_ProjectTemplate/`
   - `C:/Claude Folder/Epoch_Labs/Epoch Labs Project Template/_ProjectTemplate/`
   - If not found, ask Nathan for the path.

2. **Read version info:**
   - `.template_version` from the project (or `0.0.0` if missing)
   - `claude_md_structure_version` from the template's `TEMPLATE_MANIFEST.json`
   - Scan the first 10 lines of the project's `CLAUDE.md` for `<!-- claude_md_version: X.Y.Z -->`

3. **Determine migration type:**

   | Project State | Migration Type |
   |--------------|----------------|
   | No CLAUDE.md at all | **Fresh install** |
   | CLAUDE.md exists, no version marker | **Legacy migration** |
   | Version marker present but outdated | **Structure upgrade** |
   | Version marker matches template | **Up to date** → report clean, delegate to `/template-sync` if infrastructure needs updating |

4. **Report the detection result** to Nathan before proceeding.

### Phase 2: Extraction (Legacy and Structure Upgrade Only)

Read the existing CLAUDE.md and extract project-specific data:

**Look for these sections and extract their content:**

| Section | What to Extract |
|---------|----------------|
| Project name | The `# {Name} —` header |
| Description | The "is {description}" sentence in Identity section |
| Load-bearing walls | The numbered list under `## Architecture — Load-Bearing Walls` |
| Gold Rush custom bullet | Any project-specific bullet beyond the template defaults |
| Custom anti-patterns | Any anti-patterns not in the template defaults |
| Key specs references | Any project-specific spec files listed |
| Escalation contacts | Names in the escalation rules section |
| Custom sections | Any `##` headings not in the template structure |

**If the CLAUDE.md format is unrecognizable** (heavily customized, pre-v1.x, or completely different structure):
- Do NOT attempt to auto-extract. Instead:
- Show Nathan the full existing CLAUDE.md
- Show the new template structure with blank placeholders
- Ask: "I can't automatically extract project data from this format. Please tell me what to carry forward."

### Phase 3: Review & Confirmation

Present a migration report to Nathan:

```
=== TEMPLATE MIGRATION REPORT ===

Migration type: {Fresh install | Legacy migration | Structure upgrade}
Current CLAUDE.md: {version or "unversioned/legacy" or "missing"}
Target CLAUDE.md: {template's claude_md_structure_version}

EXTRACTED PROJECT DATA:
  Project name: {name or "not found"}
  Description: {description or "not found"}
  Load-bearing walls: {count} found
  Custom anti-patterns: {count} beyond template defaults
  Custom sections: {count} found
    {list heading names if any}

PROPOSED CHANGES:
  1. {Describe what will happen to CLAUDE.md}
  2. Archive old CLAUDE.md to _Archive/CLAUDE_pre_migration_{timestamp}.md
  3. Run template_sync.py for infrastructure/hooks/rules/skills

REQUIRES YOUR INPUT:
  {List any fields that couldn't be extracted and need Nathan's input}
```

**Wait for Nathan's explicit confirmation before proceeding.**

If `--dry-run` was passed, stop here. Do not make any changes.

### Phase 4: Application

After Nathan confirms:

1. **Archive the existing CLAUDE.md** (if one exists):
   ```
   _Archive/CLAUDE_pre_migration_{YYYYMMDD_HHMMSS}.md
   ```
   Create `_Archive/` directory if it doesn't exist.

2. **Write the new CLAUDE.md:**
   - Start from the template CLAUDE.md structure
   - Populate all extracted project data
   - Set the `<!-- claude_md_version: X.Y.Z -->` marker to the current template version
   - Append any custom sections at the end under a separator:
     ```markdown
     ## Project-Specific Notes
     <!-- Migrated from pre-v{old} CLAUDE.md. Review and reorganize as needed. -->
     ```

3. **Run template_sync.py:**
   ```bash
   python "$TEMPLATE_DIR/template_sync.py" "$TEMPLATE_DIR" "$CLAUDE_PROJECT_DIR" --apply
   ```
   This handles all infrastructure files (hooks, rules, skills) AND the settings.json hook merge.

4. **Report results** — show what was created/updated.

### Phase 5: Post-Migration Verification

1. Run `/governance-health` to verify the full governance system is intact.
2. Confirm the CLAUDE.md loads correctly (read it back and verify structure).
3. Show a summary:
   ```
   === MIGRATION COMPLETE ===
   CLAUDE.md: Migrated to v{X.Y.Z} structure
   Infrastructure: {N} files synced
   Settings.json: Hook registrations merged
   Governance health: {PASS/WARN/FAIL}
   ```

## Fresh Install Flow

When there is no existing CLAUDE.md (brand new project):

1. Copy the template CLAUDE.md verbatim to the project.
2. Ask Nathan for required fields:
   - Project name
   - One-sentence description
   - At least 1 load-bearing wall decision
   - Gold Rush custom bullet (project-specific quality bar)
3. Replace placeholders in the new CLAUDE.md with Nathan's answers.
4. Set the `<!-- claude_md_version: X.Y.Z -->` marker.
5. Run `template_sync.py --apply` for everything else.
6. Run `/governance-health` to verify.

## Safety

- **Never overwrites CLAUDE.md without confirmation** — always shows the plan first
- **Archives before replacing** — old CLAUDE.md is preserved in `_Archive/`
- **Falls back to manual** — if extraction fails, asks Nathan instead of guessing
- **Delegates infrastructure to template_sync.py** — does not manually copy hooks/rules/skills
- **Idempotent** — running on an up-to-date project is a harmless no-op
