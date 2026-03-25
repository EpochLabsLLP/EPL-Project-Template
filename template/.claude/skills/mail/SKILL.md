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
5. **Log each message to the mail ledger** — for each message, append a `RECEIVED` entry to `.claude/mail-ledger.md` if one doesn't already exist for that filename (dedupe by grepping for `file:{filename}`)
6. For each message, summarize the content and action needed
7. Ask Nathan which messages to act on (if interactive). If running autonomously (CLI heartbeat / `/work` flow), act on urgent messages immediately and process normal messages per the work pickup sequence.
8. After acting on a message:
   - **Log the action to the mail ledger** — append an `ACTED` entry with a note describing what was done, OR a `NO-ACTION` entry with `status:fyi` if the message was informational only
   - Move the message to `.claude/inbox/_processed/`

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
   `YYYY-MM-DD_HHMMSS_{from_abbreviation}-{env}_{subject_slug}.md`
   - `from_abbreviation`: This project's abbreviation (from registry, or ask Nathan). **MUST be lowercase.**
   - `env`: `cli` if running in `--print` mode (CLI heartbeat), `vsc` if running in VS Code. Detect by checking if the session is interactive.
   - `subject_slug`: **Lowercase**, hyphens only (no underscores), max 40 chars
   - **ALL components MUST be lowercase.** Uppercase in filenames causes Syncthing case collisions across Mac/Windows.
   - Example: `2026-03-25_103000_pm-cli_phase-n-start-signal.md`
   - Example: `2026-03-25_143000_epoe-vsc_status-beacon.md`
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

4. **Log the send to the mail ledger** — append a `SENT` entry to this project's `.claude/mail-ledger.md`
5. Confirm to Nathan: "Mail sent to {project} — {subject}"

### Step 4 — Reply Threading (Optional)

If this message is a reply to a received message:
- Add `in-reply-to: {original filename}` to the frontmatter
- Reference the original message in the Context section

## Check Ledger (`/mail --ledger`)

If `$ARGUMENTS` is `--ledger`:

1. Read `.claude/mail-ledger.md` (last 20 lines)
2. Count entries by status: `grep -c "status:pending"`, `grep -c "status:done"`, `grep -c "status:fyi"`
3. Display summary: `Pending: N | Done: N | FYI: N`
4. Show the last 20 entries
5. If any entries have `status:pending`, list them prominently — these are messages that were received but not yet acted on

## Mail Ledger Format

The mail ledger at `.claude/mail-ledger.md` is an append-only, grep-scannable log of all mail events. It is `.gitignored` (machine-local). Each entry is one line:

```
YYYY-MM-DDTHH:MM:SS | ACTION | from:PROJECT | subject:SLUG | file:FILENAME | by:INSTANCE_ID | status:STATUS | note:TEXT
```

**Fields:**
- **ACTION**: `RECEIVED`, `ACTED`, `NO-ACTION`, `SENT`, `REPLIED`
- **from:/to:**: The project the mail came from (for inbound) or went to (for SENT)
- **subject:**: The message subject slug (from frontmatter)
- **file:**: The message filename (key for deduplication and cross-reference)
- **by:**: The instance ID that performed this action (from `.claude/instance-id`)
- **status:**: `pending` (received, not yet acted on), `done` (action complete), `fyi` (informational, no action needed)
- **note:**: Brief description of what was done (for ACTED/NO-ACTION/REPLIED entries)

**Examples:**
```
2026-03-24T10:30:00 | RECEIVED  | from:Epoch-PM | subject:phase-n-start | file:2026-03-24_pm_phase-n.md | by:epoe-cli-20260324-1030 | status:pending
2026-03-24T10:35:00 | ACTED     | from:Epoch-PM | subject:phase-n-start | file:2026-03-24_pm_phase-n.md | by:epoe-cli-20260324-1030 | status:done | note:Updated mission-lock, began Phase N
2026-03-24T10:36:00 | SENT      | to:Epoch-PM   | subject:status-beacon | file:2026-03-24_epoe_beacon.md | by:epoe-cli-20260324-1030 | status:done
2026-03-24T14:00:00 | NO-ACTION | from:Epoch-PM | subject:fyi-metrics   | file:2026-03-24_pm_metrics.md | by:epoe-vsc-20260324-1400 | status:fyi | note:Informational only
```

**Reading the ledger:**
- `grep "status:pending"` — find all unresolved messages
- `grep "from:ATLAS"` — find all ATLAS correspondence
- `grep "ACTED"` — find all messages that were acted on (with notes)
- `grep "by:epoe-cli"` — find all actions by CLI heartbeat instances

**Rotation:** When the ledger exceeds 500 lines, truncate to the last 250 lines. Check line count before appending and rotate if needed.

**How to write a ledger entry:**
Read the instance ID from `.claude/instance-id` (or use "unknown" if missing). Append one line using the format above. The `note:` field is optional for RECEIVED and SENT entries but required for ACTED and NO-ACTION entries.

## Inbox Conventions

- Messages live in `.claude/inbox/` until processed
- Processed messages move to `.claude/inbox/_processed/` (permanent archive)
- Never delete messages — the `_processed/` folder is the audit trail
- Urgent messages should be addressed before continuing other work
- The session-start hook automatically surfaces unread messages
- **The mail ledger tracks what happened** — every receive, action, and send is logged so the next instance knows what was already handled
