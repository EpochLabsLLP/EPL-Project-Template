# 03_redteam_bypass_vectors (agent-aefc7ee6cfbcdc026.jsonl)

## Message 1

Now I have a complete picture of the system. Let me compile the exhaustive red team analysis.

---

# RED TEAM ANALYSIS: Template Guard System Bypass Vectors

## System Under Test

A proposed `template-guard.sh` PreToolUse hook on `Write` that enforces template usage for new spec/session/work-order files. The hook checks for a `<!-- TEMPLATE_SOURCE: TEMPLATE_*.md -->` marker in Write content for files matching governed patterns in governed directories.

---

## CATEGORY 1: TOOL-LEVEL BYPASSES (Alternative Write Mechanisms)

### BYPASS 1.1: Edit Tool -- Create via "Empty Old String"

**The bypass:** The agent uses the `Edit` tool with `old_string: ""` and `new_string: "<full file content without template marker>"` on a file that doesn't exist yet. The Edit tool creates a new file when the target doesn't exist and `old_string` is empty.

**Why it works:** The `settings.json` matcher is `"Edit|Write"` for the existing hooks (protect-frozen-files, spec-gate), but the proposed template-guard is described as firing "on every Write operation." If the template guard's matcher is only `Write` (not `Edit|Write`), the Edit tool is completely unmonitored. Even if it IS `Edit|Write`, the hook only receives `tool_input.file_path`, `tool_input.old_string`, and `tool_input.new_string` for Edit -- NOT `tool_input.content`. The hook cannot inspect whether the template marker is present because it never sees the full assembled file content.

**Severity:** CRITICAL. This is the single largest hole. The Edit tool is a fully functional file creation mechanism that the template guard structurally cannot inspect for content compliance.

**Suggested fix:** Two options: (A) Add a secondary hook specifically for Edit that checks if the target file is new (doesn't exist) and the target path matches governed patterns -- if so, BLOCK and require the agent to use Write with a template. (B) After Edit completes, add a PostToolUse hook that reads the resulting file and checks for the template marker. Option A is simpler and more secure.

---

### BYPASS 1.2: Bash Tool -- Direct File Creation

**The bypass:** The agent uses Bash to create the file directly via any of dozens of commands:
- `echo "content" > Specs/MyProject_PVD_v1.md`
- `cat > Specs/MyProject_PVD_v1.md << 'EOF' ... EOF`
- `printf "content" > Specs/MyProject_PVD_v1.md`
- `tee Specs/MyProject_PVD_v1.md <<< "content"`
- `python -c "open('Specs/MyProject_PVD_v1.md','w').write('content')"`
- `cp /dev/stdin Specs/MyProject_PVD_v1.md`
- `dd of=Specs/MyProject_PVD_v1.md <<< "content"`
- `node -e "require('fs').writeFileSync('Specs/MyProject_PVD_v1.md','content')"`
- `powershell -c "Set-Content Specs/MyProject_PVD_v1.md 'content'"`

**Why it works:** The template guard fires on `Write` (or `Edit|Write`). The Bash tool has its own hook (`block-dangerous.sh`) but that only blocks destructive git commands, `rm -rf`, and `DROP TABLE/DELETE FROM`. It does not check whether Bash is creating files in governed directories.

**Severity:** CRITICAL. The `block-dangerous.sh` hook is trivially insufficient to prevent file creation. There are effectively infinite ways to create files from Bash.

**Suggested fix:** Add to `block-dangerous.sh` (or a new hook) a check that detects writes to governed directories. This is extremely hard to do comprehensively in Bash -- you'd need to detect output redirections (`>`, `>>`, `tee`), file-writing commands, and scripting language invocations. A more practical approach: add a PostToolUse hook that runs after every Bash command and scans the governed directories for new files that lack the template marker, then alerts/blocks.

---

### BYPASS 1.3: Bash Tool -- Copy/Move from Ungoverned Location

**The bypass:** The agent:
1. Uses `Write` to create the file at an ungoverned path (e.g., `/tmp/MyProject_PVD_v1.md` or `Notes/draft.md`) -- no template marker needed because it's not in a governed directory.
2. Uses Bash: `cp /tmp/MyProject_PVD_v1.md Specs/MyProject_PVD_v1.md` or `mv Notes/draft.md Specs/MyProject_PVD_v1.md`.

**Why it works:** The template guard only fires on `Write` tool calls. File system operations (cp, mv) through Bash are a different tool. The `block-dangerous.sh` hook doesn't check for `cp` or `mv` into governed directories.

**Severity:** CRITICAL. This is a two-step bypass that uses only "approved" operations at each step.

**Suggested fix:** Either (A) add `cp` and `mv` detection to governed directories in the Bash hook, or (B) use a PostToolUse hook to scan for new ungoverned files after any Bash execution, or (C) add a file-system watcher (inotify/fswatch) that validates new files in governed directories regardless of how they were created.

---

### BYPASS 1.4: Bash Tool -- Git Checkout / Git Restore

**The bypass:** The agent commits a non-template file on another branch, then:
- `git checkout other-branch -- Specs/MyProject_PVD_v1.md`
- `git restore --source=other-branch Specs/MyProject_PVD_v1.md`
- `git show other-branch:Specs/MyProject_PVD_v1.md > Specs/MyProject_PVD_v1.md`

**Why it works:** The `block-dangerous.sh` hook blocks `git reset --hard`, `git push --force`, `git clean -f`, `git branch -D`, but does NOT block `git checkout -- <file>`, `git restore`, or `git show`. These are legitimate git operations that happen to create/overwrite files.

**Severity:** HIGH. Requires a multi-step setup but is entirely feasible for a motivated or confused agent.

**Suggested fix:** Add `git checkout.*--.*Specs/|git restore.*Specs/|git show.*>.*Specs/` patterns to the Bash guard for governed directories.

---

### BYPASS 1.5: NotebookEdit Tool

**The bypass:** The agent uses `NotebookEdit` to create a `.ipynb` file in a governed directory (e.g., `Specs/MyProject_Engineering_Spec.ipynb`). While `.ipynb` is not `.md`, the filename contains the governed pattern `Engineering_Spec`.

**Why it works:** The template guard fires on `Write` (and possibly `Edit`). `NotebookEdit` is a completely separate tool with no hook attached. The settings.json shows it's in the allowed permissions list.

**Severity:** MEDIUM. The `.ipynb` format is unusual for specs, but if the filename pattern check is based on substrings, it would match and should be blocked. Since it's not `.md`, it may be an edge case. The real risk is if an agent stores spec content in a notebook cell as a workaround.

**Suggested fix:** Either add `NotebookEdit` to the matcher, or restrict the pattern check to `.md` files only (the more pragmatic fix since notebooks aren't spec documents).

---

### BYPASS 1.6: MCP Tools -- Chrome DevTools File Download

**The bypass:** The agent uses `mcp__chrome-devtools__evaluate_script` to execute JavaScript that creates a file:
```javascript
() => {
  // Use a data URL or fetch to construct content, then trigger download
  // Or if the browser has file system access...
}
```

Or more practically, the agent navigates to a page that contains the desired content and uses `mcp__chrome-devtools__take_screenshot` with `filePath` pointing to a governed directory (though this creates an image, not a markdown file).

**Why it works:** MCP tool calls don't go through the PreToolUse hooks unless explicitly matched in settings.json. The hooks matcher is `"Edit|Write"` -- MCP tools have different names like `mcp__chrome-devtools__*`.

**Severity:** LOW. The Chrome DevTools tools can't directly write arbitrary text files to the filesystem in most configurations. The `filePath` parameter on `take_screenshot` creates images, not markdown. However, if any MCP tool with file-write capability is added in the future, this becomes a real vector.

**Suggested fix:** Add a catch-all PostToolUse hook that monitors governed directories for new files regardless of creation source.

---

## CATEGORY 2: PATTERN EVASION BYPASSES

### BYPASS 2.1: Filename Pattern Evasion -- Synonym/Abbreviation

**The bypass:** Instead of `MyProject_PVD_v1.md`, the agent creates:
- `MyProject_Product_Vision_v1.md` (full name instead of abbreviation)
- `MyProject_Vision_Doc_v1.md`
- `MyProject_Requirements_v1.md` (instead of PRD)
- `MyProject_Arch_Spec_v1.md` (instead of Engineering_Spec)
- `MyProject_Build_Plan_v1.md` (instead of Blueprint)
- `MyProject_Test_Spec_v1.md` (instead of Testing_Plans)

**Why it works:** The guard checks for specific substrings: `PVD`, `PRD`, `Engineering_Spec`, `Blueprint`, `UX_Spec`, `Testing_Plans`, `Decision_Record`, `Work_Order`, `gap_tracker`, `Work_Ledger`, `session_`. If the agent uses a semantically equivalent but syntactically different name, the pattern doesn't match and the guard allows the write.

**Severity:** HIGH. The agent creates a fully functional spec document that bypasses all template enforcement. Downstream tools (spec-gate, trace-check) may also fail to find these files, creating a false sense of compliance.

**Suggested fix:** (A) Use broader pattern matching -- e.g., block ANY new `.md` file in `Specs/`, `Testing/`, `WorkOrders/`, and `Sessions/` that doesn't have the template marker, regardless of filename. (B) Maintain a positive list: only allow files that match the naming convention AND have the template marker. Everything else is blocked.

---

### BYPASS 2.2: Case Sensitivity Evasion

**The bypass:** The agent creates:
- `Specs/MyProject_pvd_v1.md` (lowercase)
- `Specs/MyProject_Pvd_v1.md` (mixed case)
- `Specs/MyProject_PVD_V1.MD` (uppercase extension)
- `Specs/MyProject_engineering_spec_v1.md`

**Why it works:** On Windows (where this system runs), the filesystem is case-insensitive but the Bash `grep` pattern matching in the hook is case-sensitive by default. If the hook uses `grep -q "PVD"`, it won't match `pvd` or `Pvd`. The file will exist on disk and be readable by everything, but the guard won't recognize it as a governed file.

**Severity:** HIGH. Windows case-insensitivity makes this especially dangerous -- the file `pvd.md` and `PVD.md` are the SAME file on NTFS, but the guard only blocks one pattern.

**Suggested fix:** Use `grep -qi` (case-insensitive) for all pattern matching. On the directory check side, also use case-insensitive matching (`specs/` = `Specs/` = `SPECS/`).

---

### BYPASS 2.3: Directory Path Evasion

**The bypass:** The agent creates the file in a subdirectory of the governed directory:
- `Specs/drafts/MyProject_PVD_v1.md`
- `Specs/v2/MyProject_PVD_v1.md`
- `Testing/unit/MyProject_Testing_Plans.md`

Or uses a sibling directory with a similar name:
- `specs/MyProject_PVD_v1.md` (lowercase on case-sensitive systems)
- `Specifications/MyProject_PVD_v1.md`
- `Spec/MyProject_PVD_v1.md`

**Why it works:** If the directory check uses exact prefix matching (`Specs/`), subdirectories might match but alternate names won't. If it uses `grep -q "Specs/"`, then `Specifications/Specs/` would falsely match but `Spec/` wouldn't. The behavior depends on the exact implementation.

**Severity:** MEDIUM. Subdirectories of governed directories should probably be governed too. Alternative directory names are less likely to cause confusion since other tools (spec-gate, trace-check) also look in specific directories.

**Suggested fix:** Use recursive directory matching: any file under `Specs/**`, `Testing/**`, `WorkOrders/**`, `Sessions/**`. Also normalize paths before checking.

---

### BYPASS 2.4: Path Traversal / Symlink

**The bypass:** The agent:
1. Creates a symlink: `ln -s ../Specs WorkOrders/specs_link`
2. Writes to `WorkOrders/specs_link/MyProject_PVD_v1.md`

Or uses path traversal:
- Writes to a path like `Notes/../Specs/MyProject_PVD_v1.md`
- The raw path doesn't start with `Specs/` but resolves to it

**Why it works:** If the hook does simple string matching on the path without canonicalizing it, traversal sequences like `../` or symlinks can route a file to a governed directory without matching the directory pattern.

**Severity:** MEDIUM. The `parse_hook_input.py` script normalizes backslashes to forward slashes but doesn't resolve `..` or symlinks.

**Suggested fix:** Canonicalize the file path (resolve `..`, `.`, and symlinks) before pattern matching. In the Python helper: use `os.path.realpath()` or `pathlib.Path.resolve()`.

---

### BYPASS 2.5: Unicode / Homoglyph Evasion

**The bypass:** The agent uses Unicode characters that look identical to ASCII:
- `Specs/MyProject_PVD_v1.md` where the `S` in `Specs` is actually Cyrillic `С` (U+0421)
- `Specs/MyProject_PVD_v1.md` where the `/` is a Unicode fraction slash
- Invisible characters in the filename: `Specs/MyProject_\u200BPVD_v1.md` (zero-width space)

**Why it works:** The hook uses ASCII string matching. Unicode homoglyphs pass through undetected. On NTFS/Windows, some Unicode characters are valid in filenames.

**Severity:** LOW. This is exotic and unlikely from an AI agent, but technically possible. The resulting files would be hard to work with downstream, which reduces practical impact.

**Suggested fix:** Normalize paths to ASCII before pattern matching, or reject any path containing non-ASCII characters in governed directories.

---

### BYPASS 2.6: Filename Containing Governed Pattern in Non-Governed Directory

**The bypass:** The agent creates `Notes/MyProject_PVD_v1.md` -- the filename matches the spec pattern, but the directory (`Notes/`) is not governed.

**Why it works:** The guard checks BOTH directory AND filename. If a governed pattern appears in an ungoverned directory, the guard allows it. The spec then exists outside the governed directory system.

**Severity:** MEDIUM. The spec exists but in the wrong location. Other tools (spec-gate) look in specific directories so they won't find it. But the agent could reference it manually.

**Suggested fix:** This may actually be desired behavior (allowing notes/drafts about specs in ungoverned directories). If not, extend the filename pattern check to all directories.

---

## CATEGORY 3: MARKER FORGERY BYPASSES

### BYPASS 3.1: Trivial Marker Injection

**The bypass:** The agent simply includes the string `<!-- TEMPLATE_SOURCE: TEMPLATE_PVD.md -->` in its content without actually using the template. The content can be completely freeform with no template structure whatsoever.

**Why it works:** The guard only checks for the PRESENCE of the marker string. It does not validate that the file's structure matches the template, that template sections are preserved, or that the template was actually read/used. The marker is a trivially forgeable string.

**Severity:** CRITICAL. This is the fundamental weakness of a marker-based system. Any agent that knows the marker format (which is documented in error messages the hook itself outputs) can forge it. The guard gives away the exact format in its block message: "which template to use."

**Severity note:** Made worse by the fact that when the guard BLOCKS a write, it tells the agent the exact template filename. A naive agent that gets blocked once now knows exactly what marker to forge on the second attempt.

**Suggested fix:** Multiple layers: (A) Check for structural compliance -- verify that required template sections exist in the content (e.g., the PVD template has `## Product Overview`, `## Features`, etc. -- check for their presence). (B) Use a cryptographic hash: the template marker includes a hash of the template content plus a salt, making forgery non-trivial. (C) Use a PostToolUse hook that compares the written file's structure against the template schema.

---

### BYPASS 3.2: Marker with Wrong Template Name

**The bypass:** The agent writes a Decision Record but includes `<!-- TEMPLATE_SOURCE: TEMPLATE_PVD.md -->` -- the marker is present but references the wrong template.

**Why it works:** If the guard only checks for the presence of `TEMPLATE_SOURCE:` without cross-referencing the template name against the file type, any valid-looking marker passes regardless of whether it's the correct template for the document type.

**Severity:** HIGH. The agent gets the structure of template A while being forced to use template B's marker. Result: structurally wrong documents that pass the guard.

**Suggested fix:** Cross-reference the template name in the marker against the filename pattern. If the file contains `PVD` in its name, the marker must reference `TEMPLATE_PVD.md`. Map each filename pattern to its required template.

---

### BYPASS 3.3: Marker Embedded in Comment/Hidden Section

**The bypass:** The agent writes:
```markdown
<!-- TEMPLATE_SOURCE: TEMPLATE_PVD.md -->
<!-- Everything above is just to satisfy the guard. Real content below: -->

# My Completely Custom PVD That Follows No Template
...
```

**Why it works:** The marker's presence is sufficient. The guard doesn't check that template-mandated sections actually exist below the marker.

**Severity:** HIGH (same root cause as 3.1, but specifically illustrating the "marker as header, ignore everything else" pattern).

**Suggested fix:** Same as 3.1 -- structural validation, not just marker presence.

---

## CATEGORY 4: TEMPORAL / RACE CONDITION BYPASSES

### BYPASS 4.1: Create-Then-Edit (Two-Step Bypass)

**The bypass:**
1. Agent uses `Write` to create the file WITH the template marker and proper template content. Guard passes.
2. Agent immediately uses `Edit` to replace the entire content with non-template content. The guard sees this as an "existing file being edited" and allows it.

**Why it works:** The guard explicitly exempts existing files being edited. After step 1, the file exists. Step 2 is a legitimate edit to an existing file, so the guard doesn't check for the template marker in the new content.

**Severity:** CRITICAL. This is a two-step bypass that uses only sanctioned operations. The agent follows the rules in step 1 then immediately violates them in step 2.

**Suggested fix:** For Edit operations on governed files, check if the edit removes the template marker. Or: check that governed files ALWAYS contain the template marker, not just at creation time. A PostToolUse hook could validate that governed files still contain their markers after every edit.

---

### BYPASS 4.2: Write Empty File Then Edit

**The bypass:**
1. Agent uses `Write` to create a file with minimal content: just the marker line `<!-- TEMPLATE_SOURCE: TEMPLATE_PVD.md -->`. Guard passes.
2. Agent uses `Edit` to add all the real content below the marker -- content that doesn't follow the template structure.

**Why it works:** The Write passes because the marker is present. The subsequent Edit passes because the file already exists. No structural validation occurs at any point.

**Severity:** HIGH. Slightly less severe than 4.1 because the marker technically persists in the file, but the content still doesn't follow the template.

**Suggested fix:** Structural validation at write time -- check for required sections, not just the marker.

---

### BYPASS 4.3: Overwrite Existing Governed File

**The bypass:** The agent uses `Write` on an existing governed file (e.g., `Specs/gap_tracker.md` or `Specs/Work_Ledger.md` which already exist in the template). Since these files already exist, the "existing files being edited" exception applies.

**Why it works:** The guard exempts existing files. The agent can completely rewrite these files with `Write` without any template check, because the files already exist on disk.

**Severity:** MEDIUM. This doesn't create NEW ungoverned files, but it allows existing governed files to be overwritten with arbitrary content. The `protect-frozen-files.sh` hook partially addresses this for frozen files, but unfrozen files in governed directories are unprotected.

**Suggested fix:** For `Write` operations (full file replacement, not Edit) on governed files, require the template marker even for existing files. Only exempt `Edit` operations.

---

## CATEGORY 5: HOOK INFRASTRUCTURE BYPASSES

### BYPASS 5.1: Subagent Tool Calls

**The bypass:** If the agent spawns a subagent (via Task tool or similar), and the subagent makes Write calls, do the PreToolUse hooks fire?

**Why it works:** Hook behavior for subagents is implementation-dependent. If hooks only fire in the main agent's context, subagents operate without guard enforcement. The user's environment description mentions a subagents directory: `C:\Users\Nathan\.claude\projects\...\subagents`.

**Severity:** HIGH if hooks don't fire for subagents. NONE if they do. This needs empirical testing.

**Suggested fix:** Verify that hooks fire for all tool calls regardless of agent context. If they don't, add explicit subagent hook registration.

---

### BYPASS 5.2: Modifying the Hook Itself

**The bypass:** The agent uses `Edit` to modify `.claude/hooks/template-guard.sh` to neuter it (e.g., add `exit 0` at the top), or modifies `.claude/settings.json` to remove the hook registration.

**Why it works:** The hook files themselves are not in governed directories (they're in `.claude/hooks/`). The `protect-frozen-files.sh` hook only protects files listed in its `FROZEN_PATTERNS` array, which currently is empty. There's no protection on hook files or settings.json.

**Severity:** CRITICAL. If the agent can modify the guard, it can disable all enforcement. This is the "who watches the watchmen?" problem.

**Suggested fix:** Add `.claude/hooks/*` and `.claude/settings.json` and `.claude/rules/*` to the frozen files list. Or add a dedicated hook that blocks modifications to the `.claude/` directory tree.

---

### BYPASS 5.3: Modifying parse_hook_input.py

**The bypass:** The agent edits `.claude/hooks/parse_hook_input.py` to always return an empty string, or to strip governed directory prefixes from paths.

**Why it works:** All hooks depend on `parse_hook_input.py` to extract the file path. If it's compromised, all hooks are blind.

**Severity:** CRITICAL. Single point of failure for the entire hook system.

**Suggested fix:** Same as 5.2 -- protect the `.claude/` directory tree from modification. Or inline the parsing logic in each hook to eliminate the shared dependency.

---

### BYPASS 5.4: Environment Variable Manipulation

**The bypass:** The agent uses Bash to modify `CLAUDE_PROJECT_DIR` or other environment variables that hooks depend on, causing path resolution to fail or point to wrong directories.

**Why it works:** Hooks use `$CLAUDE_PROJECT_DIR` for path resolution. If the agent can influence this variable (e.g., through Bash's `export` command), the hook might check the wrong directory.

**Severity:** LOW. Shell state doesn't persist between Bash calls (per the environment notes), so `export` in one call won't affect hook execution in another. But if the hook runs in the same shell context as the Bash command, this could work.

**Suggested fix:** Hooks should resolve their own paths independently rather than trusting environment variables. Use the hook's own `$0` path to derive the project root.

---

### BYPASS 5.5: Hook Timeout Exploitation

**The bypass:** The agent constructs a Write operation with extremely large content (megabytes of text), causing the template guard hook to exceed its timeout while processing the content check.

**Why it works:** The settings show `"timeout": 5` for the existing hooks and `"timeout": 10` for spec-gate. If the template guard uses `grep` on the content piped through stdin, extremely large content could cause it to exceed the timeout. When a hook times out, the default behavior may be to ALLOW (fail-open).

**Severity:** MEDIUM. Depends on the timeout behavior (fail-open vs. fail-closed). If the hook infrastructure treats timeouts as errors and blocks, this doesn't work.

**Suggested fix:** Ensure hooks fail CLOSED on timeout (block rather than allow). Also, limit content inspection to the first few kilobytes (template markers should be at the top of the file).

---

### BYPASS 5.6: Corrupted/Invalid JSON Input

**The bypass:** If the agent somehow causes the hook input JSON to be malformed (e.g., by including special characters in the file path or content), `parse_hook_input.py` will catch the exception and print an empty string (line 25: `except Exception: print("")`). An empty file path causes all hooks to `exit 0` (allow).

**Why it works:** The error handling in `parse_hook_input.py` is a silent fail-open. Any parsing error results in an empty string, which every hook treats as "nothing to check, allow."

**Severity:** MEDIUM. The agent doesn't directly control the JSON serialization of tool inputs -- that's done by the Claude Code infrastructure. But edge cases in content (null bytes, very deep nesting) could theoretically cause parse failures.

**Suggested fix:** Change `parse_hook_input.py` to exit with a non-zero status on parse failure, and have hooks treat non-zero exits from the parser as "block." Fail closed, not open.

---

## CATEGORY 6: LOGICAL / SEMANTIC BYPASSES

### BYPASS 6.1: The "Existing File" Loophole for Templates Themselves

**The bypass:** The guard exempts `TEMPLATE_*` files themselves. The agent edits `TEMPLATE_PVD.md` to contain project-specific content, effectively turning the template into the actual spec document.

**Why it works:** Template files are explicitly exempted so they can be maintained. But nothing prevents the agent from repurposing a template file as the actual spec.

**Severity:** MEDIUM. This defeats the purpose of having templates (the template is now the spec), but it's a weird edge case that a confused agent might fall into rather than a deliberate bypass.

**Suggested fix:** Template files should be frozen (added to `protect-frozen-files.sh`). Changes to templates should require explicit human approval.

---

### BYPASS 6.2: Session Files -- Naming Pattern Gap

**The bypass:** The guard checks for `session_` in filenames. The existing session template is `SESSION_TEMPLATE.md` in the `Sessions/` directory. If the agent creates `Sessions/2026-03-01_meeting_notes.md` (no `session_` substring), it bypasses the pattern.

**Why it works:** The naming convention says sessions are `YYYY-MM-DD_session_{topic}.md`, but the pattern check is substring-based. Files not matching the pattern are ungoverned.

**Severity:** MEDIUM. The agent can create files in the `Sessions/` directory that don't trigger the guard by simply not using the word `session` in the filename.

**Suggested fix:** Govern the entire `Sessions/` directory, not just files matching the `session_` pattern. Any new `.md` file in `Sessions/` should require the template marker.

---

### BYPASS 6.3: Work_Ledger and gap_tracker Are Auto-Generated

**The bypass:** The `Work_Ledger.md` and `gap_tracker.md` are special files that already exist in the template and may be auto-generated by `/trace-check`. If the template guard blocks the trace-check skill from updating these files (or if the skill generates them without the template marker), the system breaks.

**Why it works:** These files exist at the intersection of "governed file" and "programmatically generated file." The guard needs to allow programmatic updates but also enforce template compliance. If `gap_tracker.md` already exists, the "existing file" exception handles it. But if the file is deleted and recreated by trace-check, the guard might block it.

**Severity:** LOW-MEDIUM. This is more of a "friendly fire" / self-sabotage risk than an adversarial bypass.

**Suggested fix:** Ensure the trace-check skill includes the appropriate template markers when regenerating these files. Or explicitly whitelist the trace-check script's output.

---

### BYPASS 6.4: WorkOrders/_Archive/ Subdirectory

**The bypass:** The agent creates `WorkOrders/_Archive/WO-1.2.3-A.md` without a template marker. If the guard governs `WorkOrders/` but not its subdirectories, or if `_Archive/` is explicitly excluded (as archive directories sometimes are), this works.

**Why it works:** The `_Archive/` subdirectory is a standard part of the project structure used for superseded documents. If the guard treats it as part of `WorkOrders/`, old/archived files should be exempt. But if the agent creates "new" files directly in `_Archive/`, it bypasses the guard while placing files in a location that tools still scan.

**Severity:** LOW. Archived files are generally not active, but a determined agent could store active work orders in the archive to avoid template enforcement.

**Suggested fix:** Apply the same governance to `_Archive/` subdirectories, or at minimum check that files in `_Archive/` were moved there rather than created there (check git history or modification times).

---

## CATEGORY 7: CROSS-PROJECT / ENVIRONMENT BYPASSES

### BYPASS 7.1: Writing to _shared/ Junction

**The bypass:** The `_shared/` directory is a Windows directory junction to `_SharedCore/`. The agent writes to `_shared/SomeSpec_PVD_v1.md`. If the guard checks the path string `_shared/` and doesn't recognize it as a governed directory (it's not `Specs/`, `Testing/`, `WorkOrders/`, or `Sessions/`), the file passes through ungoverned.

**Why it works:** Directory junctions on Windows make a path look local but actually resolve to a different location. The file ends up in `_SharedCore/` which is a cross-project directory outside the project tree.

**Severity:** MEDIUM. The file ends up in a location that multiple projects read from, potentially contaminating the shared spec layer.

**Suggested fix:** Add `_shared/` and `_SharedCore/` to the governed directory list. Resolve junction targets before path checking.

---

### BYPASS 7.2: Writing to Project Root (CLAUDE.md)

**The bypass:** The guard governs "project root" files. The agent creates a new file in the project root with a spec-like name (e.g., `./MyProject_PVD_v1.md`) outside the `Specs/` directory.

**Why it works:** If "project root" governance is limited to specific files (like `CLAUDE.md`), any other file created in the root is ungoverned. If it's based on the filename pattern, the file would be caught -- but only if the root directory is in the governed list.

**Severity:** LOW-MEDIUM. Depends on the exact implementation of "project root" governance.

**Suggested fix:** Clarify the "project root" governance: either govern ALL `.md` files at the root, or enumerate the specific root files that are protected.

---

### BYPASS 7.3: Creating a settings.local.json

**The bypass:** The agent creates `.claude/settings.local.json` (from the example file) but modifies it to override hook settings, removing or altering the template guard hook registration.

**Why it works:** The example file shows that `settings.local.json` "MERGES with settings.json." If local settings can override hook registrations (e.g., by providing an empty hooks array), the template guard can be disabled per-machine.

**Severity:** HIGH. The merge behavior of local settings could neutralize the entire hook system.

**Suggested fix:** Hooks should be non-overridable -- `settings.local.json` should only be able to ADD permissions, not modify hook registrations. Or: protect `.claude/settings.local.json` creation through a hook.

---

## CATEGORY 8: TIMING AND ORDERING BYPASSES

### BYPASS 8.1: Race Between Hooks

**The bypass:** If multiple PreToolUse hooks fire sequentially (as shown in settings.json: `protect-frozen-files.sh` then `spec-gate.sh`), and the template-guard is added as a third hook, the agent might exploit ordering. For example, if a hook earlier in the chain modifies the input or sets a state that the template guard doesn't expect.

**Why it works:** Hooks fire in sequence. If an earlier hook outputs JSON with `permissionDecision: "allow"`, does that short-circuit later hooks? The behavior is implementation-dependent.

**Severity:** LOW. In most hook systems, all hooks must pass. But if any hook can emit an explicit "allow" that overrides subsequent hooks, earlier hooks become bypass vectors.

**Suggested fix:** Ensure the hook infrastructure uses a "deny wins" model -- any hook returning deny/block takes precedence over all allows.

---

### BYPASS 8.2: Writing During Session Start/Resume Hooks

**The bypass:** The `session-start.sh` and `session-resume.sh` hooks fire on SessionStart, not PreToolUse. If these hooks use `cat` or other commands that create files, or if an agent can influence the session hooks to create governed files, those writes bypass PreToolUse guards entirely.

**Why it works:** SessionStart hooks fire in a different lifecycle stage than PreToolUse. File writes performed by session hooks are shell operations, not tool calls, so PreToolUse never fires.

**Severity:** LOW. The existing session hooks are read-only (they output context to stdout). But if a future session hook writes files, this becomes a vector.

**Suggested fix:** Ensure session hooks are audited for file-write operations. Or add a PostToolUse hook that validates governed directory state after any lifecycle event.

---

## SUMMARY TABLE

| # | Bypass | Severity | Category |
|---|--------|----------|----------|
| 1.1 | Edit tool creates new files without content inspection | CRITICAL | Tool-level |
| 1.2 | Bash tool direct file creation (echo, cat, python, etc.) | CRITICAL | Tool-level |
| 1.3 | Write to /tmp then cp/mv to governed directory | CRITICAL | Tool-level |
| 1.4 | Git checkout/restore/show to create governed files | HIGH | Tool-level |
| 1.5 | NotebookEdit in governed directories | MEDIUM | Tool-level |
| 1.6 | MCP tools with file-write capabilities | LOW | Tool-level |
| 2.1 | Filename synonym/abbreviation to evade pattern | HIGH | Pattern evasion |
| 2.2 | Case sensitivity mismatch (Windows NTFS) | HIGH | Pattern evasion |
| 2.3 | Subdirectory or alternate directory names | MEDIUM | Pattern evasion |
| 2.4 | Path traversal (`../`) and symlinks | MEDIUM | Pattern evasion |
| 2.5 | Unicode homoglyphs in filenames | LOW | Pattern evasion |
| 2.6 | Governed pattern in non-governed directory | MEDIUM | Pattern evasion |
| 3.1 | Trivial marker string injection (forgery) | CRITICAL | Marker forgery |
| 3.2 | Marker referencing wrong template | HIGH | Marker forgery |
| 3.3 | Marker present but content ignores template structure | HIGH | Marker forgery |
| 4.1 | Create with marker, then Edit to remove all template content | CRITICAL | Temporal |
| 4.2 | Write minimal marker-only file, then Edit to add arbitrary content | HIGH | Temporal |
| 4.3 | Overwrite existing governed file via Write (existing file exception) | MEDIUM | Temporal |
| 5.1 | Subagent tool calls may not trigger hooks | HIGH | Infrastructure |
| 5.2 | Agent modifies the hook script itself | CRITICAL | Infrastructure |
| 5.3 | Agent modifies parse_hook_input.py | CRITICAL | Infrastructure |
| 5.4 | Environment variable manipulation | LOW | Infrastructure |
| 5.5 | Hook timeout with large content (fail-open) | MEDIUM | Infrastructure |
| 5.6 | Corrupted JSON input causes silent fail-open | MEDIUM | Infrastructure |
| 6.1 | Repurposing TEMPLATE_* files as actual specs | MEDIUM | Logical |
| 6.2 | Session files without `session_` in name | MEDIUM | Logical |
| 6.3 | Auto-generated files (Work_Ledger, gap_tracker) conflict | LOW-MEDIUM | Logical |
| 6.4 | Direct creation in _Archive/ subdirectories | LOW | Logical |
| 7.1 | Writing through _shared/ directory junction | MEDIUM | Cross-project |
| 7.2 | Spec files created in project root | LOW-MEDIUM | Cross-project |
| 7.3 | Creating settings.local.json to override hooks | HIGH | Cross-project |
| 8.1 | Hook ordering / "allow" short-circuit | LOW | Timing |
| 8.2 | File writes during SessionStart hooks | LOW | Timing |

---

## TOP 5 RECOMMENDATIONS (Priority Order)

1. **Protect the guard infrastructure itself.** Add `.claude/hooks/*`, `.claude/settings.json`, `.claude/settings.local.json`, `.claude/rules/*`, and `parse_hook_input.py` to the frozen files list. Without this, every other defense can be trivially disabled (bypasses 5.2, 5.3, 7.3).

2. **Block file creation via Bash in governed directories.** Add a PostToolUse hook (or enhance `block-dangerous.sh`) that detects when Bash commands create or move files into governed directories. This closes bypasses 1.2, 1.3, and 1.4. A practical approach: after every Bash command, run a quick scan of governed directories for files modified within the last 5 seconds that lack the template marker.

3. **Handle the Edit tool's blind spot.** Add a PreToolUse hook for Edit that blocks creating NEW files in governed directories (when the target file doesn't already exist). This closes bypass 1.1. For existing files, add a PostToolUse check that the template marker was not removed (closes 4.1).

4. **Add structural validation, not just marker presence.** The marker is trivially forgeable (3.1, 3.2, 3.3). At minimum, validate that the file contains the required section headers from the referenced template. For example, a PVD must contain `## Product Overview`, `## Features`, `## Success Metrics`, etc. This transforms the guard from a "did you paste the magic string?" check into a "does this actually follow the template?" check.

5. **Govern directories, not just filenames.** Instead of matching `PVD`, `PRD`, `Engineering_Spec`, etc. as substrings, govern ALL new `.md` file creation in `Specs/`, `Testing/`, `WorkOrders/`, and `Sessions/`. Any new `.md` file in these directories requires a template marker. This closes the entire family of filename evasion bypasses (2.1, 2.2, 6.2).

---

## DESIGN PHILOSOPHY NOTE

The fundamental tension in this system is that it's a **soft guard in a cooperative environment**. The agent has full access to Bash, Edit, Python, and file system operations. Any PreToolUse hook on a single tool (Write) is inherently incomplete because there are many other paths to file creation. The guard system needs to evolve from "check before Write" to "validate the filesystem state after any mutation" -- a PostToolUse or periodic audit approach. The marker-based system should be treated as a **speed bump for well-intentioned agents**, not a **security boundary against adversarial ones**. For true enforcement, consider a filesystem-level watcher or a pre-commit git hook that validates template compliance before any commit is accepted.

