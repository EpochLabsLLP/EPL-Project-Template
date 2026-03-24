---
name: mail
description: Send a message to another project's agent. Use when you discover something relevant to another project (bugs, decisions, context, requests), when Nathan asks you to notify another project, or when cross-project coordination is needed. Also use to check this project's inbox with `/mail --check`.
user-invocable: true
argument-hint: <project-name> [subject] | --check
---

# Agent Mail

Send structured messages to other projects' agents, or check this project's inbox.

## Check Inbox (`/mail --check` or no arguments)

If `$ARGUMENTS` is `--check` or empty:

1. Scan `$CLAUDE_PROJECT_DIR/.claude/inbox/` for `*.md` files (exclude `_processed/`)
2. If no messages, report "Inbox empty." and stop
3. Display each message with its frontmatter (priority, from, type, date, subject)
4. Sort by priority: **urgent** first, then **normal**, then **fyi**
5. For each message, summarize the content and action needed
6. Ask Nathan which messages to act on
7. After acting on a message, move it to `.claude/inbox/_processed/`

## Send Mail

When `$ARGUMENTS` contains a project name:

### Step 1 — Resolve Target

1. Read the project registry at `_shared/project_registry.json`
   - If `_shared/` doesn't exist, try `$CLAUDE_PROJECT_DIR/_shared/project_registry.json`
   - If registry is missing, ask Nathan for the target project's filesystem path
2. Find the target project by name (case-insensitive partial match is OK)
3. Determine the target's full path:
   - Read `path_roots` from registry to get the OS-appropriate root
   - On Windows (paths contain `\` or `C:`): use `path_roots.windows`
   - On macOS/Linux: use `path_roots.mac` (expand `~`)
   - Append the project's `path` to the root
4. Verify the target path exists on disk. If not, warn Nathan and stop.

### Step 2 — Compose Message

Gather the following (infer from context when possible, ask Nathan if unclear):

- **priority**: `urgent` | `normal` | `fyi`
  - `urgent`: Requires action before the receiving agent continues other work
  - `normal`: Should be addressed when convenient
  - `fyi`: Informational — no action required
- **type**: `request` | `alert` | `info` | `question`
  - `request`: Asking the receiving project to do something
  - `alert`: Something is broken or needs immediate attention
  - `info`: Sharing context or a decision that affects the receiving project
  - `question`: Need input or an answer back
- **subject**: Brief one-line summary
- **body**: Write three sections:
  - `## Context` — What you discovered or were working on that prompted this message
  - `## Action Needed` — What the receiving agent should do (or "None — FYI only" for info type)
  - `## References` — File paths, commit hashes, error output, or other concrete details

### Step 3 — Deposit

1. Create the target inbox directory if it doesn't exist:
   `{target_project_path}/.claude/inbox/`
2. Generate the filename:
   `YYYY-MM-DD_HHMMSS_{from_abbreviation}_{subject_slug}.md`
   - `from_abbreviation`: This project's abbreviation (from registry, or ask Nathan)
   - `subject_slug`: Lowercase, hyphens, max 40 chars
3. Write the message file:

```markdown
---
from: {this project name}
to: {target project name}
priority: {urgent|normal|fyi}
type: {request|alert|info|question}
date: {ISO 8601 timestamp}
subject: {one-line subject}
---

## Context
{context}

## Action Needed
{action needed}

## References
{references}
```

4. Confirm to Nathan: "Mail sent to {project} — {subject}"

### Step 4 — Reply Threading (Optional)

If this message is a reply to a received message:
- Add `in-reply-to: {original filename}` to the frontmatter
- Reference the original message in the Context section

## Inbox Conventions

- Messages live in `.claude/inbox/` until processed
- Processed messages move to `.claude/inbox/_processed/` (permanent archive)
- Never delete messages — the `_processed/` folder is the audit trail
- Urgent messages should be addressed before continuing other work
- The session-start hook automatically surfaces unread messages
