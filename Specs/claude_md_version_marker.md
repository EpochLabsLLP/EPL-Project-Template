# claude_md_version Marker — Engineering Spec

| Field | Value |
|-------|-------|
| **Version** | 1 |
| **Status** | DRAFT |
| **Date** | 2026-03-03 |
| **Author** | Nathan / Claude |
| **Component** | Template CLAUDE.md scaffolding |

---

## 1. Problem Statement

`.template_version` tracks which template version the project's *infrastructure* (hooks, rules, skills) is synced to. But it says nothing about the CLAUDE.md *structure*.

Since CLAUDE.md is scaffolding (project-owned, never overwritten), its structure can drift from the template over time. We need a way to detect when a project's CLAUDE.md structure is outdated relative to the current template — without conflating that with the infrastructure version.

**Example:** A project might be at template v2.5.0 (all hooks/rules current) but still have a v2.0.0 CLAUDE.md structure (missing a section added in v2.3.0). The version marker lets `/template-migrate` and `/template-sync` distinguish these cases.

---

## 2. Design

### 2.1 Marker Format

An HTML comment on line 3 of CLAUDE.md (after the title and subtitle):

```markdown
# {ProjectName} — Project Constitution
# This file auto-loads into every Claude Code session. It is LAW, not guidance.
<!-- claude_md_version: 2.2.0 -->
# Last updated: {YYYY-MM-DD}
```

**Why an HTML comment:**
- Invisible to rendered markdown (doesn't clutter the document).
- Parseable by simple regex: `<!-- claude_md_version: (\S+) -->`.
- Won't confuse Claude Code's auto-loader (comments are ignored).
- Follows the same pattern as `<!-- TEMPLATE_SOURCE: ... -->` used by template-guard.

**Why line 3 (approximately):**
- Predictable location for parsers. But detection should scan the first 10 lines, not rely on exact line number — projects may have added lines above it.

### 2.2 Version Semantics

The `claude_md_version` tracks the **template CLAUDE.md structure version**, not the project content version. It increments only when the template changes the CLAUDE.md scaffolding structure:

| Change Type | Version Bump? |
|-------------|--------------|
| Project fills in placeholders | No |
| Project adds custom sections | No |
| Project modifies anti-patterns | No |
| Template adds a new required section | Yes (minor) |
| Template reorganizes section order | Yes (minor) |
| Template fundamentally restructures CLAUDE.md | Yes (major) |
| Template fixes a typo in boilerplate text | No (cosmetic, not structural) |

**Initial value:** `2.2.0` — matches the template version at the time this feature is introduced. This establishes the baseline.

**Future values:** Increment independently from `template_version` in `TEMPLATE_MANIFEST.json`. The infrastructure can be at v2.5.0 while the CLAUDE.md structure is still at v2.2.0 (if no structural changes were needed).

### 2.3 Version Storage in Manifest

Add to `TEMPLATE_MANIFEST.json`:

```json
{
  "template_version": "2.3.0",
  "claude_md_structure_version": "2.2.0",
  "hook_registrations": { ... },
  "categories": { ... }
}
```

This is the source of truth for what CLAUDE.md structure version the template currently expects.

---

## 3. Detection Logic

### For `template_sync.py`:

```python
def check_claude_md_version(project_dir, manifest):
    """Check if project CLAUDE.md structure matches template expectation.

    Returns:
        (project_version, template_version, needs_migration)
    """
    expected = manifest.get("claude_md_structure_version", None)
    if expected is None:
        return (None, None, False)  # Template predates this feature

    claude_md_path = os.path.join(project_dir, "CLAUDE.md")
    if not os.path.isfile(claude_md_path):
        return (None, expected, True)  # No CLAUDE.md at all

    # Scan first 10 lines for version marker
    project_version = None
    with open(claude_md_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 10:
                break
            match = re.search(r'<!-- claude_md_version: (\S+) -->', line)
            if match:
                project_version = match.group(1)
                break

    if project_version is None:
        return (None, expected, True)  # Legacy CLAUDE.md, no marker

    needs_migration = project_version != expected
    return (project_version, expected, needs_migration)
```

### Integration with Sync Report:

When `needs_migration` is true, `template_sync.py` adds a warning to the report:

```
⚠ CLAUDE.MD STRUCTURE OUTDATED
  Project CLAUDE.md: v2.2.0 (or: unversioned/legacy)
  Template expects:   v2.4.0
  Run /template-migrate to update CLAUDE.md structure.
  (template_sync.py does not modify CLAUDE.md — this requires guided migration.)
```

This makes it visible during routine syncs without taking any automatic action.

---

## 4. Backfill Strategy

### Existing Projects (at v2.2.0)

When this feature ships (as part of v2.3.0):

1. `template_sync.py` runs as normal — updates infrastructure files.
2. The sync report shows the CLAUDE.MD STRUCTURE OUTDATED warning.
3. Running `/template-migrate` on a v2.2.0 project:
   - Detects: CLAUDE.md has no version marker but matches the v2.2.0 structure.
   - Action: Insert the `<!-- claude_md_version: 2.2.0 -->` comment line. No structural changes needed.
   - This is a minimal, safe edit — adding one comment line.

### Legacy Projects (pre-v2.0)

1. No marker found → `needs_migration = True`.
2. `/template-migrate` handles the full extraction and rebuild flow (per the template-migrate spec).
3. New CLAUDE.md gets the version marker automatically.

### New Projects

1. Template CLAUDE.md already has the marker.
2. `/template-migrate` (fresh install flow) populates project data; marker is already present.
3. No additional action needed.

---

## 5. Template CLAUDE.md Change

Add the marker to the template's CLAUDE.md (line 3):

```markdown
# {ProjectName} — Project Constitution
# This file auto-loads into every Claude Code session. It is LAW, not guidance.
<!-- claude_md_version: 2.2.0 -->
# Last updated: {YYYY-MM-DD}
```

This is a one-line addition to the scaffolding template.

---

## 6. Implementation Scope

| File | Change |
|------|--------|
| `template/CLAUDE.md` | Add `<!-- claude_md_version: 2.2.0 -->` on line 3 |
| `template/TEMPLATE_MANIFEST.json` | Add `"claude_md_structure_version": "2.2.0"` |
| `template/template_sync.py` | Add `check_claude_md_version()`, add warning to `print_report()` |
| `/template-migrate` skill | Reads this marker for detection (defined in template-migrate spec) |
| `/template-sync` skill | Updated output description to mention CLAUDE.md version check |

Estimated additions: ~20 lines to `template_sync.py`, 1 line to CLAUDE.md, 1 line to manifest.

---

## 7. Testing Strategy

1. **Detection — marker present:** CLAUDE.md with `<!-- claude_md_version: 2.2.0 -->` and manifest expects `2.2.0` → `needs_migration = False`.
2. **Detection — marker outdated:** CLAUDE.md with `2.2.0`, manifest expects `2.4.0` → `needs_migration = True`, warning shown.
3. **Detection — no marker:** Legacy CLAUDE.md → `needs_migration = True`, "unversioned/legacy" shown.
4. **Detection — no CLAUDE.md:** Missing file → `needs_migration = True`.
5. **Backfill:** v2.2.0 project with no marker → `/template-migrate` inserts marker only, no structural changes.
6. **Sync report integration:** Run `template_sync.py` on outdated project, verify warning appears in report.

---

## 8. Relationship to Other Specs

- **Consumed by:** [template_migrate_skill.md](template_migrate_skill.md) — the version marker is how `/template-migrate` determines migration type.
- **Consumed by:** [settings_json_smart_merge.md](settings_json_smart_merge.md) — indirectly; both are part of the v2.3.0 upgrade package.
- **Independent of:** Infrastructure version tracking (`.template_version`). These are separate version axes.

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | 2026-03-03 | Initial spec | Nathan / Claude |
