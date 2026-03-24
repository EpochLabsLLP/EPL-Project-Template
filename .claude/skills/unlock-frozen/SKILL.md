---
name: unlock-frozen
description: Create a formal edit authorization for a frozen spec file. Requires written rationale justifying the edit — what will change, why, and what authorized it. Creates a one-shot bypass consumed after one write. All authorizations are permanently logged for audit.
argument-hint: <file-path>
user-invocable: true
---

# unlock-frozen

Creates a formal, audited authorization to edit a frozen spec file exactly once.

## When to Use

- When you need to update a tracking section in a frozen spec (checklist, status field, progress table)
- When an approved gap item requires modifying an existing frozen document
- When Nathan has explicitly approved an edit to a frozen spec in the current session
- **NOT** for rewriting or restructuring a frozen spec — that requires full change control (see `change-control.md`)

## How to Invoke

/unlock-frozen <file-path>

## Execution

When invoked with a file path ($ARGUMENTS):

1. **Agent MUST state the following before the bypass is granted:**

   - **Scope** — Which specific section or field will be modified.
     Example: "Updating the acceptance criteria checklist in Section 4"
   - **Rationale** — Why this edit is necessary.
     Example: "Gap Tracker GT-4 approved by Nathan; the checklist needs a new item for auth token refresh"
   - **Authorization** — What approved this edit.
     Example: "GT-4", "DR-003", "Nathan approved in session on 2026-03-08", "WO-2.1.3-A requires status update"

   If the agent cannot provide all three, STOP. Do not proceed. The edit is not authorized.

2. **Validate preconditions:**

   a. **File exists** — Resolve `$ARGUMENTS` to an absolute path. Check the file exists.
      - If not found → REJECT: "File not found: $ARGUMENTS"

   b. **File is frozen** — Read first 15 lines and check for FROZEN marker (case-insensitive).
      - If not frozen → REJECT: "File is not frozen — no unlock needed. You can edit it directly."

   c. **No active bypass** — Check if `.claude/frozen-bypass` exists.
      - If it exists → REJECT: "A frozen-file bypass is already active. Complete or cancel that edit before requesting another."

3. **Write the bypass marker** — `.claude/frozen-bypass`:

   ```
   FILE=<relative-path-from-project-root>
   SCOPE=<scope from step 1>
   AUTHORIZATION=<authorization reference from step 1>
   TIMESTAMP=<ISO-8601 datetime>
   ```

4. **Append to the audit log** — `.claude/frozen-edit-log.md`:

   If the file doesn't exist, create it with header `# Frozen Edit Authorization Log` and a blank line.

   Append:
   ```markdown
   ### <ISO-8601 datetime>
   - **File:** <relative-path>
   - **Scope:** <scope>
   - **Rationale:** <rationale>
   - **Authorization:** <authorization reference>
   - **Status:** GRANTED
   ```

5. **Confirm:**

   > Edit authorization granted for one edit to `<file>`.
   > Make your edit now — the bypass will be consumed after the next write to this file.

## Important

- **One at a time.** Only one bypass can be active. Complete the edit before requesting another.
- **One shot.** The bypass is consumed after a single write. If you need multiple edits to the same frozen file, invoke `/unlock-frozen` again for each edit.
- **Scope discipline.** Only edit what you declared in the Scope. Do not make unrelated changes to the frozen file.
- **Not for restructuring.** If the frozen spec needs significant revision (not just a tracking update), follow the full change control protocol: escalate to Nathan, create a new version, archive the old one, and file a Decision Record.
