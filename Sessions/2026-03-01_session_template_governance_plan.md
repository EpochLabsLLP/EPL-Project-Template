# Template Governance System — Design Plan (IN PROGRESS)

## Status: Phase 2 — Exploration complete, design pending

## Context

Nathan identified that agents using the project template are:
1. Missing template files entirely when creating spec documents
2. Ignoring `settings.local.json.example`
3. Writing specs from scratch instead of from templates
4. Writing spec docs to project root instead of `Specs/`
5. Struggling when asked to pull template parts into existing projects
6. Template updates are painful to deploy to active projects with customized docs

## What We Need (Three Capabilities)

1. **Guard** — Prevent agents from creating docs wrong (including root writes)
2. **Sync** — Deploy template updates to active projects without clobbering customizations
3. **Audit** — Drop something into any repo that inventories what's there, what's not, what's modified, what shouldn't be — then normalizes and merges

## Original Strategy (5 Layers)

| Layer | Component | Purpose |
|-------|-----------|---------|
| 1. Awareness | Enhanced `session-start.sh` | Lists templates, warns about missing settings |
| 2. Enforcement | `template-guard.sh` hook | Blocks spec creation without TEMPLATE_SOURCE marker |
| 3. Convenience | `/init-doc` skill | Scaffolds documents from templates with proper naming |
| 4. Sync | `template_sync.py` + `TEMPLATE_MANIFEST.json` | Compares template vs project, merges updates |
| 5. Audit | `/template-sync` skill | Runs the sync engine on demand |

## Red Team Findings (From Crashed Conversation)

### Bypass Vectors (32 vectors, 8 categories)
**CRITICAL:**
- Edit tool with empty `old_string` creates files without triggering Write hooks
- Bash can create files via `echo >`, `cat >`, `tee`, `python -c` — none caught
- Copy/move from ungoverned locations bypasses guard entirely
- Marker forgery is trivial — agent can just inject `<!-- TEMPLATE_SOURCE: TEMPLATE_PVD.md -->` without actually reading the template
- Create empty file first (Write), then Edit to add content (Edit doesn't get full content inspection)
- Modifying the hook itself or parse_hook_input.py
- Subagent tool calls — hooks may not fire for subagent operations

### Architecture Flaws (10 fundamental issues)
1. Entire enforcement model is advisory, not mechanistic (hooks are suggestions to AI)
2. FROZEN status detection is fragile (string matching first 15 lines, inconsistent across hooks)
3. Traceability validates structure, not semantics
4. Session hooks are context budget time bombs (caused the crash!)
5. No template versioning or integrity verification
6. Section-level markdown merge is architecturally unsound
7. Bootstrap/circular dependency in sync engine
8. Spec-gate uses denylist instead of allowlist for code directories
9. Binary DRAFT/FROZEN prevents practical workflows
10. No governance of the governance layer itself

### Adoption Friction (39 findings, 11 BLOCKING)
- `/init-doc` skill doesn't exist yet
- Template guard hook doesn't exist yet
- `/template-sync` skill doesn't exist yet
- Quick one-off documents would be incorrectly blocked
- Pre-existing project adoption is painful
- Python dependency may not be available everywhere
- Hook errors could block ALL writes if they crash
- Session-start output could become too verbose (context budget!)

### Sync Engine Issues
- Manifest corruption = single point of failure
- Tight coupling to file paths
- Markdown section parsing too fragile for production

## Research Findings

### Hooks System (Key Facts)
- PreToolUse hooks receive FULL file content in `tool_input.content` for Write
- For Edit, only `tool_input.file_path`, `old_string`, `new_string` — NOT full content
- Exit codes: 0=allow, 1=error, 2=block
- Hook output can include `permissionDecision: deny` and `updatedInput`
- 18 hook event types available

### Template Sync Patterns (Best Practice: Copier)
- Gold standard: three-way merge with answer memory
- File ownership categories: `_skip_if_exists`, `_preserve`, `_exclude`
- `.copier-answers.yml` tracks template version and user choices
- Migration scripts for breaking changes
- Key insight: template author declares file ownership, not the project

## Current Template Inventory

### Files
- 7 hooks in `.claude/hooks/`
- 5 rules in `.claude/rules/`
- 12 skills in `.claude/skills/`
- 9 TEMPLATE_*.md files in `Specs/` and `Testing/`
- 1 session template in `Sessions/`
- `settings.json` with hook registrations
- `validate_traceability.py` for trace-check skill

### Existing Enforcement
- `spec-gate.sh` — blocks code writes without frozen specs (Edit|Write)
- `protect-frozen-files.sh` — blocks editing frozen files (Edit|Write, but FROZEN_PATTERNS currently empty)
- `block-dangerous.sh` — blocks destructive bash commands (Bash)
- `pre-commit-reminder.sh` — advisory only (Bash)

## NEXT STEP: Formulate revised design incorporating all red team feedback

Key design principles to address:
1. Accept that enforcement is advisory — optimize for guidance, not lockout
2. Fail-open on hook errors (never block all writes due to a bug)
3. Keep context budget lean (the crashed conversation is proof)
4. Make the sync engine simple and transparent (no fragile markdown parsing)
5. Support pre-existing projects gracefully
6. Allow legitimate one-off documents (escape hatch)
7. Version the template itself
