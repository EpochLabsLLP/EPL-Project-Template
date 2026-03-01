# Project Template — Epoch Labs Standard Structure
## Last Updated: 2026-02-24

---

## Purpose

This is a clean, reusable project template for new Epoch Labs projects. Copy this entire folder to `C:\Claude Folder\{ProjectName}\` and customize the placeholder files.

## Setup Instructions

1. **Copy** this folder to `C:\Claude Folder\{YourProjectName}\`
2. **Rename** placeholder files (replace `{ProjectName}` with your actual project name)
3. **Edit** `CLAUDE.md` — fill in all `{placeholder}` values with project-specific details
4. **Create _shared junction** (connects to cross-project shared specs):
   ```cmd
   mklink /J "C:\Claude Folder\{YourProjectName}\_shared" "C:\Claude Folder\_SharedCore"
   ```
5. **Delete** this README.md (it's the template guide, not your project readme)

## Folder Structure

```
{ProjectName}/
  CLAUDE.md               -- Project constitution (auto-loads into Claude Code)
  Specs/                   -- Specifications, PVDs, blueprints, engineering specs
  Research/                -- Research docs, competitive analysis, market research
  Code/                    -- Source code, scripts
  Testing/                 -- Test plans, QA documentation
  Quality/                 -- Feature-level quality assessments
  Patents/                 -- Patent briefs, IP documents
  Processes/               -- Project-specific process documentation
  Sessions/                -- Session summaries for continuity across conversations
  Notes/                   -- General notes, scratch work
  Investor/                -- Investor materials, pitch decks
  _shared/                 -- Junction to _SharedCore (cross-project shared specs)
  _Archive/                -- Archived/superseded files (NEVER delete, archive here)
  .claude/
    skills/                -- Custom Claude Code skills for this project
    settings.json          -- Claude Code settings (hooks, permissions)
```

## What Goes Where

| Folder | Contents | Naming Convention |
|--------|----------|-------------------|
| **Specs/** | PVD, engineering spec, feature specs, blueprints, interface contracts | `{Abbrev}_{Topic}_v{N}.md` |
| **Research/** | Market research, competitive analysis, technology evaluations | `{Topic}_Research_v{N}.md` |
| **Code/** | All source code, organized by framework conventions | Per-framework conventions |
| **Testing/** | Test plans, test strategies, QA checklists | `{Topic}_Test_Plan.md` |
| **Quality/** | Per-feature quality assessments and acceptance criteria | `feature_{feature-name}.md` |
| **Patents/** | Patent briefs for novel concepts | `{Abbrev}-PAT-{NNN}_{Title}.md` |
| **Processes/** | Documented procedures specific to this project | `{Process_Name}.md` |
| **Sessions/** | End-of-session summaries for continuity | `YYYY-MM-DD_session_{topic}.md` |
| **Notes/** | Scratch work, informal notes | Any |
| **Investor/** | Pitch decks, financial models, investor updates | Any |
| **_Archive/** | Superseded docs (moved, never deleted) | Original filename |

## Document Lifecycle

1. **Drafts** live in the appropriate folder with `_DRAFT` suffix
2. **Finalized docs** drop the suffix and get a version number (`_v1.md`)
3. **Superseded docs** get moved to `_Archive/` with a note in the current doc's header
4. **All docs** get logged to `document_index` table in `claude_memory.db` (if available)

## Cross-Project Resources

These global directories support all projects:

| Directory | Purpose |
|-----------|---------|
| `_SharedCore/` | Cross-project shared specs, schemas, templates, security |
| `_Processes/` | Global skills and process library |
| `_TaskQueue/` | Task briefs for future sessions |
| `_IP_Pipeline/` | Patent brief queue for review |
| `Memory/` | Memory database (`claude_memory.db`) and sync infrastructure |

## Session Documentation Standard

Every substantive session ends with a summary in `Sessions/`:

```markdown
# Session Summary: {Topic}
## {ProjectName} | {YYYY-MM-DD}

## What Was Accomplished
- {Bullet list}

## Key Decisions Made
| Decision | Rationale | Impact |
|----------|-----------|--------|

## Files Created / Modified
| File | Action | Purpose |
|------|--------|---------|

## Open Questions / Unresolved
- {Questions for next session}

## Next Steps
1. {Prioritized list}
```

## Safety Rules (All Projects)

- **NEVER delete files** — archive to `_Archive/` instead
- **NEVER overwrite existing files** without asking first
- **NEVER commit secrets** — API keys in env vars or Supabase vault only
- **Ask before** making structural changes to folder organization
- **Log all created documents** to `document_index` in memory DB
