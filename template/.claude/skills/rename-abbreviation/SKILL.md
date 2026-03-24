---
name: rename-abbreviation
description: Rename a project's abbreviation across all spec files, Work Orders, and governance artifacts. Use when a project changes its abbreviation (e.g., OC → AT after renaming OpenClaw Research to ATLAS). Handles file renames and content updates with traceability preservation.
user-invocable: true
argument-hint: OLD NEW
---

# Rename Project Abbreviation

Safely rename a project's abbreviation across all governance artifacts.

## When to Use

- Project has been renamed and the abbreviation no longer fits
- Abbreviation conflicts with another project in the registry
- Initial abbreviation was a placeholder

## Execution

When invoked with `$ARGUMENTS` containing OLD and NEW abbreviations (e.g., `/rename-abbreviation OC AT`):

### Step 1 — Validate

1. Parse OLD and NEW from arguments. Both should be 2-4 uppercase letters.
2. Confirm with Nathan: "Rename abbreviation from **{OLD}** to **{NEW}** across all project files?"
3. If Nathan declines, stop.

### Step 2 — Inventory

Scan the project for all files containing the old abbreviation. Check:

1. **Spec files** — `Specs/{OLD}_*.md` (filenames and content)
2. **Work Orders** — `WorkOrders/WO-*.md` (content references to spec IDs like `ES-N.M`, `BP-N.M.T`)
3. **Testing Plans** — `Testing/{OLD}_*.md`
4. **Work Ledger** — `Specs/Work_Ledger.md` (auto-generated, will be regenerated)
5. **Gap Tracker** — `Specs/gap_tracker.md`
6. **Decision Record** — `Specs/{OLD}_Decision_Record.md`
7. **Session files** — `Sessions/*.md` (content references)
8. **CLAUDE.md** — project abbreviation declaration
9. **Blueprint task IDs** — BP-N.M.T references throughout
10. **Project registry** — `_shared/project_registry.json` abbreviation field

Report the full inventory to Nathan before proceeding.

### Step 3 — Rename Files

For each file with the old abbreviation in its NAME:

```
Specs/{OLD}_PVD_v1.md           → Specs/{NEW}_PVD_v1.md
Specs/{OLD}_Engineering_Spec_v1.md → Specs/{NEW}_Engineering_Spec_v1.md
Specs/{OLD}_Blueprint_v1.md     → Specs/{NEW}_Blueprint_v1.md
Testing/{OLD}_Testing_Plans_v1.md → Testing/{NEW}_Testing_Plans_v1.md
Specs/{OLD}_Decision_Record.md  → Specs/{NEW}_Decision_Record.md
```

Use `git mv` for each rename to preserve git history.

### Step 4 — Update Content

For each file with the old abbreviation in its CONTENT:

1. Replace `{OLD}_` prefixes in document titles and headers
2. Replace abbreviation references in metadata tables (Author, Implements, etc.)
3. **Do NOT replace traceability IDs** (ES-N.M, BP-N.M.T, WO-N.M.T-X) — these are numeric, not abbreviation-based
4. Replace abbreviation in CLAUDE.md project identity section

### Step 5 — Update Registry

Edit `_shared/project_registry.json`:
- Change the `"abbreviation"` field from OLD to NEW

### Step 6 — Regenerate Work Ledger

Run `/trace-check` to regenerate the Work Ledger with updated file paths.

### Step 7 — Commit

Create a single atomic commit:
```
chore: Rename project abbreviation {OLD} → {NEW}

All spec files, governance artifacts, and registry updated.
Traceability IDs (ES-N.M, BP-N.M.T, WO-N.M.T-X) unchanged.
```

### Step 8 — Report

Display summary:
- Files renamed: {count}
- Files content-updated: {count}
- Registry updated: yes/no
- Work Ledger regenerated: yes/no

## Important

- **Traceability IDs are NOT affected.** ES-1.1 stays ES-1.1 regardless of abbreviation. Only file names and display text change.
- **Frozen files need /unlock-frozen first.** If specs are frozen, you must get authorization before renaming them.
- **Use git mv** for all file renames — preserves blame history.
- **This is a cosmetic change** — it doesn't alter the traceability chain, only the human-readable labels.
