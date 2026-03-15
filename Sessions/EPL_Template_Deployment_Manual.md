# EPL Project Template v2.3.1 — Deployment Manual

**For:** Nathan (and anyone deploying the template into a project repo)
**Template repo:** `EpochLabsLLP/EPL-Project-Template` on GitHub
**Version file to check:** `.template_version` in any deployed project

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Scenario A: Fresh Project (No Existing Code)](#2-scenario-a-fresh-project)
3. [Scenario B: Existing Repo (Add Governance)](#3-scenario-b-existing-repo)
4. [Scenario C: Upgrading an Existing Deployment](#4-scenario-c-upgrading)
5. [Post-Deployment Verification](#5-post-deployment-verification)
6. [Customizing CLAUDE.md](#6-customizing-claudemd)
7. [Settings.json — Permissions Setup](#7-settingsjson-permissions)
8. [Troubleshooting](#8-troubleshooting)
9. [Cheat Sheet](#9-cheat-sheet)

---

## 1. Prerequisites

**On your machine:**
- Git (with GitHub auth configured)
- Python 3.x (hooks use `python` to parse JSON)
- Bash (hooks are shell scripts — on Windows, Git Bash or WSL works)
- Claude Code CLI installed

**On GitHub:**
- Your project repo exists (can be empty or have existing code)
- You have push access

**Files you need access to (one of):**
- A clone of `EpochLabsLLP/EPL-Project-Template` somewhere local, OR
- The workshop repo with the template at `template/` subdirectory

---

## 2. Scenario A: Fresh Project (No Existing Code)

This is the simplest path. You're starting a new project from scratch.

### Step 1: Clone the template into your project

```bash
# Clone the template repo
git clone https://github.com/EpochLabsLLP/EPL-Project-Template.git MyProject
cd MyProject

# Remove the template's git history and start fresh
rm -rf .git
git init
git add -A
git commit -m "Initialize from EPL Project Template v2.3.1"
```

### Step 2: Set your remote

```bash
git remote add origin https://github.com/YourOrg/MyProject.git
git push -u origin main
```

### Step 3: Customize CLAUDE.md

Open `CLAUDE.md` and replace all `{placeholders}`:
- `{ProjectName}` — your project name (appears ~10 times)
- `{one-sentence description}` — what the project is
- `{ecosystem/standalone}` — relationship to other projects
- `{Decision 1/2/3}` — your architectural load-bearing walls
- `{One sentence describing the specific quality bar}` — your Gold Rush bullet
- `{YYYY-MM-DD}` — today's date

### Step 4: Customize settings.json permissions

Open `.claude/settings.json`. The `permissions.allow` block has Nathan's Python paths. Replace with your own or clear it:

```json
"permissions": {
    "allow": []
}
```

Claude Code will prompt you for permissions as needed and you can approve them interactively. They'll accumulate here.

**Do NOT touch the `hooks` block.** That's managed by the template.

### Step 5: Verify

Open Claude Code in the project directory. You should see the session-start hook fire, showing `[SESSION START — MISSION ANCHOR]` followed by template awareness prompts.

Run `/governance-health` to verify all hooks, rules, and skills are intact.

**Done.** You're at v2.3.1 with full governance.

---

## 3. Scenario B: Existing Repo (Add Governance to Existing Code)

Your repo already has code, maybe specs, maybe its own CLAUDE.md. This is the most common real-world scenario.

### Step 1: Get the template files locally

```bash
# Clone the template repo alongside your project (not inside it)
git clone https://github.com/EpochLabsLLP/EPL-Project-Template.git /tmp/epl-template
```

Or if you have the workshop repo, the template is at `template/` inside it.

### Step 2: Run the sync engine in dry-run mode

```bash
cd /path/to/your/project
python /tmp/epl-template/template_sync.py /tmp/epl-template /path/to/your/project
```

This shows you exactly what will happen:
- **WILL CREATE** — files that don't exist in your project yet (hooks, rules, skills, templates)
- **WILL UPDATE** — files that exist but differ from the template (shouldn't happen on first deploy)
- **SKIPPED — PROJECT-OWNED** — your CLAUDE.md and README.md (never touched)
- **MISSING DIRECTORIES** — folders that need to be created (Specs/, Testing/, WorkOrders/, etc.)

**Review this output carefully.** Nothing is modified yet.

### Step 3: Apply the sync

```bash
python /tmp/epl-template/template_sync.py /tmp/epl-template /path/to/your/project --apply
```

This will:
- Create all missing directories (Specs/, Testing/, WorkOrders/, Sessions/, Code/, Research/, Notes/)
- Copy all infrastructure files (10 hooks, 6 rules, 16 skills, sync engine, manifest)
- Copy all template files (9 spec templates, 1 session template)
- Create `.claude/settings.json` with all hook registrations
- Create `.template_version` set to `2.3.1`
- Copy `CLAUDE.md` scaffold (only if no CLAUDE.md exists yet)
- **Back up** any overwritten files to `.template_backup/{timestamp}/`

### Step 4: Handle CLAUDE.md

**If you had no CLAUDE.md:** The template scaffold was created. Customize it per Step 3 in Scenario A above.

**If you already have a CLAUDE.md:** The sync engine skipped it (scaffolding = never overwrite). You have two options:

**Option A — Manual merge (recommended for complex existing CLAUDE.md):**
1. Open your existing CLAUDE.md and the template CLAUDE.md side by side
2. Carry over the sections you need:
   - Add `<!-- claude_md_version: 2.2.0 -->` as line 3
   - Add the Governance Heartbeat section
   - Add the Skills table
   - Add the Anti-Patterns section
   - Add the Key Specs section with traceability explanation
3. Keep your project-specific content (architecture decisions, custom rules)

**Option B — Use /template-migrate (in Claude Code):**
1. Open Claude Code in the project
2. Run `/template-migrate`
3. The skill will detect your CLAUDE.md as "unversioned/legacy"
4. It extracts project-specific data (name, description, load-bearing walls, custom sections)
5. Shows you a migration report — **review it carefully**
6. On your approval, it archives the old CLAUDE.md and writes the new one with your data merged in
7. If extraction fails (heavily customized format), it falls back to asking you what to carry forward

### Step 5: Customize settings.json permissions

Same as Scenario A Step 4 — replace Nathan's Python paths with your own or clear the block.

### Step 6: Handle existing code directories

The spec-gate checks for code in: `Code/`, `code/`, `src/`, `lib/`, `app/`, `packages/`. If your existing code is in one of these directories, **the code-gate will block new writes until you have frozen specs and an active Work Order.**

For existing projects with code already written, you have two approaches:

**Approach 1 — Retrofit specs (recommended):**
1. Create your PVD, Engineering Spec, Blueprint, and Testing Plans using `/init-doc`
2. Freeze them (set `**Status:** FROZEN` in the header)
3. Create a Work Order for your next piece of work
4. Now the code-gate allows writes

**Approach 2 — Move code first, then govern:**
If the project is mid-development and you can't freeze specs yet, temporarily keep code outside the governed directories (e.g., in a `dev/` or `draft/` folder). The code-gate only watches the directories listed above.

### Step 7: Commit and verify

```bash
git add .claude/ CLAUDE.md TEMPLATE_MANIFEST.json template_sync.py .template_version
git add Specs/ Testing/ WorkOrders/ Sessions/ CHANGELOG.md
# Don't add .template_backup/ — that's local
echo ".template_backup/" >> .gitignore
git commit -m "Deploy EPL governance template v2.3.1"
```

Run `/governance-health` in Claude Code to verify everything is working.

---

## 4. Scenario C: Upgrading an Existing Deployment

Your project already has v2.2.0 (or earlier) and you want to update to v2.3.1.

### Step 1: Get the latest template

```bash
# Pull latest from template repo
cd /tmp/epl-template
git pull origin main
```

### Step 2: Dry-run

```bash
cd /path/to/your/project
python /tmp/epl-template/template_sync.py /tmp/epl-template /path/to/your/project
```

The report will show:
- `UPGRADE: 2.2.0 -> 2.3.1 — See CHANGELOG.md for details.`
- CLAUDE.MD STRUCTURE OUTDATED warning (if no version marker)
- SETTINGS.JSON HOOK MERGE status
- Files that will be updated

### Step 3: Apply

```bash
python /tmp/epl-template/template_sync.py /tmp/epl-template /path/to/your/project --apply
```

All infrastructure files are overwritten (with backup). Your CLAUDE.md, README.md, and settings.json permissions are untouched. Hook registrations in settings.json are smart-merged.

### Step 4: CLAUDE.md migration (if needed)

If the sync report showed "CLAUDE.MD STRUCTURE OUTDATED", run `/template-migrate` in Claude Code to update the CLAUDE.md structure.

### Step 5: Verify

```bash
# Re-run sync — should show "fully in sync"
python /tmp/epl-template/template_sync.py /tmp/epl-template /path/to/your/project
```

Then `/governance-health` in Claude Code.

---

## 5. Post-Deployment Verification

After any deployment, run these checks:

### Quick check (command line)
```bash
# Version
cat .template_version
# → Should show: 2.3.1

# Hooks exist
ls .claude/hooks/
# → Should show 10 files (9 .sh + 1 .py)

# Rules exist
ls .claude/rules/
# → Should show 6 .md files

# Skills exist
ls .claude/skills/
# → Should show 16 directories
```

### Full check (in Claude Code)
```
/governance-health
```

This skill runs 11 checks:
1. All 10 hooks present and executable
2. All 6 rules present
3. All 16 skills present with valid SKILL.md
4. settings.json has correct hook registrations
5. TEMPLATE_MANIFEST.json matches .template_version
6. validate_traceability.py exists and runs
7. parse_hook_input.py exists
8. template_sync.py exists
9. Directory structure complete
10. CLAUDE.md has version marker
11. Hook registrations match manifest

### Smoke test (in Claude Code)
Try to write a file in `Code/` without frozen specs — the code-gate should block you with a clear message listing what's missing.

---

## 6. Customizing CLAUDE.md

### What you MUST customize
| Placeholder | Where | What to Put |
|-------------|-------|-------------|
| `{ProjectName}` | Throughout (~10 places) | Your project's name |
| `{one-sentence description}` | Identity section | What the project is |
| `{ecosystem/standalone}` | Identity section | "Epoch Labs ecosystem" or "standalone" |
| `{Decision 1/2/3}` | Load-Bearing Walls | Your architectural decisions (add more if needed) |
| `{quality bar sentence}` | Gold Rush Doctrine | Project-specific quality standard |
| `{YYYY-MM-DD}` | Header | Today's date |

### What you CAN customize
- Add more anti-patterns specific to your project
- Add more load-bearing walls (there's no limit)
- Add project-specific sections after the template sections
- Modify the escalation rules if someone other than Nathan is the decision-maker

### What you should NOT modify
- The Gold Rush Doctrine text (above the bullets) — it's universal
- The Governance Heartbeat section — it documents the hooks, don't desync
- The Skills table — it's updated by the template
- The `<!-- claude_md_version: X.Y.Z -->` marker — managed by template-migrate

---

## 7. Settings.json — Permissions Setup

`.claude/settings.json` has two blocks:

```json
{
    "permissions": { ... },   ← YOURS — project-owned, never overwritten
    "hooks": { ... }          ← TEMPLATE'S — managed by sync engine
}
```

### Permissions you might want to pre-approve

The `permissions.allow` array uses glob patterns. Common useful entries:

```json
"permissions": {
    "allow": [
        "Bash(python *)",
        "Bash(git status*)",
        "Bash(git log*)",
        "Bash(git diff*)",
        "Bash(npm test*)",
        "Bash(npm run *)"
    ]
}
```

Or start with an empty array and approve interactively — Claude Code saves your choices.

### Hook registrations (don't touch)

The `hooks` block has 10 hook registrations across 3 event types:
- **SessionStart** (3): startup, resume, compact
- **PreToolUse → Bash** (3): block-dangerous, commit-gate, dep-gate
- **PreToolUse → Edit|Write** (2): protect-frozen-files, spec-gate
- **PreToolUse → Write** (1): template-guard

Future syncs will add new hooks here without removing your custom hooks or permissions.

---

## 8. Troubleshooting

### "Permission denied" running hooks
Hooks are bash scripts. On Windows, make sure Git Bash is available. The hooks use `bash "$CLAUDE_PROJECT_DIR/.claude/hooks/..."` so bash must be on PATH.

### "python not found" in hooks
Hooks call `python` (not `python3`). If your system uses `python3`, create an alias or symlink.

### Code-gate blocks everything
This means specs aren't frozen or no Work Order is IN-PROGRESS. Check:
```bash
# Are specs frozen?
head -15 Specs/*Engineering_Spec* | grep FROZEN
head -15 Specs/*Blueprint* | grep FROZEN

# Is a WO active?
head -20 WorkOrders/*.md | grep IN-PROGRESS
```

### Commit-gate blocks commit
Run `/trace-check` to see what traceability chains are broken. Fix the broken references, then commit again.

### Session hooks don't fire
Check that `.claude/settings.json` has the hooks block. Run `/governance-health` to diagnose.

### "validate_traceability.py not found"
The script lives at `.claude/skills/trace-check/scripts/validate_traceability.py`. If missing, run template sync again.

### Template sync shows drift but files look identical
Could be line-ending differences (CRLF vs LF). The sync uses SHA-256 hash comparison, so any byte difference counts. Normalize line endings in your project: `git config core.autocrlf true`.

---

## 9. Cheat Sheet

### One-Time Setup (Fresh or Existing Repo)

```bash
# 1. Clone template
git clone https://github.com/EpochLabsLLP/EPL-Project-Template.git /tmp/epl-template

# 2. Dry-run (see what will happen)
python /tmp/epl-template/template_sync.py /tmp/epl-template ./my-project

# 3. Apply
python /tmp/epl-template/template_sync.py /tmp/epl-template ./my-project --apply

# 4. Customize CLAUDE.md (replace {placeholders})
# 5. Customize .claude/settings.json permissions block
# 6. Commit
git add .claude/ CLAUDE.md TEMPLATE_MANIFEST.json template_sync.py .template_version Specs/ Testing/ WorkOrders/ Sessions/ CHANGELOG.md
git commit -m "Deploy EPL governance template v2.3.1"

# 7. Verify (in Claude Code)
/governance-health
```

### Upgrading

```bash
# 1. Get latest template
cd /tmp/epl-template && git pull

# 2. Dry-run
python /tmp/epl-template/template_sync.py /tmp/epl-template ./my-project

# 3. Apply
python /tmp/epl-template/template_sync.py /tmp/epl-template ./my-project --apply

# 4. If CLAUDE.md outdated → /template-migrate (in Claude Code)

# 5. Verify
python /tmp/epl-template/template_sync.py /tmp/epl-template ./my-project
# → "Project is fully in sync with template."
```

### Day-to-Day Governance Flow

```
Start session → session-start.sh fires → read Work Ledger
  ↓
/spec-lookup <module>          ← load context
  ↓
/init-doc wo WO-N.M.T-X       ← create Work Order
Set WO to IN-PROGRESS          ← unlocks code-gate
  ↓
Write code in Code/src/...     ← code-gate checks specs + WO
  ↓
/dep-check <pkg>               ← before any dependency install
  ↓
/code-review <module>          ← quality review
/module-complete <module>      ← 6 quality gates
  ↓
Set WO to DONE
  ↓
/pre-commit                    ← hygiene check
git commit -m "WO-N.M.T-X: description"  ← commit-gate validates
```

### Key File Locations

| File | Purpose |
|------|---------|
| `.template_version` | Current governance version |
| `CLAUDE.md` | Project constitution (your file) |
| `TEMPLATE_MANIFEST.json` | File ownership manifest |
| `template_sync.py` | Sync engine |
| `CHANGELOG.md` | Version history + migration notes |
| `.claude/settings.json` | Hook registrations + permissions |
| `.claude/hooks/` | 10 enforcement hooks |
| `.claude/rules/` | 6 governance rules |
| `.claude/skills/` | 16 skill definitions |
| `Specs/Work_Ledger.md` | Auto-generated project status |
| `Specs/gap_tracker.md` | Tiered work items |
| `WorkOrders/` | Execution units |
| `.template_backup/` | Backups from sync (add to .gitignore) |

### Version Check

```bash
cat .template_version    # → 2.3.1
```

---

*EPL Project Template v2.3.1 | Epoch Labs, LLP*
