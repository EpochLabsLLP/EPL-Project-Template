---
name: init-doc
description: Create a new spec document from the correct template. Use when starting any new document (PVD, PRD, Engineering Spec, Blueprint, etc.) to ensure proper structure, naming, and template compliance.
argument-hint: <type> [abbreviation]
user_invocable: true
---

# init-doc

Creates a new document from the appropriate template with correct naming, location, and provenance tracking.

## Invocation

```
/init-doc <type> [abbreviation]
```

## Arguments

- `type` (required): The document type to create. See type table below.
- `abbreviation` (optional): 2-4 letter project abbreviation (e.g., `VK`, `CM`). If omitted, detect from existing spec files in `Specs/` or ask the user.

## Type Table

| Type Argument | Aliases | Template File | Target Directory |
|---------------|---------|---------------|------------------|
| `pvd` | `product-vision` | `Specs/TEMPLATE_PVD.md` | `Specs/` |
| `prd` | `product-requirements` | `Specs/TEMPLATE_PRD.md` | `Specs/` |
| `brief` | `product-brief` | `Specs/TEMPLATE_Product_Brief.md` | `Specs/` |
| `es` | `eng-spec`, `engineering-spec` | `Specs/TEMPLATE_Engineering_Spec.md` | `Specs/` |
| `ux` | `ux-spec` | `Specs/TEMPLATE_UX_Spec.md` | `Specs/` |
| `bp` | `blueprint` | `Specs/TEMPLATE_Blueprint.md` | `Specs/` |
| `tp` | `testing-plans`, `test-plan` | `Testing/TEMPLATE_Testing_Plans.md` | `Testing/` |
| `wo` | `work-order` | `Specs/TEMPLATE_Work_Order.md` | `WorkOrders/` |
| `dr` | `decision-record` | `Specs/TEMPLATE_Decision_Record.md` | `Specs/` |
| `gt` | `gap-tracker` | (built-in scaffold) | `Specs/` |
| `session` | (none) | `Sessions/SESSION_TEMPLATE.md` | `Sessions/` |

## Execution Steps

Given `$ARGUMENTS` (parsed as `<type> [abbreviation]`):

### 1. Parse Arguments

Split `$ARGUMENTS` into `TYPE` and `ABBREV`.

- Normalize `TYPE` to its canonical form using the aliases above (case-insensitive).
- If `TYPE` is not recognized, list valid types and ask the user to choose.

### 2. Detect or Request Abbreviation

If `ABBREV` was not provided:

1. Search `Specs/` for existing spec files matching `*_PVD_*`, `*_PRD_*`, `*_Engineering_Spec_*`, etc.
2. Extract the prefix before the first `_` as the abbreviation.
3. If found, use it. If not found, ask the user: "What 2-4 letter abbreviation should I use for this project? (e.g., VK for ViviKeys)"

### 3. Read the Template

Read the template file from the path in the type table above.

- If the template file does not exist, STOP and report: "Template not found: {path}. Check that the project template is properly installed."

### 4. Prepare the Output

**Filename pattern** (by type):

| Type | Filename Pattern |
|------|-----------------|
| `pvd` | `{ABBREV}_PVD_v1.md` |
| `prd` | `{ABBREV}_PRD_v1.md` |
| `brief` | `{ABBREV}_Product_Brief_v1.md` |
| `es` | `{ABBREV}_Engineering_Spec_v1.md` |
| `ux` | `{ABBREV}_UX_Spec_v1.md` |
| `bp` | `{ABBREV}_Blueprint_v1.md` |
| `tp` | `{ABBREV}_Testing_Plans_v1.md` |
| `wo` | `{ABBREV}_Work_Order_WO-X.X.X-A.md` (ask user for WO ID) |
| `dr` | `{ABBREV}_Decision_Record.md` |
| `gt` | `{ABBREV}_gap_tracker.md` |
| `session` | `YYYY-MM-DD_session_{topic}.md` (ask user for topic) |

**Check for conflicts:** If the target file already exists, STOP and report: "File already exists: {path}. Use a higher version number or a different name."

### 5. Transform Content

1. Prepend `<!-- TEMPLATE_SOURCE: {template_filename} -->` as the very first line.
2. Replace all `{ProjectName}` placeholders with the full project name (from CLAUDE.md `## Identity` section, or ask user).
3. Replace all `{Abbrev}` placeholders with `ABBREV`.
4. Replace `{YYYY-MM-DD}` with today's date.

### 6. Write the File

Write the transformed content to `{Target Directory}/{Filename}`.

Ensure the target directory exists (create if needed: `WorkOrders/` may not exist yet in a new project).

### 7. Report

Output to the user:

```
Created: {target_path}
From template: {template_filename}
Next: Fill in the bracketed sections. Refer to the template comments for guidance.
```

## Special Cases

### Gap Tracker (`gt`)
The gap tracker does not have a standalone TEMPLATE_ file. Create it with this scaffold:

```markdown
<!-- TEMPLATE_SOURCE: init-doc:gap-tracker -->
# {ABBREV} Gap Tracker

## Tier 0 — Critical Defects
<!-- Blocking bugs, security issues, data loss risks. Fix before ALL other work. -->

## Tier 1 — Functional Gaps
<!-- Missing features required by the spec. Core functionality not yet implemented. -->

## Tier 2 — Quality Gaps
<!-- Performance issues, UX polish, error handling improvements. -->

## Tier 3 — Enhancements
<!-- Nice-to-haves, optimizations, future features. Lowest priority. -->
```

### Work Orders (`wo`)
Ask the user for the Work Order ID (e.g., `WO-1.2.3-A`) which determines the filename. If they don't know it yet, suggest they run `/trace-check` first to see the traceability tree.

### Sessions (`session`)
Ask for a brief topic slug (lowercase, hyphens). Use today's date for the prefix.

## Why This Skill Exists

The project template includes 9+ document templates with specific structure, naming conventions, and traceability ID systems. Agents creating documents from scratch miss all of this, producing docs that:
- Lack required sections
- Use inconsistent naming
- Break the traceability chain
- Don't get picked up by `/trace-check`

This skill is the happy path. The `template-guard.sh` hook catches the cases where agents forget to use it.
