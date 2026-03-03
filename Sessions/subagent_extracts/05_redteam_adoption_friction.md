# 05_redteam_adoption_friction (agent-a255b6797f9fbdca3.jsonl)

## Message 1

I now have a comprehensive understanding of the entire system. Let me compile the exhaustive red team assessment.

---

# RED TEAM ASSESSMENT: Template Governance System
## Adoption & Usability Attack Surface

---

## CATEGORY 1: COMPONENTS THAT DON'T EXIST YET

### Finding 1.1: `/init-doc` Skill Does Not Exist
**The problem:** The task description references an `/init-doc` skill as a core workflow component, but no such skill exists in `.claude/skills/`. There is no `init-doc` directory, no SKILL.md for it, and no reference to it in CLAUDE.md's skills table. The entire "happy path" for creating documents from templates depends on a skill that has not been built.

**Who it affects:** Both Nathan and the agent. The agent has no `/init-doc` to invoke. Nathan will be told to use it and get nothing.

**Severity:** BLOCKING. The template guard hook (which also doesn't exist yet -- see 1.2) would require `TEMPLATE_SOURCE` markers that only `/init-doc` is supposed to inject. Without `/init-doc`, there is no sanctioned way to create spec documents.

**Suggested fix:** Build the skill before shipping the governance system. Alternatively, if the system is meant to be built incrementally, ship `/init-doc` first and the template guard hook second, so there's always a valid creation path before enforcement begins.

---

### Finding 1.2: Template Guard Hook Does Not Exist
**The problem:** The task description describes a "Template Guard Hook" that blocks spec document creation unless content includes `<!-- TEMPLATE_SOURCE: TEMPLATE_*.md -->`. No such hook exists in `.claude/hooks/`. The existing `protect-frozen-files.sh` protects frozen files, and `spec-gate.sh` gates code writes behind frozen specs. Neither enforces template sourcing.

**Who it affects:** The entire governance model. Without this hook, there is no enforcement that documents come from templates. The system described in the task is aspirational, not implemented.

**Severity:** BLOCKING for the described system. Non-blocking for current usage since the hook doesn't exist to cause friction.

**Suggested fix:** Build it, but see Finding 2.1 before doing so.

---

### Finding 1.3: `/template-sync` Skill Does Not Exist
**The problem:** No `/template-sync` skill directory exists. No `template_sync.py` script exists. No `TEMPLATE_MANIFEST.json` exists. The entire sync infrastructure is absent.

**Who it affects:** Both. Template evolution across projects has no mechanism.

**Severity:** BLOCKING for the described sync capability. Currently not causing friction because nothing references it.

**Suggested fix:** Build it, but carefully consider findings in Category 5 about sync complexity.

---

### Finding 1.4: Session-Start Does Not List Templates or Warn About settings.local.json
**The problem:** The task describes "Enhanced Session-Start" that lists available templates and warns about missing `settings.local.json`. The actual `session-start.sh` does neither. It reads the Work Ledger, Gap Tracker, and last session summary. No template listing. No settings warning.

**Who it affects:** Agents who need to discover templates.

**Severity:** Frustrating. Agents must independently discover templates by globbing for `TEMPLATE_*` files.

**Suggested fix:** Add these to session-start.sh, but see Finding 6.1 about information overload.

---

## CATEGORY 2: THE TEMPLATE GUARD CONCEPT IS HOSTILE TO LEGITIMATE WORKFLOWS

### Finding 2.1: Quick One-Off Documents Are Blocked
**The problem:** If the template guard enforces `TEMPLATE_SOURCE` markers on all writes to `Specs/`, `Testing/`, `Sessions/`, `WorkOrders/`, and root, then Nathan cannot create any document that doesn't fit a template. Examples: a quick meeting note in `Sessions/`, a research summary in `Specs/`, a competitive analysis, a tech spike writeup, a scratch document for brainstorming. None of these have templates, so the guard would block them.

**Who it affects:** Nathan and the agent. Nathan asks "write up notes from today's call" and the agent is blocked from writing to Sessions/.

**Severity:** BLOCKING. This would be the single most frustrating experience for a user. It turns a productivity tool into a permission gate.

**Suggested fix:** The guard should have a whitelist of document types that require templates (PVD, Blueprint, Engineering Spec, PRD, Product Brief, UX Spec, Testing Plans, Work Orders, Decision Record) and allow everything else through. The scope should be filename-pattern-based, not directory-based.

---

### Finding 2.2: The TEMPLATE_SOURCE Marker Is Visible Clutter
**The problem:** `<!-- TEMPLATE_SOURCE: TEMPLATE_PVD.md -->` is an HTML comment. While invisible in rendered Markdown, it is fully visible in raw editing. Nathan reads and edits these files in raw Markdown constantly. The marker is governance metadata polluting the document body.

**Who it affects:** Nathan, who reads raw Markdown.

**Severity:** Annoying. One line per document is minor, but multiplied across dozens of documents, it's papercut friction.

**Suggested fix:** The templates already have extensive HTML comments with usage instructions. Make the TEMPLATE_SOURCE marker part of the existing template header comment block rather than a separate line. Or better: don't use an in-document marker at all. Instead, have `/init-doc` log the template source in a manifest file (e.g., `.claude/template_origins.json`) and have the guard check that manifest.

---

### Finding 2.3: Manually Created Documents Require Workaround Knowledge
**The problem:** If Nathan manually copies a template (instead of using `/init-doc`), he must know to add the `TEMPLATE_SOURCE` marker. Nothing tells him this. He copies `TEMPLATE_PVD.md` to `VK_PVD_DRAFT.md`, fills it in, and the guard blocks edits because there's no marker.

**Who it affects:** Nathan, who is technically capable and may prefer direct file operations.

**Severity:** Frustrating. The error message needs to explain both what happened AND how to fix it (add the marker or use `/init-doc`).

**Suggested fix:** The error message must include the exact marker text to paste. Or better: if the file's content is >80% structurally similar to a template (same headings, same field table), accept it without the marker.

---

### Finding 2.4: No Escape Hatch for Intentional Divergence
**The problem:** If Nathan wants to create a PVD that intentionally deviates from the template structure (e.g., a minimal PVD for a tiny project, a PVD that uses a different section ordering for a specific audience), the guard blocks it. There is no `--force` equivalent, no override mechanism, no "I know what I'm doing" flag.

**Who it affects:** Nathan.

**Severity:** Frustrating to Blocking (depends on frequency). The Gold Rush Doctrine demands speed. Governance that slows down the person it's meant to serve is counter-productive.

**Suggested fix:** Add an override marker like `<!-- TEMPLATE_OVERRIDE: manual -->"` that the guard accepts. Log overrides to a manifest so they can be audited. The guard should warn but allow, not block.

---

## CATEGORY 3: AGENT DISCOVERY AND COGNITIVE LOAD

### Finding 3.1: Agent Does Not Know About `/init-doc` Unless Told
**The problem:** When a new Claude session starts, the CLAUDE.md skills table lists 12 skills. `/init-doc` is not among them (since it doesn't exist yet, but even when built, it needs to be added). A fresh agent asked "create a PVD" would naturally use the Write tool to create the file, not knowing `/init-doc` exists. The template guard would then block the write. The agent would be confused.

**Who it affects:** The agent. Every new session. Every time context is compacted.

**Severity:** Frustrating. The agent tries the obvious approach, gets blocked, reads the error message, and then has to figure out `/init-doc`. This wastes 2-3 round trips.

**Suggested fix:** Three-part fix: (1) Add `/init-doc` to the CLAUDE.md skills table. (2) Make the template guard's error message explicitly say "Use `/init-doc pvd` to create this document." (3) Add the template listing to session-start output as described in Finding 1.4.

---

### Finding 3.2: Remembering Exact Type Names for `/init-doc`
**The problem:** The `/init-doc` skill takes a document type argument. The user or agent must remember the exact type name: `pvd`, `blueprint`, `engineering-spec`, `prd`, `product-brief`, `ux-spec`, `testing-plans`, `work-order`, `decision-record`. That's 9 types. What if someone types `eng-spec` instead of `engineering-spec`? Or `test-plan` instead of `testing-plans`? Or `WO` instead of `work-order`?

**Who it affects:** Both Nathan and the agent.

**Severity:** Frustrating. Especially for Nathan who doesn't memorize CLI incantations.

**Suggested fix:** (1) Accept multiple aliases: `es`, `eng-spec`, `engineering-spec`, `engineering_spec` should all work. (2) If no match, list the valid types with descriptions. (3) Add tab-completion hints via the `argument-hint` field in SKILL.md frontmatter.

---

### Finding 3.3: 12+ Skills Create Decision Paralysis
**The problem:** The CLAUDE.md skills table already has 12 skills. Adding `/init-doc` and `/template-sync` makes 14. A new Claude instance reads this table and must internalize all 14 skills. This is a lot of context to load. The "When to Use" guidance is sometimes vague. Multiple skills have overlapping domains (e.g., `/spec-lookup` vs `/alignment-check` vs `/trace-check` -- all deal with specs).

**Who it affects:** The agent. Each skill consumes context budget.

**Severity:** Annoying. Skills are lazy-loaded (only SKILL.md frontmatter is read until invoked), but the table itself consumes context in CLAUDE.md which is always loaded.

**Suggested fix:** Group skills by workflow phase: "Spec Creation", "Implementation", "Validation", "Maintenance". Add a one-line flowchart: "Creating a doc? /init-doc. Writing code? /spec-lookup first. Done coding? /module-complete. Committing? /pre-commit."

---

### Finding 3.4: Session-Start Output Could Become Information Overload
**The problem:** If session-start is enhanced to include template listings alongside the Work Ledger, Gap Tracker, and last session summary, the startup output could easily exceed 100 lines. For a project with a full Work Ledger and Gap Tracker, this is already 50-80 lines. Adding template listings, settings.local.json warnings, and other diagnostics pushes it into "wall of text" territory that the agent must parse.

**Who it affects:** The agent. More startup context = less room for actual work.

**Severity:** Frustrating. The more you front-load, the less useful each piece becomes.

**Suggested fix:** Make template listing conditional: only show it when no specs exist yet (brand new project). Once a PVD exists, the templates are no longer novel information. Similarly, the settings.local.json warning should only fire once, not every session.

---

## CATEGORY 4: PRE-EXISTING PROJECTS (ADOPTION FRICTION)

### Finding 4.1: Projects That Predate the Template System
**The problem:** Epoch Labs has existing projects (like the one that produced this template). Those projects have specs, sessions, and work orders that were created without template markers, without the current naming conventions, and possibly without the traceability ID system. If `/template-sync` is run against such a project, what happens? The sync engine would see missing infrastructure files and try to apply them. But the existing project's `CLAUDE.md`, `settings.json`, hooks, and rules may conflict with or differ from the template.

**Who it affects:** Nathan and the agent. The first time Nathan tries to "upgrade" an existing project.

**Severity:** Frustrating to Blocking. If the sync engine blindly overwrites `CLAUDE.md` or `settings.json`, it destroys project-specific customizations. If it doesn't, the project has a mishmash of old and new conventions.

**Suggested fix:** Build an explicit "adoption mode" into `/template-sync` that: (1) Scans the project for existing conventions. (2) Presents a diff-style report of what would change. (3) Requires Nathan's approval before any changes. (4) Creates a backup branch before applying. (5) Tags existing documents with compatibility notes rather than requiring marker injection.

---

### Finding 4.2: No Migration Path for Existing Documents
**The problem:** Existing PVDs, Engineering Specs, etc. in pre-template projects lack `TEMPLATE_SOURCE` markers. Once the template guard is active, these documents cannot be edited. The agent would need to inject markers into every existing spec to "bless" them, which is busywork that adds no value.

**Who it affects:** Both.

**Severity:** Blocking. Editing existing specs in a newly-templated project is a core workflow.

**Suggested fix:** The template guard should have a "grandfather clause" -- documents that existed before the guard was installed should be exempt. Implementation: check the file's git creation date against the guard's installation date. Or: only enforce the marker for newly created files (check if the file already exists before blocking).

---

### Finding 4.3: Template Sync Categories Are Ambiguous in Practice
**The problem:** The three sync categories (infrastructure: overwrite, template: overwrite, scaffolding: section merge) seem clear in theory but are murky in practice. What is "infrastructure" vs "scaffolding"? If `CLAUDE.md` is infrastructure (overwrite), then project-specific customizations in CLAUDE.md get wiped. If it's scaffolding (section merge), which sections are template-controlled and which are project-controlled? The boundary is unclear.

**Who it affects:** Both.

**Severity:** Frustrating. Getting this wrong destroys work.

**Suggested fix:** Every file in TEMPLATE_MANIFEST.json needs explicit documentation of what "sync" means for that specific file. For CLAUDE.md specifically: template-controlled sections need clear delimiters (`<!-- TEMPLATE SECTION START -->` / `<!-- TEMPLATE SECTION END -->`), and everything outside those delimiters is project-controlled and untouched.

---

## CATEGORY 5: TEMPLATE SYNC ENGINE COMPLEXITY

### Finding 5.1: Python Dependency Is Not Guaranteed
**The problem:** `template_sync.py`, `validate_traceability.py`, and `parse_hook_input.py` all require Python. While Python is common, it's not universally installed or on PATH on Windows machines. Nathan's Windows 11 machine may have Python installed (since the hooks already use it), but if he sets up a new machine or a contractor joins, the entire hook and skill system silently fails.

**Who it affects:** Anyone setting up a new machine.

**Severity:** Blocking. If Python isn't available, `parse_hook_input.py` fails, which means `spec-gate.sh`, `block-dangerous.sh`, and `protect-frozen-files.sh` all fail. Depending on how they fail (exit code 0 vs non-zero), this either silently disables all guards or blocks all writes.

**Suggested fix:** (1) Add a Python check to session-start.sh: `which python || echo "WARNING: Python not found."` (2) Document the Python requirement prominently in project setup. (3) Consider whether the parse_hook_input.py functionality could be replaced with `jq` or bash-native JSON parsing for simpler hooks.

---

### Finding 5.2: parse_hook_input.py Failure Mode Is Silent
**The problem:** If `parse_hook_input.py` crashes (Python not found, malformed JSON, wrong field path), it prints an empty string. The calling shell scripts treat empty string as "no file path" and exit 0 (ALLOW). This means a crash in the parser silently disables all guards. A security hook that fails open is not a security hook.

**Who it affects:** The agent and Nathan (unknowingly).

**Severity:** Frustrating (subtle). The system appears to work but is not enforcing anything. This is worse than a loud failure.

**Suggested fix:** The shell scripts should check parse_hook_input.py's exit code. If Python fails to run, the hook should exit 2 (BLOCK) with an error message, not exit 0 (ALLOW). Fail closed, not open.

---

### Finding 5.3: Who Maintains TEMPLATE_MANIFEST.json?
**The problem:** When Nathan adds a new file to the template repository (e.g., a new rule file, a new template, a new skill), he must also update `TEMPLATE_MANIFEST.json`. This is a second step that is easily forgotten. The manifest and the actual file tree can drift apart.

**Who it affects:** Nathan.

**Severity:** Frustrating. Silent drift means `/template-sync` either misses new files (if they're not in the manifest) or errors on deleted files (if manifest references files that were removed).

**Suggested fix:** Auto-generate the manifest. A script that walks the template directory tree and produces `TEMPLATE_MANIFEST.json` based on file location and naming conventions. Run this as a pre-commit hook on the template repo itself.

---

### Finding 5.4: Backup Files Clutter the Project
**The problem:** The task describes infrastructure sync as "overwrite" with presumably some backup mechanism. If the sync engine creates `.bak` files or `_pre_sync_backup` copies every time it runs, the project accumulates clutter. Run sync 5 times, get 5 backup copies of each file.

**Who it affects:** Nathan (visual clutter), the agent (needs to distinguish current from backup files).

**Severity:** Annoying.

**Suggested fix:** Put backups in a single timestamped directory: `.claude/_sync_backups/YYYY-MM-DD/`. Prune backups older than 30 days automatically. Or: use git -- since the project is a git repo, the pre-sync state is already preserved in the commit history. Just commit before syncing.

---

### Finding 5.5: Git Conflicts from Sync Are Unexplained
**The problem:** If `/template-sync` modifies files that have uncommitted local changes, git will show conflicts or dirty state. Nathan may not understand why files he didn't touch are modified. The sync engine's changes are invisible to Nathan -- he didn't request them, didn't see them happen, and now git status shows unexpected modifications.

**Who it affects:** Nathan.

**Severity:** Frustrating. Unexpected git changes erode trust in the system.

**Suggested fix:** (1) `/template-sync` should refuse to run if there are uncommitted changes (warn and require commit first). (2) After sync, show a clear summary: "Updated 3 files, added 1 file, no conflicts." (3) Create a sync commit automatically: "template-sync: applied updates from template v2.1".

---

### Finding 5.6: Section Merge Is a Hard Problem
**The problem:** "Scaffolding (section merge)" means the sync engine needs to identify which sections of a file are template-controlled and which are project-customized, then merge only the template sections. This is a hard problem. Markdown has no machine-readable section ownership metadata. The merge algorithm will inevitably either: (a) clobber user customizations, or (b) leave stale template content in place because it couldn't tell user content from template content.

**Who it affects:** Both.

**Severity:** Frustrating to Blocking. If the merge is wrong, it corrupts documents silently.

**Suggested fix:** Abandon generic section merge. Instead, use explicit delimiters in files that need section-level sync. Sections between `<!-- TEMPLATE:START -->` and `<!-- TEMPLATE:END -->` are template-owned. Everything else is project-owned. This is ugly but unambiguous.

---

## CATEGORY 6: HOOK AND SYSTEM RELIABILITY

### Finding 6.1: Hook Timeout Could Block Legitimate Work
**The problem:** `spec-gate.sh` has a 10-second timeout. `protect-frozen-files.sh` and `block-dangerous.sh` have 5-second timeouts. On a slow machine, a large project directory, or when Python takes time to cold-start (especially on Windows where Python startup is notoriously slow), these hooks could timeout. What happens on timeout? If it blocks, the agent can't write anything. If it allows, the guard is bypassed.

**Who it affects:** The agent.

**Severity:** Frustrating (intermittent). Timeouts are non-deterministic, making them hard to diagnose.

**Suggested fix:** (1) Document Claude Code's timeout behavior (does timeout = allow or block?). (2) Increase timeouts for Windows. (3) Add timing diagnostics to hooks: if a hook takes >3s, log a warning. (4) Consider caching Python startup by keeping a warm process.

---

### Finding 6.2: Multiple Hooks on Write Create Cumulative Latency
**The problem:** Every `Edit` or `Write` operation triggers two hooks: `protect-frozen-files.sh` and `spec-gate.sh`. Each calls Python's `parse_hook_input.py`. That's two Python process launches per write. During a heavy coding session with hundreds of writes, this adds seconds of cumulative overhead. On Windows, Python process launch is especially slow (~200-500ms per invocation).

**Who it affects:** The agent (slower iteration).

**Severity:** Annoying. Death by a thousand cuts. Each individual write is only slightly slower, but cumulatively the session feels sluggish.

**Suggested fix:** (1) Combine the two hooks into a single script that does both checks in one Python invocation. (2) Use a faster parsing approach (bash-native `jq` or even `grep` for the simple field extraction).

---

### Finding 6.3: spec-gate.sh Only Gates "Code/" Directories But Lists Six Directories
**The problem:** `spec-gate.sh` checks if the target file is in `Code/`, `code/`, `src/`, `lib/`, `app/`, or `packages/`. But many real projects use different directory structures: `backend/`, `frontend/`, `server/`, `client/`, `api/`, `functions/`, `lambda/`, `services/`. A project using any of these would have code writes that bypass the spec gate entirely.

**Who it affects:** The agent and Nathan.

**Severity:** Frustrating (silent failure). The gate exists but doesn't protect.

**Suggested fix:** Make the code directory list configurable per-project, perhaps in `CLAUDE.md`'s Architecture section or in a `.claude/config.json`. The template should provide sensible defaults but allow override.

---

### Finding 6.4: FROZEN Detection Is Fragile
**The problem:** Both `spec-gate.sh` and `validate_traceability.py` detect "frozen" status by checking if the word `FROZEN` appears in the first 15 lines. This is fragile: (1) If the status table is pushed below line 15 by a long title or extra metadata, FROZEN won't be found. (2) If someone writes "This document is NOT yet FROZEN" in the header comment, it matches as frozen. (3) If someone uses lowercase "frozen", it won't match (bash `grep -q "FROZEN"` is case-sensitive).

**Who it affects:** The agent.

**Severity:** Frustrating. False negatives (frozen doc not detected) block code writes unnecessarily. False positives (unfrozen doc detected as frozen) allow premature code writes.

**Suggested fix:** Use a more precise pattern: `grep -q '| **Status** | FROZEN |'` or similar structured match. Or define a canonical marker: `<!-- STATUS: FROZEN -->` in a specific position that can't be confused.

---

### Finding 6.5: spec-gate.sh Uses `head -15` Which Is Not Robust
**The problem:** Related to 6.4 but distinct: `head -15 "$f"` in bash reads from a file on disk. But the file being checked is the existing file, not the content being written. If the agent is creating a new spec file and writing it for the first time, the file may not exist yet when the hook fires. Worse, the hook checks all spec files in the `Specs/` directory, so it's checking the *other* specs' frozen status, not the file being written. This is actually correct for the spec-gate's purpose (gatekeeping code writes behind frozen specs), but it's confusing to debug.

**Who it affects:** Anyone debugging why the hook allows or blocks.

**Severity:** Annoying (confusing logic flow).

**Suggested fix:** Add inline comments to the hook explaining: "We check frozen status of OTHER spec files, not the file being written. This hook gates code writes, not spec writes."

---

## CATEGORY 7: WORKFLOW AND PROCESS FRICTION

### Finding 7.1: Nine Document Types Must Be Created In Strict Order
**The problem:** The spec-readiness guide mandates: PVD -> Engineering Spec -> UX Spec -> Blueprint -> Testing Plans -> Gap Tracker -> Decision Record. That's 7 documents (minimum) before coding can begin. For a small project or a quick prototype, this is an enormous upfront investment. Nathan's Gold Rush Doctrine says "move fast" but the SDD framework says "freeze 4-7 specs before writing a single line of code."

**Who it affects:** Nathan.

**Severity:** Frustrating. The tension between "move fast" and "spec everything first" is fundamental. For a 2-week project, spending 3 days on specs feels disproportionate.

**Suggested fix:** Define a "lightweight path" for small projects. A minimal PVD (1 page) with just features and acceptance criteria, a minimal Engineering Spec (just the tech stack and module list), no Blueprint (go straight to Gap Tracker), no formal Testing Plans (inline test cases in the Gap Tracker). The full SDD framework is for flagship products. Not everything is a flagship.

---

### Finding 7.2: Template Guard + Spec Gate Create a Catch-22 for New Projects
**The problem:** A new project starts with nothing. To create a PVD, the agent must use `/init-doc pvd`. The template guard requires the TEMPLATE_SOURCE marker. That's fine -- `/init-doc` handles it. But what about the CLAUDE.md file itself? It needs project-specific customization. Is it gated? What about `.claude/rules/*.md` files? What about the `gap_tracker.md`? The template guard's directory scope (`Specs/`, `Testing/`, `Sessions/`, `WorkOrders/`, root) could inadvertently block modifications to the governance files themselves.

**Who it affects:** The agent during initial project setup.

**Severity:** Potentially Blocking. The guard blocks the very files needed to set up the guard.

**Suggested fix:** Explicitly exclude governance infrastructure files from the guard: `.claude/*`, `CLAUDE.md`, `gap_tracker.md`, `Work_Ledger.md`, `*.gitkeep`. Only guard actual deliverable documents.

---

### Finding 7.3: Testing Plans Template Lives in Testing/ but Others Live in Specs/
**The problem:** The Testing Plans template (`TEMPLATE_Testing_Plans.md`) is in `Testing/` while all other templates are in `Specs/`. When Nathan or an agent looks for templates, they'll check `Specs/TEMPLATE_*` and miss the testing one. Alternatively, they'll look for the testing template in `Specs/` and not find it.

**Who it affects:** Both.

**Severity:** Annoying. Minor confusion, easily resolved, but it's a papercut.

**Suggested fix:** Either (a) put all templates in a single `Specs/` directory (current approach, mostly, but testing is the exception), or (b) create a dedicated `Templates/` directory for all templates, or (c) ensure `/init-doc` abstracts away the location so nobody needs to find templates manually.

---

### Finding 7.4: protect-frozen-files.sh Has an Empty Frozen List
**The problem:** The `protect-frozen-files.sh` hook has `FROZEN_PATTERNS=()` -- an empty array with commented-out examples. This means the hook currently protects nothing. It runs on every Edit/Write, consuming Python startup time, but does zero useful work. Worse, it must be manually updated per-project by editing a shell script, which is not something Nathan should be doing.

**Who it affects:** Nathan (must manually edit a shell script to activate protection).

**Severity:** Frustrating. The hook is inert out of the box. Nathan must know to find this obscure file and edit it. If he doesn't, frozen files get silently modified.

**Suggested fix:** Auto-populate the frozen patterns by reading the FROZEN status from spec files (the same check spec-gate.sh already does). If a file contains `| **Status** | FROZEN |` in its header, protect it. No manual editing needed.

---

### Finding 7.5: No Way to Create Multiple Variants of the Same Document Type
**The problem:** What if Nathan wants two PVD variants -- one for consumer products and one for developer tools? Or a "mini PVD" for spikes vs a "full PVD" for flagship products? The `/init-doc` skill maps type names to single templates. There's no way to select a variant.

**Who it affects:** Nathan, as the template system matures.

**Severity:** Annoying initially, Frustrating long-term.

**Suggested fix:** Support variant syntax: `/init-doc pvd:mini` or `/init-doc pvd --variant=lightweight`. Default to the standard template if no variant is specified. Store variants as `TEMPLATE_PVD_mini.md`, `TEMPLATE_PVD_full.md`.

---

### Finding 7.6: WorkOrders Directory Is Referenced But Has No Template Guard Coverage
**The problem:** The task description says the template guard covers `WorkOrders/`, but Work Orders are created frequently during development. If every WO creation requires `/init-doc work-order`, that's a lot of ceremonial overhead for a document that is essentially a structured form with a predictable format.

**Who it affects:** The agent.

**Severity:** Frustrating. WOs are high-frequency documents. Adding friction to their creation slows execution.

**Suggested fix:** Either (a) don't guard WOs (trust the agent to use the template), or (b) make `/init-doc work-order BP-3.2.4` auto-populate the traceability chain, task list, and testing requirements from the Blueprint and Testing Plans, turning the guard into a value-add rather than just a gate.

---

## CATEGORY 8: SETTINGS AND CONFIGURATION FRICTION

### Finding 8.1: settings.local.json Must Be Manually Created
**The problem:** The template ships `settings.local.json.example` with a comment "Copy this file to settings.local.json and customize." This is a manual step that every new project must perform. If it's not done, the project has no `settings.local.json`, which means no permissions are configured, and every tool invocation triggers a permission prompt.

**Who it affects:** Nathan (first setup of every project).

**Severity:** Frustrating. First-run experience is crippled by permission prompts until Nathan realizes he forgot this step.

**Suggested fix:** (1) Have the session-start hook check for settings.local.json and, if missing, copy the example file automatically (with a message). (2) Or make `/template-sync` handle this as part of project initialization. (3) At minimum, the session-start warning should include the exact command: `cp .claude/settings.local.json.example .claude/settings.local.json`.

---

### Finding 8.2: settings.json Merge Semantics Are Unclear
**The problem:** `settings.json` holds hooks. `settings.local.json` holds permissions. Claude Code merges them. But what if `/template-sync` updates `settings.json` with new hooks? Does the merge still work? What if someone accidentally puts permissions in `settings.json`? What if `settings.local.json` has hooks? The merge behavior is Claude Code internals, not documented in the project.

**Who it affects:** Both.

**Severity:** Annoying. Ambiguity about merge semantics leads to subtle bugs.

**Suggested fix:** Add a comment in both files explaining the split: "`settings.json`: HOOKS ONLY (template-managed, do not add permissions). `settings.local.json`: PERMISSIONS ONLY (per-machine, not committed)." Add a validation check to session-start that warns if permissions appear in settings.json or hooks appear in settings.local.json.

---

### Finding 8.3: MCP Server Configuration Is Global
**The problem:** `.mcp.json` configures Context7 as the default MCP server. Template sync would overwrite this. But some projects may need additional MCP servers (Playwright, database, custom APIs). If `/template-sync` overwrites `.mcp.json`, project-specific MCP configurations are lost.

**Who it affects:** Projects with custom MCP needs.

**Severity:** Blocking for those projects. A single `npx` command replacing a carefully configured MCP setup is destructive.

**Suggested fix:** `.mcp.json` should be "scaffolding" category (section merge), not "infrastructure" (overwrite). Or better: sync should only add the Context7 entry if it's missing, never remove existing entries.

---

## CATEGORY 9: ERROR MESSAGES AND DEBUGGING

### Finding 9.1: Hook Error Messages Don't Tell You What to Do
**The problem:** The spec-gate error message is: "SPEC GATE BLOCKED: Cannot write to code files until required specs are frozen. Missing/unfrozen: PVD (or Product Brief + PRD), Engineering Spec, Blueprint, Testing Plans." This tells you what's wrong but not what to do about it. A confused agent might try to create all 4 specs from scratch. A confused Nathan might not know these are template documents.

**Who it affects:** Both.

**Severity:** Frustrating.

**Suggested fix:** Add actionable guidance: "Use `/init-doc pvd` to create the PVD from template. See CLAUDE.md > Key Specs for the document creation sequence. Freeze specs by setting Status to FROZEN in the document header."

---

### Finding 9.2: No Diagnostic Command for "Why Is My Write Blocked?"
**The problem:** When a hook blocks a write, the error message appears inline. But there's no way to proactively check "will this write be blocked?" before attempting it. The agent must attempt the write, get blocked, read the error, fix the issue, and retry. For spec-gate, this means potentially fixing 4 missing specs before a single line of code can be written.

**Who it affects:** The agent.

**Severity:** Frustrating.

**Suggested fix:** Add a `/check-readiness` or `/spec-status` skill that runs the same checks as the hooks but as a proactive diagnostic. "Before writing code, run `/spec-status` to see what's missing."

---

### Finding 9.3: template_sync.py Has No Error Handling for Missing Template Repo
**The problem:** `template_sync.py` (when built) will need to know where the template repo is. How does it find `_ProjectTemplate`? Is the path hardcoded? Is it a CLI argument? An environment variable? If the template repo is on a different drive, a network share, or not cloned locally, the script fails. The error message needs to be clear about what path it expected and how to configure it.

**Who it affects:** Nathan.

**Severity:** Blocking (first run). If the script can't find the template, it can't sync.

**Suggested fix:** Make the template repo path a required argument: `/template-sync --template-repo "C:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate"`. Or store it in a project-level config file. Never hardcode paths.

---

## CATEGORY 10: CONCEPTUAL AND ARCHITECTURAL ISSUES

### Finding 10.1: The Template Guard Is Solving a Problem That Doesn't Exist Yet
**The problem:** The template guard prevents agents from creating spec documents without templates. But in practice, Claude instances already follow CLAUDE.md instructions to use templates. The rules files, CLAUDE.md constitution, and session-start context all reinforce template usage. Adding a hard enforcement hook adds friction for the compliant case (legitimate template usage requires a marker) without much benefit (agents rarely create rogue specs when properly instructed).

**Who it affects:** Both.

**Severity:** Philosophical. The guard trades occasional drift prevention for constant friction.

**Suggested fix:** Consider whether the template guard is necessary at all. An alternative: make `/init-doc` the recommended path, make the templates discoverable, but don't hard-block non-template writes. Instead, have a post-session audit skill that checks for documents without template origins and flags them. Guidance over gates.

---

### Finding 10.2: The Traceability System Is the Real Governance -- Template Guard Is Overhead
**The problem:** The traceability system (`validate_traceability.py`, `/trace-check`, Work Ledger) already enforces structural integrity. It checks that PVDs have ES modules, ES modules have Blueprint tasks, tasks have tests. This is the real governance. The template guard adds a second governance layer that validates document *provenance* (where did the file come from?) rather than document *content* (does the file have the right structure?). Content governance is more valuable than provenance governance.

**Who it affects:** The overall system design.

**Severity:** Annoying (unnecessary complexity).

**Suggested fix:** Invest more in content validation (does the PVD have all required sections? Are PVD-N identifiers assigned?) and less in provenance validation (did this file come from a template?). `/trace-check` already does some content validation. Extend it rather than adding a separate template guard layer.

---

### Finding 10.3: The gap_tracker.md Still References "mission-lock" in Scope Guards
**The problem:** Line 25 of `gap_tracker.md` says: "Exception: Nathan can explicitly authorize out-of-order work (log in mission-lock deviation log)". The mission-lock has been archived (see `_Archive/mission-lock.md.archived`). The reference should be to the Decision Record, per the change-control rule.

**Who it affects:** The agent (follows outdated instructions).

**Severity:** Annoying. Minor inconsistency that causes brief confusion.

**Suggested fix:** Update gap_tracker.md line 25 to reference the Decision Record instead of mission-lock.

---

### Finding 10.4: The advanced_patterns.md Still References Mission Lock
**The problem:** In `Guides/advanced_patterns.md`, line 105, the "Where to Put Them" section says structured criteria belong in "Mission Lock (`/.claude/rules/mission-lock.md`)". The Mission Lock has been archived and replaced by the change-control system.

**Who it affects:** The agent following guidance from this file.

**Severity:** Annoying. References a non-existent file.

**Suggested fix:** Update the reference to point to the current governance mechanism (change-control.md, Decision Record, or CLAUDE.md as appropriate).

---

### Finding 10.5: Template Testing Plans Uses "testing_plan" in Filename Check But Template Uses "Testing_Plans"
**The problem:** In `validate_traceability.py` line 100, the code checks `if "testing_plan" in name` (singular, underscore). But the template file is named `TEMPLATE_Testing_Plans.md` (plural, capitalized). After copying the template, the user might name the file `VK_Testing_Plans_v1.md`. The lowercased check `"testing_plan"` would NOT match `"testing_plans"` because `"testing_plan"` is not a substring of `"testing_plans"` -- wait, actually `"testing_plan"` IS a substring of `"testing_plans"`. So this works by accident. But the spec-gate.sh at line 110 checks `*Testing_Plans*` with a glob, which is case-sensitive and expects the exact casing. Inconsistency in case handling between Python and bash checks could create edge-case failures.

**Who it affects:** The agent.

**Severity:** Annoying (latent bug).

**Suggested fix:** Standardize: use the same matching logic in both places. Preferably case-insensitive contains-check on the canonical name.

---

## CATEGORY 11: WINDOWS-SPECIFIC ISSUES

### Finding 11.1: Bash Hooks on Windows Require Git Bash or WSL
**The problem:** All hooks are `.sh` files. Windows doesn't natively run bash. Claude Code on Windows uses bash (per the environment info), likely Git Bash. But `$CLAUDE_PROJECT_DIR` on Windows produces paths like `c:\Claude Folder\...` with backslashes and spaces. The hooks use Unix-style path handling. `parse_hook_input.py` normalizes backslashes to forward slashes, but the shell scripts do their own path manipulation that may break with Windows paths containing spaces (like `"Claude Folder"`).

**Who it affects:** Nathan (Windows user).

**Severity:** Potentially Blocking. Path issues on Windows are the #1 cause of shell script failures.

**Suggested fix:** (1) Ensure all path references in shell scripts are double-quoted (they are, mostly). (2) Test every hook on a Windows path with spaces. (3) Consider adding a Windows-specific path normalization function at the top of each hook.

---

### Finding 11.2: `ls -t` Behavior in Session-Start on Windows
**The problem:** `session-start.sh` line 54 uses `ls -t "$SESSIONS_DIR"/*.md` to find the most recent session. On Windows/Git Bash, `ls` timestamp sorting can behave differently than on Unix. More critically, if `SESSIONS_DIR` contains spaces (it does: `C:\Claude Folder\...`), the glob may not expand correctly even with quotes.

**Who it affects:** Nathan.

**Severity:** Annoying (session context may not load correctly).

**Suggested fix:** Use `find` with `-newer` or Python for cross-platform reliable file sorting by modification time.

---

## CATEGORY 12: ONBOARDING EXPERIENCE

### Finding 12.1: No "Getting Started" Flow
**The problem:** A new user/agent opening a fresh project from this template sees: CLAUDE.md (long constitutional document), 8 template files, 12 skills, 5 hooks, 7 rules files, a guide. There is no single "start here" document that walks through the first-time setup: "Step 1: Copy settings.local.json. Step 2: Create your PVD. Step 3: Run /trace-check." The system assumes familiarity.

**Who it affects:** Nathan (first project from template), any future Epoch Labs team member.

**Severity:** Frustrating. The first 30 minutes with the template are spent reading governance documents instead of building.

**Suggested fix:** Add a `QUICKSTART.md` (or a "Getting Started" section at the top of CLAUDE.md) with a 10-step numbered walkthrough. Or better: make the session-start hook detect "brand new project" (no specs, no sessions, no commits beyond template) and output a guided onboarding sequence.

---

### Finding 12.2: CLAUDE.md Has Project-Specific Placeholders That Must Be Replaced
**The problem:** The template CLAUDE.md is full of `{ProjectName}`, `{Decision 1}`, `{Choice}`, `{One-sentence description}` placeholders. If these aren't replaced before the first session, the agent reads a constitution full of placeholder text and doesn't know what the project is about.

**Who it affects:** The agent (confused by placeholders), Nathan (must manually replace them).

**Severity:** Frustrating.

**Suggested fix:** Make `/init-doc` also work for CLAUDE.md: `/init-doc project --name "ViviGames" --abbrev "VK"` that replaces all `{ProjectName}` and `{Abbrev}` placeholders throughout the template. Or add this as a `/project-init` skill that runs once at project creation.

---

### Finding 12.3: The Skills Table in CLAUDE.md Uses `/skill-name <args>` Format But That's Not How Claude Code Skills Work
**The problem:** The skills table shows invocations like `/spec-lookup <module>`. But Claude Code skills are invoked by name, and the arguments are described by `argument-hint` in the SKILL.md frontmatter. The user types `/spec-lookup auth` not `/spec-lookup <module>`. The angle brackets in the table suggest command-line syntax that doesn't exist. A user might literally type `<module>`.

**Who it affects:** Nathan (if he manually types skill invocations).

**Severity:** Annoying. Minor formatting confusion.

**Suggested fix:** Use example values instead of angle brackets: `/spec-lookup auth-module` instead of `/spec-lookup <module>`.

---

## SUMMARY: TOP 5 HIGHEST-IMPACT ISSUES

1. **The system described doesn't exist yet.** `/init-doc`, template guard hook, `/template-sync`, and `TEMPLATE_MANIFEST.json` are all unbuilt. Ship them or don't describe them. (Findings 1.1-1.4)

2. **The template guard concept blocks legitimate work.** Quick documents, one-off notes, and non-template document types get blocked. Directory-based scoping is too broad. (Findings 2.1, 2.4, 7.2)

3. **Pre-existing projects have no migration path.** Adopting the template system into existing projects is destructive without careful adoption tooling. (Findings 4.1, 4.2)

4. **parse_hook_input.py fails open.** A Python crash silently disables all security and governance hooks. This is a design flaw, not a feature. (Finding 5.2)

5. **The governance-to-velocity ratio is wrong for small projects.** Nine document types, strict ordering, four frozen specs before any code -- this is flagships-only process applied uniformly. (Finding 7.1)

---

## SCORING SUMMARY

| Severity | Count |
|----------|-------|
| Blocking | 11 |
| Frustrating | 18 |
| Annoying | 10 |
| **Total** | **39** |

