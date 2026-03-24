<!-- AGENT INSTRUCTION: Follow these naming conventions for all files created in the project.
     Consistent naming enables the SessionStart hooks and spec-lookup skills
     to find files programmatically.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# File Naming Conventions

*Intent: Consistent naming enables automation — hooks, skills, and scripts can find files by pattern. It also helps future Claude instances navigate the project without prior context.*

## Document Files

| Type | Pattern | Example |
|------|---------|---------|
| Specs | `{Abbrev}_{Topic}_v{N}.md` | `VK_Keyboard_Spec_v2.md` |
| Research | `{Topic}_Research_v{N}.md` | `Market_Analysis_Research_v1.md` |
| Patents | `{Abbrev}-PAT-{NNN}_{Title}.md` | `VK-PAT-001_Adaptive_Layout.md` |
| Sessions | `YYYY-MM-DD_session_{topic}.md` | `2026-02-28_session_phase1_hooks.md` |
| Test Plans | `{Abbrev}_{Topic}_Test_Plan.md` | `VK_Input_Test_Plan.md` |

## Conventions

- **{Abbrev}** = 2-4 letter project abbreviation (set once, use everywhere)
- **{N}** = version number, starting at 1. Increment when making significant revisions.
- **Superseded docs** get moved to `_Archive/` — never delete, never rename in place
- **Draft docs** use `_DRAFT` suffix until finalized: `VK_PVD_DRAFT.md` → `VK_PVD_v1.md`

## Code Files

Follow the conventions of your project's tech stack (e.g., PascalCase for Kotlin classes, snake_case for Python modules). Do not enforce a universal code naming rule — defer to the language/framework standard.
