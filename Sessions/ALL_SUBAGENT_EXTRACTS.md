# 01_hooks_research (agent-a136651be338bd214.jsonl)

## Message 1

Excellent. Now let me compile a comprehensive document for you. Let me create a summary document with all the critical information:

Based on my research of the official Claude Code documentation, here is the comprehensive documentation on Claude Code hooks, the skills system, and related topics:

---

## COMPREHENSIVE CLAUDE CODE DOCUMENTATION

### 1. HOOKS SYSTEM - COMPLETE REFERENCE

#### 1.1 Hook Lifecycle & Events

Hooks fire at specific points during a Claude Code session. There are 18 hook event types:

| Event                | When it fires                                                                                               | Can block? |
| :------------------- | :---------------------------------------------------------------------------------------------------------- | :--------- |
| `SessionStart`       | When a session begins or resumes                                                                            | No         |
| `UserPromptSubmit`   | When you submit a prompt, before Claude processes it                                                        | Yes        |
| `PreToolUse`         | Before a tool call executes                                                                                 | Yes        |
| `PermissionRequest`  | When a permission dialog appears                                                                            | Yes        |
| `PostToolUse`        | After a tool call succeeds                                                                                  | No         |
| `PostToolUseFailure` | After a tool call fails                                                                                     | No         |
| `Notification`       | When Claude Code sends a notification                                                                       | No         |
| `SubagentStart`      | When a subagent is spawned                                                                                  | No         |
| `SubagentStop`       | When a subagent finishes                                                                                    | Yes        |
| `Stop`               | When Claude finishes responding                                                                             | Yes        |
| `TeammateIdle`       | When an agent team teammate is about to go idle                                                             | Yes        |
| `TaskCompleted`      | When a task is being marked as completed                                                                    | Yes        |
| `ConfigChange`       | When a configuration file changes during a session                                                          | Yes        |
| `WorktreeCreate`     | When a worktree is being created via `--worktree` or `isolation: "worktree"`                               | Yes        |
| `WorktreeRemove`     | When a worktree is being removed                                                                            | No         |
| `PreCompact`         | Before context compaction                                                                                   | No         |
| `SessionEnd`         | When a session terminates                                                                                   | No         |

#### 1.2 PreToolUse Hook - Critical Detail for Your Use Case

**PreToolUse hooks fire BEFORE a tool executes** and can inspect and block the tool call. They support matchers on tool name.

##### PreToolUse Input Schema for Write Tool

When Claude is about to write a file, a PreToolUse hook receives this JSON on stdin:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"  // <-- THIS IS THE FULL FILE CONTENT
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

**Key insight**: `tool_input.content` contains the COMPLETE file content before it's written. Your hook can inspect this.

##### PreToolUse Input Schema for Edit Tool

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "old_string": "original text",
    "new_string": "replacement text",
    "replace_all": false
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

Note: Edit provides the replacement in progress, not the final file content.

##### PreToolUse Decision Control

PreToolUse hooks use `hookSpecificOutput` (NOT top-level `decision`):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow" | "deny" | "ask",
    "permissionDecisionReason": "Your reason here",
    "updatedInput": {
      "content": "modified content"  // <-- Can modify tool input before execution
    },
    "additionalContext": "Text added to Claude's context"
  }
}
```

Exit codes:
- **Exit 0**: Tool call proceeds (unless JSON says `"deny"`)
- **Exit 2**: Tool call blocked. Write reason to stderr.
- **Any other code**: Non-blocking error, tool proceeds

#### 1.3 PostToolUse Hook - After Tool Executes

PostToolUse fires AFTER a tool has already succeeded. Input includes both `tool_input` and `tool_response`:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "success": true
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

#### 1.4 Complete Hook Configuration Schema

Hooks are defined in settings JSON files at three scope levels:

**File Locations:**
- `~/.claude/settings.json` - Global (all projects)
- `.claude/settings.json` - Project scope (this project only)
- `.claude/settings.local.json` - Project local (not committed, gitignored)

**Full Hook Configuration Structure:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command|http|prompt|agent",
            "command": "path/to/script.sh",  // for type: command
            "url": "http://localhost:8080",  // for type: http
            "prompt": "Your prompt here",    // for type: prompt
            "timeout": 600,                  // seconds, optional
            "statusMessage": "Running...",   // optional spinner message
            "once": false,                   // only run once per session (skills only)
            "async": false,                  // run in background (command only)
            "headers": {                     // for type: http
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"],  // for type: http
            "model": "opus"                  // for type: prompt
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash|Edit|Write|Read|Glob|Grep|WebFetch|WebSearch|Agent|mcp__.*",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/my-hook.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Tool completed' >&2"
          }
        ]
      }
    ]
  },
  "disableAllHooks": false  // Set true to disable all hooks temporarily
}
```

#### 1.5 Hook Input/Output Details

**Common Input Fields** (all events receive these):

```json
{
  "session_id": "unique-session-id",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|dontAsk|bypassPermissions",
  "hook_event_name": "PreToolUse|PostToolUse|..."
}
```

**Hook Output via Exit Codes:**

```
Exit 0   → Action proceeds. For UserPromptSubmit/SessionStart, stdout is added as context
Exit 2   → Action blocked. Write reason to stderr
Other    → Non-blocking error. Stderr logged but not shown to Claude
```

**Hook Output via JSON** (exit 0 + stdout JSON):

```json
{
  "continue": true,                    // false = stop everything
  "stopReason": "Why we stopped",      // shown when continue: false
  "suppressOutput": false,             // hide from verbose mode
  "systemMessage": "Warning message",
  
  // For PreToolUse specifically:
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Reason for decision",
    "updatedInput": {
      "field": "new value"  // Modifies tool input before execution
    },
    "additionalContext": "Text for Claude"
  },
  
  // For other events (PostToolUse, Stop, etc):
  "decision": "block",                 // Only value is "block"
  "reason": "Why blocked",
  "additionalContext": "Text for Claude"
}
```

#### 1.6 Matcher Patterns

Matchers are regex patterns that filter when hooks fire:

```json
{
  "matcher": "Bash",           // Exact tool name
  "matcher": "Edit|Write",     // OR pattern
  "matcher": "mcp__.*",        // Any MCP tool
  "matcher": "mcp__github__.*", // Specific MCP server
  "matcher": "",               // OR omit - matches all
  "matcher": "*"               // Same as omitting
}
```

MCP Tool Naming: `mcp__<server>__<tool>`
- Example: `mcp__memory__create_entities`, `mcp__github__search_repositories`

#### 1.7 Hook Types

**1. Command Hooks** (`type: "command"`)
- Runs a shell script
- Input arrives on stdin as JSON
- Output via stdout (JSON), stderr, and exit code
- Hooks run with `$CLAUDE_PROJECT_DIR` environment variable available
- Use `"$CLAUDE_PROJECT_DIR"/.claude/hooks/script.sh` for project-relative paths

```json
{
  "type": "command",
  "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/inspect.sh",
  "timeout": 30,
  "async": false
}
```

**2. HTTP Hooks** (`type: "http"`)
- POSTs JSON to a URL
- Response body uses same JSON schema as command hook output
- Environment variables in headers: `"$VAR_NAME"` or `"${VAR_NAME}"`
- Must list allowed env vars: `"allowedEnvVars": ["VAR_NAME"]`

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "headers": {
    "Authorization": "Bearer $MY_TOKEN",
    "X-Session": "${CLAUDE_SESSION_ID}"
  },
  "allowedEnvVars": ["MY_TOKEN", "CLAUDE_SESSION_ID"],
  "timeout": 30
}
```

**3. Prompt Hooks** (`type: "prompt"`)
- Sends a single-turn prompt to Claude Haiku (or specified model)
- Returns `{"ok": true}` or `{"ok": false, "reason": "why"}`
- Use for judgment-based decisions, not deterministic rules

```json
{
  "type": "prompt",
  "prompt": "Should this tool call proceed? Respond with {\"ok\": true} or {\"ok\": false, \"reason\": \"...\"} $ARGUMENTS",
  "model": "opus",  // optional
  "timeout": 30
}
```

**4. Agent Hooks** (`type: "agent"`)
- Spawns a subagent with tool access (Read, Grep, Glob, Bash, etc.)
- Returns `{"ok": true}` or `{"ok": false, "reason": "..."}`
- Use when verification requires inspecting files or running commands
- Default timeout: 60 seconds (longer than prompt hooks)

```json
{
  "type": "agent",
  "prompt": "Verify all tests pass. Run the test suite and report. $ARGUMENTS",
  "timeout": 120,
  "model": "opus"  // optional
}
```

#### 1.8 Security Considerations

- **No shell injection risk**: Hook input is always JSON, not shell commands
- **API key handling**: Pass via environment variables (`$MY_TOKEN`) in HTTP hooks, don't hardcode
- **Permission rules**: Hooks can be restricted by admin settings (`allowManagedHooksOnly`, `allowedHttpHookUrls`)
- **Prevent loops**: SessionStart hooks run on EVERY session - keep them fast
- **Profile interference**: If your shell profile has unconditional `echo`, it breaks JSON parsing. Use `if [[ $- == *i* ]]` to limit to interactive shells

#### 1.9 Best Practices for Hook Development

1. **Use absolute paths or `$CLAUDE_PROJECT_DIR`** for project files
2. **Test hooks manually** by piping sample JSON: `echo '{"tool_name":"Bash",...}' | ./hook.sh`
3. **Check exit codes** with `echo $?` after running manually
4. **Use `jq` for JSON parsing** in shell scripts - it handles edge cases reliably
5. **Make scripts executable** on Unix: `chmod +x ./hook.sh`
6. **Parse stdin completely** before writing output - partial reads cause hangs
7. **For large JSON**, use proper JSON parsers, not regex
8. **Keep SessionStart hooks fast** - they run on every session resume
9. **Use non-interactive shell guards** in your profile to avoid breaking JSON parsing
10. **Test the full chain** - verify the hook fires with `/hooks` menu, check verbose mode with `Ctrl+O`

#### 1.10 Example: Hook That Inspects Write Content

Here's a complete example that inspects file content being written:

**`.claude/hooks/inspect-content.sh`:**

```bash
#!/bin/bash

INPUT=$(cat)  # Read JSON from stdin
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

# Example: Block writing secrets
if echo "$CONTENT" | grep -q 'password\|api_key\|secret'; then
  echo "Blocked: File contains sensitive values" >&2
  exit 2
fi

# Example: Allow with modification
if [ ${#CONTENT} -gt 10000 ]; then
  # Return JSON to modify content before write
  echo "$INPUT" | jq -c '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "ask",
      "permissionDecisionReason": "File is very large ('"${#CONTENT}"' chars). Confirm to proceed."
    }
  }'
else
  exit 0  # Allow as-is
fi
```

**`.claude/settings.json`:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/inspect-content.sh"
          }
        ]
      }
    ]
  }
}
```

**Key points:**
- PreToolUse has access to `tool_input.content` (the full file content)
- You can return `permissionDecision: "deny"` to block, `"ask"` to prompt, or `"allow"` to auto-approve
- You can use `updatedInput` to modify the content before writing
- Exit code 2 blocks and shows stderr to Claude
- Exit 0 + JSON gives you structured control

---

### 2. CLAUDE CODE SKILLS SYSTEM

#### 2.1 Skill File Structure

Skills are prompt-based templates that extend Claude's capabilities. Every skill needs a `SKILL.md` file:

```
~/.claude/skills/my-skill/
├── SKILL.md                 # Required: main instructions with frontmatter
├── reference.md             # Optional: detailed reference
├── examples.md              # Optional: example outputs
├── templates/
│   └── output-template.md  # Optional: template Claude fills in
└── scripts/
    └── helper.py           # Optional: scripts Claude can execute
```

**Skill Location Scopes:**

| Location   | Path                                    | Applies to                |
| :--------- | :-------------------------------------- | :------------------------ |
| Enterprise | Managed settings (admin-controlled)    | All users in organization |
| Personal   | `~/.claude/skills/<name>/SKILL.md`      | All your projects         |
| Project    | `.claude/skills/<name>/SKILL.md`        | This project only         |
| Plugin     | `<plugin>/skills/<name>/SKILL.md`       | Where plugin is enabled   |

When skills share names, priority is: Enterprise > Personal > Project. Plugin skills use namespace `plugin-name:skill-name`.

#### 2.2 SKILL.md Format

Every `SKILL.md` has two parts:

**1. YAML Frontmatter** (between `---` markers):

```yaml
---
name: my-skill
description: What this skill does and when Claude should use it
argument-hint: "[filename] [format]"
disable-model-invocation: false
user-invocable: true
allowed-tools: "Read, Grep, Glob"
model: "opus"
context: "fork"
agent: "Explore"
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
---
```

**2. Markdown Content** (skill instructions):

```markdown
When doing X, always:

1. Follow convention A
2. Use approach B
3. Validate with C

For detailed reference, see [reference.md](reference.md).
```

#### 2.3 Frontmatter Fields Reference

| Field                      | Required    | Description                                                                                                                           |
| :------------------------- | :---------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| `name`                     | No          | Display name (lowercase, numbers, hyphens, max 64 chars). If omitted, uses directory name                                            |
| `description`              | Recommended | What the skill does. Claude uses this to decide when to invoke it automatically                                                       |
| `argument-hint`            | No          | Hint for autocomplete, e.g., `[issue-number]` or `[filename] [format]`                                                              |
| `disable-model-invocation` | No          | `true` = only you can invoke (e.g., for deployments). Default: `false`                                                              |
| `user-invocable`           | No          | `false` = only Claude invokes (background knowledge). Default: `true`                                                                |
| `allowed-tools`            | No          | Comma-separated tools Claude can use without asking. Example: `Read, Grep, Glob`                                                    |
| `model`                    | No          | Override default model for this skill. Example: `opus`, `sonnet`, `haiku`                                                           |
| `context`                  | No          | `fork` = run in isolated subagent context (skill content becomes the task)                                                           |
| `agent`                    | No          | Which subagent type to use with `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or custom agent names             |
| `hooks`                    | No          | Hooks scoped to this skill's lifecycle. Uses same format as settings.json hooks                                                      |

#### 2.4 String Substitutions Available in Skills

When you invoke a skill with arguments, Claude receives:

```yaml
---
name: fix-issue
description: Fix a GitHub issue
---

Fix issue $ARGUMENTS with these steps:
1. Read the issue
2. Implement fix
3. Test it

# Alternative syntax:
$0 = first argument
$1 = second argument
$ARGUMENTS[0] = first argument
${CLAUDE_SESSION_ID} = current session ID
```

Example: `/fix-issue 123` → Claude sees "Fix issue 123 with these steps..."

#### 2.5 Skill Invocation Types

**Let Claude invoke automatically** (if `disable-model-invocation: false`):
- Claude detects when the skill's description matches the task
- Full skill content loads into context automatically
- Best for reference content and guidelines

**You invoke directly** with `/skill-name`:
- Type `/skill-name arguments` in Claude Code
- Claude gets the skill instructions plus any arguments
- Works even if `disable-model-invocation: true`

**You hide from menu** with `user-invocable: false`:
- Claude can still invoke automatically
- You cannot see it in the `/` menu
- Use for background knowledge

#### 2.6 Advanced Skill Patterns

**Inject Dynamic Context** using `!`command\`\` syntax:

```yaml
---
name: pr-summary
description: Summarize a pull request
---

## PR Context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

Summarize these changes...
```

The commands run BEFORE Claude sees the skill, and their output gets inserted.

**Run Skill in Isolated Context** with `context: fork`:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS:

1. Find relevant files
2. Analyze code
3. Summarize with file references
```

When invoked, this creates a subagent that gets this skill as its entire task prompt.

**Control Tool Access** with `allowed-tools`:

```yaml
---
name: safe-reader
description: Read files safely without modifications
allowed-tools: "Read, Grep, Glob"
---
```

Claude can only use these tools while this skill is active.

**Limit Invocation** - use both fields:

| Frontmatter                      | You invoke | Claude invokes | When loaded in context      |
| :------------------------------- | :--------- | :------------- | :-------------------------- |
| (default)                        | Yes        | Yes            | Always (description + full) |
| `disable-model-invocation: true` | Yes        | No             | Not loaded (hidden)         |
| `user-invocable: false`          | No         | Yes            | Always (loaded on invocation) |

#### 2.7 Supporting Files in Skills

Keep `SKILL.md` under 500 lines by referencing supporting files:

```markdown
# My Skill

For API reference, see [api-reference.md](api-reference.md).
For examples, see [examples.md](examples.md).

## Main Task
...
```

Claude only loads supporting files when you explicitly reference them or when they're needed for the task.

#### 2.8 Example: Complete Skill with All Features

```yaml
---
name: deploy-service
description: Deploy a service to production with validation
disable-model-invocation: true
allowed-tools: "Bash(npm *), Bash(git *), Read, Grep"
argument-hint: "[service-name] [environment]"
---

# Deploy Service

Deploy service **$0** to environment **$1**.

## Pre-deployment checklist

1. Verify tests pass: `npm test`
2. Check git status: `git status`
3. Review changes: `git diff main`

## Deployment steps

1. Build the service: `npm run build -- --service $0`
2. Run health checks: `npm run health-check -- $1`
3. Deploy: `npm run deploy -- --service $0 --env $1`
4. Verify deployment
5. Create a commit with the deployment details

## Rollback procedure

If deployment fails:
1. Run rollback: `npm run rollback -- --service $0 --env $1`
2. Notify team
3. Create an incident ticket
```

---

### 3. SETTINGS.JSON SCHEMA - HOOKS SECTION

The complete hook configuration in `.claude/settings.json` or `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Bash(*)", "Read(**)", "Write(**)", "Edit(**)", "Glob(**)", "Grep(**)", "WebFetch", "WebSearch"],
    "deny": []
  },
  "model": "opus",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh\"",
            "timeout": 10,
            "statusMessage": "Loading context..."
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Should this prompt be processed? Return {\"ok\": true} or {\"ok\": false, \"reason\": \"...\"}",
            "timeout": 30
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-bash.sh",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/inspect-write.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $(jq -r '.tool_input.file_path')",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify all tasks are complete. If not, return {\"ok\": false, \"reason\": \"what remains\"}",
            "timeout": 60
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/auto-approve-safe.sh"
          }
        ]
      }
    ]
  },
  "disableAllHooks": false
}
```

---

### 4. KEY LIMITATIONS & GOTCHAS

**Hook Capabilities:**
- ✅ Inspect tool input before execution (PreToolUse)
- ✅ Modify tool input before execution (updatedInput in PreToolUse)
- ✅ Block tool calls deterministically
- ✅ Read file content being written (in PreToolUse for Write tool)
- ✅ Inject context into Claude's conversation
- ✅ Run async background tasks

**Hook Limitations:**
- ❌ Cannot directly trigger tool calls or Claude actions from hooks
- ❌ HTTP hooks cannot signal blocking via status code alone (must use 2xx response with JSON)
- ❌ PostToolUse hooks cannot undo actions (tool already executed)
- ❌ PermissionRequest hooks do not fire in non-interactive mode (`-p`) - use PreToolUse instead
- ❌ Stop hooks fire on every response finish, not just task completion
- ❌ Default timeout is 10 minutes (configurable per hook)
- ❌ Your shell profile's unconditional echo statements break JSON parsing

**For Your Use Case (inspecting Write/Edit content):**
- Use **PreToolUse with Write matcher** - has full file content in `tool_input.content`
- Edit tool only has the replacement strings, not the final file content
- If you need post-write validation, use PostToolUse, but remember it can't undo
- For complex inspection, consider using an agent hook instead of command hook

---

### 5. PROJECT SCAFFOLDING & BEST PRACTICES

**Recommended hook directory structure:**

```
.claude/
├── hooks/
│   ├── session-start.sh
│   ├── pre-tool-use.sh
│   ├── inspect-write.sh
│   ├── validate-bash.sh
│   └── README.md (document your hooks)
├── rules/
│   ├── quality-gates.md
│   ├── naming-conventions.md
│   ├── problem-solving.md
│   └── spec-readiness.md
├── skills/
│   ├── my-skill/
│   │   ├── SKILL.md
│   │   ├── reference.md
│   │   └── scripts/
│   │       └── helper.py
│   └── another-skill/
│       └── SKILL.md
└── settings.json
```

**Anthropic's Recommendations:**
1. **Use hooks for deterministic enforcement** (security, format validation)
2. **Use skills for judgment-based instructions** (guidelines, patterns, domain knowledge)
3. **Use subagents for isolated complex tasks** (research, parallel work)
4. **Start with SessionStart hooks to load context** (recent commits, pending work)
5. **Create PreToolUse hooks for safety** (block dangerous patterns, validate input)
6. **Use PostToolUse hooks for cleanup** (formatting, linting, notifications)
7. **Document your hooks** - add a README explaining what each hook does and why

---

### 6. CRITICAL FINDING: PRETOOLUSE HOOKS CAN INSPECT WRITE CONTENT

Your specific use case - **inspecting file content being written before it's committed**:

**Status: Fully supported**

A PreToolUse hook with `matcher: "Write"` receives:

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "entire file content as string"  // <-- YOU CAN INSPECT THIS
  }
}
```

You can:
1. ✅ Inspect the content for patterns (secrets, quality issues, size limits)
2. ✅ Modify it with `updatedInput.content` before writing
3. ✅ Block the write with `permissionDecision: "deny"`
4. ✅ Ask the user with `permissionDecision: "ask"`
5. ✅ Auto-approve with `permissionDecision: "allow"`

**Example implementation:**

```bash
#!/bin/bash
INPUT=$(cat)
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content')

# Check for issues
ISSUES=$(python3 validate_content.py <<< "$CONTENT")

if [ -n "$ISSUES" ]; then
  echo "$INPUT" | jq -c '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "ask",
      "permissionDecisionReason": "'"$ISSUES"'"
    }
  }'
else
  exit 0
fi
```

---

## Summary

Claude Code provides a mature, well-designed hooks system for inspecting and controlling tool execution. PreToolUse hooks give you full access to file content being written, enabling comprehensive validation before files are created. The skills system is designed for prompt-based task automation, while hooks are for deterministic rules enforcement.

Sources:
- [Hooks reference](https://code.claude.com/docs/en/hooks.md)
- [Hooks guide](https://code.claude.com/docs/en/hooks-guide.md)
- [Skills documentation](https://code.claude.com/docs/en/skills.md)
- [Settings documentation](https://code.claude.com/docs/en/settings.md)



================================================================================

# 02_template_sync_research (agent-a6cc7444ffb8d21fe.jsonl)

## Message 1

Now I have comprehensive research. Let me compile this into a thorough summary.

---

# Template Repository Synchronization: Patterns, Tools, and Tradeoffs

## The Core Problem

You have a template repository that evolves. Projects created from it have customized certain files. You need to propagate template updates to existing projects without destroying customizations. This is fundamentally a **three-way merge problem** between three states:

1. **Old template** (what generated the project originally)
2. **Current project** (template output + user modifications)
3. **New template** (the evolved template)

Below are the major patterns that exist in the wild, ordered from most sophisticated to most primitive.

---

## Pattern 1: Copier (Three-Way Merge with Answer Memory)

**The gold standard for this exact problem.**

Copier is a Python tool that has evolved from a scaffolding tool into what it calls a "code lifecycle management tool." It is the only major tool with **native, first-class support** for updating existing projects from template changes.

### How It Works Internally

The `copier update` command executes a 10-step algorithm:

1. Reads `.copier-answers.yml` to extract the old template version (`_commit`) and source (`_src_path`)
2. Clones both old and new template versions from their git repository
3. Regenerates a clean project from the **old** template using the stored answers
4. Computes a diff between that clean regeneration and the **actual current project** (this is the "user diff")
5. Runs pre-migration scripts
6. Re-prompts only questions whose definitions changed between versions
7. Generates a fresh project from the **new** template with updated answers
8. Applies the user diff on top of the new generation
9. If patches conflict, inserts Git-style conflict markers (or `.rej` files)
10. Runs post-migration scripts and updates `.copier-answers.yml`

### How It Distinguishes Template from User Content

Copier uses several mechanisms:

| Directive | Behavior |
|-----------|----------|
| `_exclude` | Files never copied to destination (template metadata, `.git`, etc.) |
| `_skip_if_exists` | Files generated on first copy but **never overwritten** during updates. Regenerated only if missing. |
| `_preserve` | Files **never rendered during update**, regardless of existence. Strongest protection. |
| `_templates_suffix` | Files ending in `.jinja` are processed by the template engine; others are copied as-is. |

The philosophy is explicit: **the template author decides which files are template-owned vs. user-owned.** This is declared in `copier.yml`.

### Metadata Format

```yaml
# .copier-answers.yml (auto-generated, NEVER edit manually)
_src_path: https://github.com/org/template.git
_commit: v2.1.0-3-gabc123
_subdirectory: project
project_name: MyProject
author: Nathan
license: MIT
```

### Migration Scripts

Copier supports version-gated migration hooks:

```yaml
_migrations:
  - version: "2.0.0"
    before:
      - "python scripts/rename_config.py"
    after:
      - "npm install"
```

These only run when updating **to** the specified version or later.

### Known Failure Modes

- **Broken regeneration**: If the old template relied on external resources no longer available, the clean regeneration (step 3) fails and the entire diff calculation breaks
- **Jinja extension incompatibility**: Old and new template versions depending on incompatible Jinja extensions
- **Copier version skew**: Old template built for an older Copier version may not regenerate cleanly
- **Manual `.copier-answers.yml` edits**: Corrupts the diff algorithm because Copier assumes the answers produced the current project state
- **Context line sensitivity**: The `--context-lines` setting (default: 3) affects conflict detection accuracy. More lines = more accurate but more manual conflicts

### Pros
- Most sophisticated merge algorithm available
- Template author has fine-grained control over file ownership
- Migration scripts enable complex version transitions
- Git-native conflict resolution (familiar to developers)
- Active development, growing community

### Cons
- Requires Python (though it's a CLI tool, not a library dependency)
- Template must be a git repository with tags for versioning
- No "partial update" -- it's all-or-nothing per template version
- Learning curve for template authors to design the `copier.yml` correctly
- Newer tool with smaller ecosystem than Cookiecutter

---

## Pattern 2: Cruft (Cookiecutter + Diff Patching)

Cruft is a bolt-on tool that adds update capability to Cookiecutter templates. It stores a `.cruft.json` file in the project root.

### How It Works

1. Stores the template commit hash in `.cruft.json` at generation time
2. On `cruft update`, calculates the diff between the old commit and current template HEAD
3. Applies that diff to the project using `git apply` (falling back to `patch`)
4. If conflicts arise, they're handled like git merge conflicts

### Metadata Format

```json
{
  "template": "https://github.com/org/cookiecutter-template",
  "commit": "abc123def456",
  "checkout": null,
  "context": {
    "cookiecutter": {
      "project_name": "MyProject",
      "author": "Nathan"
    }
  },
  "directory": null
}
```

### How It Distinguishes Template from User Content

It does **not** -- Cruft applies template diffs globally. There is no `_skip_if_exists` equivalent. It relies entirely on the diff/patch mechanism to handle conflicts. If the user modified a file the template also changed, you get a merge conflict.

### Known Failure Modes

- **Three-way merge failures on fresh clones**: Cruft's 3-way merge can succeed on the working copy but fail when cloning a new copy of the repository
- **Patch hunk failures**: When searching for specific patch context, hunks can fail to apply if surrounding code changed significantly
- **No migration scripts**: No equivalent to Copier's version-gated migrations

### Pros
- Compatible with the massive Cookiecutter template ecosystem (4000+ templates)
- Simpler mental model than Copier
- `cruft diff` command lets you preview changes before applying

### Cons
- Bolt-on solution, not integrated into the template tool itself
- No file-level ownership declarations
- No migration scripts
- Less actively maintained than Copier
- Diff-based approach is more fragile than Copier's regeneration approach

---

## Pattern 3: Git Upstream Remote (Pure Git)

The most "native" approach: treat the template repository as an upstream remote and use Git's merge machinery.

### How It Works

```bash
# In the project repo, add template as upstream
git remote add template https://github.com/org/template.git
git remote set-url --push template no_push  # read-only safety

# When template updates:
git fetch template
git merge template/main --allow-unrelated-histories
# Resolve conflicts manually
```

### How It Distinguishes Template from User Content

It does **not** distinguish them at all. Git's merge treats all files equally. You get standard three-way merge conflicts when both sides modified the same file. You can use `.gitattributes` with merge strategies (`merge=ours`) for specific files, but this is manual and brittle.

### Pros
- Zero additional tooling required
- Developers already understand Git merge
- Full history preserved
- Works with any file type, any language

### Cons
- **No concept of template variables** -- can't customize file content during merge
- Every merge potentially touches every file, creating noise
- `--allow-unrelated-histories` needed on first merge (no shared commit ancestry)
- No way to declare "this file is user-owned, never touch it" at the template level
- Merge conflicts on every file the user customized, even if the template change was unrelated to the customized section
- Does not scale well across many downstream projects

---

## Pattern 4: GitHub Actions Template Sync (PR-Based)

Several GitHub Actions exist that automate template-to-project synchronization via pull requests. The most prominent is [actions-template-sync](https://github.com/AndreasAugustin/actions-template-sync).

### How It Works

1. A scheduled GitHub Action runs in the downstream project
2. It fetches the template repository
3. Merges changes using `--allow-unrelated-histories --squash --strategy=recursive -X theirs`
4. Creates a PR with the changes for human review
5. Uses `.templatesyncignore` (glob patterns, like `.gitignore`) to exclude files

### Key Detail: Default Strategy is "Theirs"

The default merge strategy **prefers template changes** (`-X theirs`). This means the template wins conflicts by default. The assumption is that the PR review step catches unwanted overwrites.

### How It Distinguishes Template from User Content

Through `.templatesyncignore` -- a file in the downstream project listing glob patterns of files that should never be synced from the template. This is the **inverse** of Copier's approach: instead of the template declaring what it owns, the project declares what it protects.

### Pros
- Fully automated via CI/CD
- Human review via PR before changes land
- Simple `.templatesyncignore` is easy to understand
- Works across git providers (GitHub, GitLab, Gitea)

### Cons
- Default "theirs" strategy is dangerous -- silently overwrites customizations unless `.templatesyncignore` is complete
- No template variable support
- No migration scripts
- Binary "sync or ignore" per file -- no merging within files
- `.templatesyncignore` in the downstream repo means the template author can't control what's safe to sync

---

## Pattern 5: Yeoman (Interactive Conflict Resolution)

Yeoman is the oldest major scaffolding tool. It handles updates through an interactive conflict resolution UI.

### How It Works

When a generator runs against an existing project, Yeoman detects existing files and prompts the user per-file:

- **Overwrite** this file?
- **Skip** this file?
- **Show diff** between old and new?

### How It Distinguishes Template from User Content

It doesn't, really. Every pre-existing file triggers the conflict resolver. For updating files (like adding an import to an existing file), Yeoman recommends **AST parsing** -- actually parsing the file's abstract syntax tree and surgically inserting changes. This is powerful but extremely complex to implement per file type.

### Pros
- Interactive UI gives users full control
- AST-based modifications are surgically precise
- Massive ecosystem (Node.js world)

### Cons
- Interactive-only -- cannot be automated
- No batch update capability across many projects
- AST parsing must be custom-built per file type
- Effectively abandoned for template update use cases
- No metadata tracking of template version

---

## Pattern 6: Plop / Hygen (Micro-Generators, Not Updaters)

These are **not** template synchronization tools. They are micro-generators for adding new files/code to an existing project. Including them for completeness since you asked.

- **Plop**: Supports "add" (new file) and "modify" (append/prepend/regex-replace in existing files) actions
- **Hygen**: File-based templates that live in `_templates/` within the project

Neither tool has any concept of template versioning or propagating upstream changes. They solve a different problem: "generate a new component/module from a pattern." They are complements to a sync tool, not replacements.

---

## Pattern 7: Organization-Wide Config (GitHub .github Repo, Renovate Presets, Probot)

These are **runtime config propagation** patterns, not template sync. But they solve a related sub-problem: keeping shared configuration in sync across many repos.

### GitHub `.github` Repository
- Organization-level repo that provides default community health files (issue templates, PR templates, CODE_OF_CONDUCT, etc.)
- Files are used as **fallbacks** only -- a repo's own files always take precedence
- Very limited scope: only specific community files, not arbitrary config

### Renovate Shareable Presets
- A config repo contains shared Renovate configuration in JSON format
- Individual repos `extends` the shared config
- Deep merging: nested objects don't need to be redefined completely
- **This is the "extend, don't copy" pattern** -- config lives in one place and is referenced, not duplicated

### Probot Config
- Shared config in a central org repo, deeply merged with repo-local config
- Same "extend, don't copy" philosophy

### Key Insight

These tools avoid the sync problem entirely by using **runtime references** instead of **file copies**. The config isn't copied into each project -- it's referenced from a central source. This only works for tools that support `extends` or `preset` mechanisms.

---

## Comparative Analysis

| Criterion | Copier | Cruft | Git Upstream | Actions-Sync | Yeoman |
|-----------|--------|-------|-------------|--------------|--------|
| Three-way merge | Yes (regeneration) | Yes (diff/patch) | Yes (git merge) | No (theirs wins) | No |
| Template variables | Yes (Jinja2) | Yes (Jinja2) | No | No | Yes (EJS) |
| File ownership declaration | Yes (`_skip_if_exists`, `_preserve`, `_exclude`) | No | No (`.gitattributes` hack) | Yes (`.templatesyncignore`) | No |
| Migration scripts | Yes (version-gated) | No | No | No | No |
| Automation-friendly | Yes (CLI, `--defaults`) | Yes (CLI) | Yes (scriptable) | Yes (CI/CD native) | No (interactive) |
| Metadata format | `.copier-answers.yml` | `.cruft.json` | Git remotes | `.templatesyncignore` | None |
| Ecosystem size | Growing | Cookiecutter compat | Universal | GitHub-specific | Large (Node) |
| Conflict resolution | Inline markers / `.rej` files | Git-style / patch | Git merge conflicts | PR review | Interactive prompt |

---

## Recommendations for Your Use Case

Given that your template repo (`_ProjectTemplate`) contains a mix of infrastructure files (`.claude/rules/`, `CLAUDE.md`, spec templates, validation scripts) and user-customizable files (project-specific `CLAUDE.md` content, `Specs/` documents), here is how I'd rank the approaches:

### Best Fit: Copier

Copier's file ownership model maps perfectly to your problem:

- **Template-owned files** (`.claude/rules/*.md`, `validate_traceability.py`, `Specs/TEMPLATE_*.md`): Managed by the three-way merge. Template updates flow through; user modifications to these are rare and would be handled by conflict markers.
- **User-customizable files** (`CLAUDE.md`, `Specs/{Abbrev}_*.md`): Use `_skip_if_exists` so they're generated once with template variables (e.g., `{ProjectName}`) but never overwritten on update.
- **User-owned files** (session docs, work orders, code): Use `_exclude` so the template never touches them.
- **Migration scripts**: When you change the rule format or add a new required file, migrations handle the transition.

### Runner-Up: Git Upstream Remote + `.gitattributes`

If you want zero additional tooling, the Git upstream remote approach works, but you'd need to manually manage which files get `merge=ours` in `.gitattributes` to prevent overwriting customizations. This is simpler but more error-prone and doesn't support template variables.

### Avoid: Actions-Template-Sync with Default Settings

The default "theirs wins" strategy is dangerous for your use case where `CLAUDE.md` contains project-specific frozen decisions. One forgotten `.templatesyncignore` entry and you lose load-bearing wall definitions.

---

## Sources

- [Copier - Updating a Project](https://copier.readthedocs.io/en/stable/updating/)
- [Copier - Configuring a Template](https://copier.readthedocs.io/en/stable/configuring/)
- [Copier - Comparisons with Other Tools](https://copier.readthedocs.io/en/stable/comparisons/)
- [Copier Update Internals (DeepWiki)](https://deepwiki.com/copier-org/copier/3.4-updating-projects)
- [Copier GitHub Repository](https://github.com/copier-org/copier)
- [Template Once, Update Everywhere (Substack)](https://aiechoes.substack.com/p/template-once-update-everywhere-build-ab3)
- [GitHub Community Discussion: How to sync template changes?](https://github.com/orgs/community/discussions/23528)
- [actions-template-sync GitHub Action](https://github.com/AndreasAugustin/actions-template-sync)
- [GitHub Templates and Repository Sync (0xDC.me)](https://0xdc.me/blog/github-templates-and-repository-sync/)
- [Cruft - Template Lifecycle Management for Cookiecutter](https://cruft.github.io/cruft/)
- [Cruft GitHub Repository](https://github.com/cruft/cruft)
- [Cookiecutter - Replay Feature](https://cookiecutter.readthedocs.io/en/latest/advanced/replay.html)
- [Cookiecutter Issue #784: How to update from template?](https://github.com/cookiecutter/cookiecutter/issues/784)
- [Cruft 3-Way Merge Failures (Issue #181)](https://github.com/cruft/cruft/issues/181)
- [Configuring GitHub Templates to Merge from Upstream (Sciri.net)](https://sciri.net/blog/configuring-github-templates-to-merge-from-upstream/)
- [Propagating Git Repo Changes Downstream (mslinn.com)](https://www.mslinn.com/git/700-propagating-git-template-changes.html)
- [Probot Config Extension](https://github.com/probot/probot-config)
- [Renovate Shareable Config Presets](https://docs.renovatebot.com/config-presets/)
- [Copier vs Cookiecutter (DEV Community)](https://dev.to/cloudnative_eng/copier-vs-cookiecutter-1jno)
- [Cookiecutter with Cruft for Platform Engineering](https://john-miller.dev/posts/cookiecutter-with-cruft-for-platform-engineering/)
- [ahmadnassri/action-template-repository-sync](https://github.com/ahmadnassri/action-template-repository-sync)
- [Yeoman Conflict Resolution (Issue #966)](https://github.com/yeoman/generator/issues/966)



================================================================================

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



================================================================================

# 04_redteam_architecture_flaws (agent-aab54307cc3bba908.jsonl)

## Message 1

Good -- this confirms the system I'm analyzing. The manifest-based governance system (TEMPLATE_MANIFEST.json, template-guard.sh, template_sync.py, /init-doc skill) described in the briefing is the **planned next phase** that doesn't exist yet. What exists today is the template as it stands. Let me read the most recent session to understand the current state and planned direction.

## Message 2

Now I have a complete picture. The system described in the briefing (TEMPLATE_MANIFEST.json, template-guard.sh, template_sync.py, /init-doc skill) is a **planned architecture that doesn't yet exist**. What exists is the current template with its hooks, rules, skills, and spec-driven development framework. My red team analysis will address both the existing system AND the proposed manifest-based governance layer, since the briefing explicitly asks me to evaluate the planned design.

---

# RED TEAM ARCHITECTURAL ANALYSIS
## Template Governance System -- Fundamental Design Flaws

---

## FLAW 1: The Entire Enforcement Model is Advisory, Not Mechanistic

### The Flaw

The system's enforcement layer operates entirely through Claude Code hooks -- shell scripts that output JSON messages to influence agent behavior. These hooks do not modify the filesystem, do not create locks, and do not prevent writes at the OS level. They emit `exit 2` (block suggestion) or JSON `permissionDecision: deny` messages, which are **suggestions to the AI agent**, not hard barriers.

Examining `spec-gate.sh` (line 127): `exit 2  # BLOCK` -- this asks Claude Code to not proceed. But the enforcement depends on:
1. Claude Code honoring the hook's exit code
2. The agent not finding workaround paths (e.g., writing to a file path that doesn't match `CODE_DIRS`)
3. No other tool being used that bypasses the hook (e.g., a Bash `echo >` command, which triggers `block-dangerous.sh` but not `protect-frozen-files.sh` or `spec-gate.sh`)

Similarly, `protect-frozen-files.sh` requires manual population of the `FROZEN_PATTERNS` array (currently empty, line 15-17). The protection is opt-in per file, per project. A project that forgets to populate this array has zero frozen file protection despite the entire governance framework assuming it exists.

### Why It Matters

The system creates an **illusion of enforcement** that is actually voluntary compliance. This is the difference between a lock on a door and a sign that says "please don't enter." For a single operator (Nathan) working with AI agents, this may be acceptable today. But it means:

- An agent in a new session (especially post-compaction) could bypass spec-gate if it uses Bash writes instead of Edit/Write tools
- The `protect-frozen-files.sh` hook is effectively disabled in the template -- every new project starts with no frozen file protection until someone manually edits the array
- If Claude Code's hook system behavior changes (e.g., a future version handles exit codes differently), the entire enforcement layer silently fails

### Suggested Alternative

1. **Make `protect-frozen-files.sh` self-discovering** instead of manually populated. Have it scan for files containing `FROZEN` in their first 15 lines (the same logic `spec-gate.sh` and `validate_traceability.py` already use) rather than requiring a hardcoded array. This eliminates the gap between "spec is frozen" and "spec is protected."

2. **Add Bash-tool coverage to protect-frozen-files**. Currently it only triggers on `Edit|Write`. An agent could `echo "new content" > Specs/frozen_file.md` via Bash and the protection hook never fires. The `block-dangerous.sh` hook (which does trigger on Bash) should include frozen-file-path matching.

3. **Document the enforcement as advisory, not absolute**. The system's documentation implies hard enforcement. Being honest about the trust boundary helps Nathan make informed decisions about when to add OS-level protections (git hooks, file permissions).

---

## FLAW 2: The FROZEN Status Detection Is Fragile and Inconsistent

### The Flaw

"FROZEN" status is detected by string-matching the first 15 lines of a markdown file for the literal word `FROZEN`. This is used in three places with subtly different implementations:

- `spec-gate.sh` (line 54): `head -15 "$f" | grep -q "FROZEN"` -- matches FROZEN anywhere in the first 15 lines, including inside words, comments, or documentation about what frozen means
- `validate_traceability.py` (line 44-47): `re.search(r'\bFROZEN\b', line)` -- uses word boundary matching, slightly more precise
- `protect-frozen-files.sh`: Does not check frozen status at all; uses a hardcoded path array

These three components each have a different understanding of what "frozen" means:
- The shell hook matches "FROZEN" as a substring (would match "UNFROZEN" or "NOT FROZEN")
- The Python validator matches "FROZEN" as a word boundary (would not match "UNFROZEN" but would match in a sentence like "Status: NOT FROZEN yet")
- The file protection hook ignores frozen status entirely

Furthermore, the templates use `| **Status** | DRAFT / FROZEN |` as the status field format. But the detection doesn't parse the table structure -- it just looks for the word in any context within 15 lines. A comment like `<!-- TODO: Change to FROZEN when ready -->` in line 3 would cause `spec-gate.sh` to treat the document as frozen.

### Why It Matters

Frozen status is the system's single most important state transition. It is the gate between "speccing" and "coding." If this detection is wrong:
- **False positive** (detects FROZEN when it shouldn't): The spec-gate opens prematurely, allowing code to be written against incomplete specs -- directly violating the Gold Rush Doctrine's "no code before frozen specs" rule
- **False negative** (misses FROZEN when it should detect): The spec-gate blocks code writes even after Nathan has approved specs, causing friction and workarounds

The inconsistency between shell and Python detection means the spec-gate hook and the traceability validator can disagree about whether a spec is frozen.

### Suggested Alternative

1. **Standardize on a single, unambiguous frozen marker**. Instead of free-text matching, use a structured marker that cannot be confused with documentation text:
   ```
   <!-- STATUS: FROZEN -->
   ```
   This is parseable by both shell (`grep -q '<!-- STATUS: FROZEN -->'`) and Python (`re.search(r'<!-- STATUS: FROZEN -->', line)`), and is unlikely to appear in explanatory text.

2. **Extract the frozen-check logic into a shared utility**. The `parse_hook_input.py` pattern already exists for shared hook logic. Create a `check_frozen.py` utility that both shell hooks and Python scripts call, eliminating the inconsistency.

3. **Fix the `head -15 | grep "FROZEN"` pattern** in `spec-gate.sh` to use `grep -w "FROZEN"` at minimum, matching the Python validator's word-boundary behavior.

---

## FLAW 3: The Traceability System Has No Reverse Validation Path

### The Flaw

The traceability validator (`validate_traceability.py`) validates chains **downward only**: it checks that ES references a valid PVD, BP references a valid ES, and so on. But it never validates **upward** in a meaningful way.

Specifically:
- It checks "does ES-3.2 reference a PVD-3 that exists?" (orphan detection)
- It checks "does PVD-3 have any ES-3.x?" (gap detection, lines 197-201)
- But it never checks "does the content of ES-3.2 actually implement what PVD-3 says?"

The IDs are purely numeric conventions. `ES-3.2` traces to `PVD-3` because the number `3` matches. But there is no validation that the content of ES-3.2 is actually related to PVD-3. An agent could create `ES-3.2: Database Indexing Strategy` under a PVD-3 that says "User Authentication" and the traceability system would report `CLEAN`.

More critically, the system detects orphans and gaps but has **no mechanism to detect drift**. If someone modifies a PVD feature description after the Engineering Spec was written, the traceability chain remains "valid" but the spec content is now misaligned.

### Why It Matters

The traceability system gives a false sense of completeness. A "CLEAN" report means "all IDs reference other IDs that exist" -- not "all work is properly justified and consistent." This is the difference between checking that every footnote has a source and checking that the footnotes actually support the claims.

In a system where AI agents are the primary implementers, this matters acutely. An agent post-compaction doesn't remember what PVD-3 said. It sees `ES-3.2 -> PVD-3 -> CLEAN` and assumes the chain is valid. If the chain is structurally correct but semantically wrong, the agent builds the wrong thing with full confidence.

### Suggested Alternative

1. **Add a content-hash field to traceability IDs**. When a PVD feature is frozen, compute a hash of its content. When ES-3.2 is written, record the PVD-3 content hash it was written against. On trace-check, compare the current PVD-3 content hash against what ES-3.2 expects. If they differ, flag a **DRIFT** warning.

2. **The `/alignment-check` skill already exists** for this purpose but is entirely manual. Integrate a lightweight semantic check into `/trace-check` that at minimum verifies that the title/description of each ES module mentions keywords from its parent PVD feature.

3. **At minimum, timestamp the freeze**. Record when each spec was frozen. If PVD was frozen at time T1 and ES at T2, but PVD's file modification timestamp is later than T1, something changed after freezing and the chain may be invalid.

---

## FLAW 4: The Session Start Hooks Are a Context Budget Time Bomb

### The Flaw

The three session hooks (`session-start.sh`, `session-resume.sh`, `session-compact.sh`) inject project state into the agent's context by dumping file contents to stdout. The compact hook is the most aggressive -- it outputs the **entire** Work Ledger and **entire** Gap Tracker via `cat`:

`session-compact.sh`, line 23: `cat "$WORK_LEDGER"` 
`session-compact.sh`, line 35: `cat "$GAP_TRACKER"`
`session-start.sh`, line 20: `cat "$WORK_LEDGER"`

For the empty template, this is trivial. But consider a real project mid-execution:
- A Work Ledger with 50 PVD features, 200 ES modules, 600 BP tasks, and 100 Work Orders produces a traceability tree that could easily exceed 500 lines
- A Gap Tracker with 100+ items across 4 tiers adds more
- The last session summary adds 20-25 lines

This entire payload is injected into the agent's context at session start. On compaction (the moment context is most constrained), the system dumps the **maximum** amount of context -- precisely when the agent has the **least** context budget available.

### Why It Matters

Claude Code has finite context windows. The session hooks are designed to prevent drift, but at scale they cause a different problem: **context starvation**. The more complete the project, the larger the Work Ledger, and the more context the hooks consume -- leaving less room for actual implementation work.

This creates a perverse dynamic: as the project matures and the governance data grows, the system has less capacity to do the work the governance exists to govern. The compact hook, which fires at 95% context usage, will inject a large Work Ledger into a context window that's already nearly full, potentially triggering another compaction, which triggers another compact hook, creating a loop.

### Suggested Alternative

1. **Implement progressive context injection**. Instead of dumping full files, the hooks should output **summaries** with an instruction to read the full file if needed:
   ```
   WORK LEDGER: 47 BP tasks, 12 complete, 3 in-progress, 32 pending. 
   2 errors, 4 warnings. Read Specs/Work_Ledger.md for full details.
   NEXT WO: WO-3.2.4-A (IN-PROGRESS)
   ```

2. **Set a hard character limit on hook output**. The compact hook should output at most 100-200 lines regardless of project size, prioritizing: current WO status, Tier 0 gaps, errors, and the immediate next task.

3. **Separate "what you need right now" from "what you can look up"**. The session hooks should tell the agent what to do next and where to find reference material, not pre-load all reference material.

---

## FLAW 5: The Template Distribution Model Has No Integrity Verification

### The Flaw

The template is distributed by copying the `_ProjectTemplate` folder. The README says:
> Copy this entire folder to `C:\Claude Folder\{YourProjectName}\`

After copying, the project is a fully independent clone with no connection back to the template. There is:
- No record of which template version was used to create the project
- No mechanism to detect when the template has been updated
- No way to selectively apply template updates to existing projects
- No checksums or integrity verification of template files

The planned manifest-based sync system (`TEMPLATE_MANIFEST.json`, `template_sync.py`) would address some of this, but it introduces its own structural problems:

**The manifest IS a single point of failure.** If it declares a file as `infrastructure` when it should be `scaffolding`, a sync operation silently overwrites project-customized content. This is a **data loss** scenario with no recovery path other than manual backup restoration.

**The category model is incomplete.** Three categories (`infrastructure`, `template`, `scaffolding`) cannot capture the real-world complexity:
- What about files that are `infrastructure` in some projects but `scaffolding` in others? (e.g., `.mcp.json` might need project-specific MCP servers)
- What about files that should be synced on initial creation but never updated? (one-time scaffold)
- What about files where the project has legitimately diverged and should never be synced again?

### Why It Matters

Without version tracking, Nathan has no way to know "Project CallMe was created from template v1.0 and is missing the SDD framework added in v2.0." He must manually compare every project against the current template to find gaps.

The proposed manifest-based sync is the right direction but the ownership model is too coarse. With only three categories and no per-project overrides, the sync system will either be too aggressive (overwriting project customizations) or too conservative (missing updates that should propagate), depending on how liberally `infrastructure` is assigned.

### Suggested Alternative

1. **Stamp projects at creation time**. When a project is created from the template, write a `.template_origin` file:
   ```json
   {
     "template_version": "2.0",
     "created_from": "EpochLabs_Project_Template",
     "created_date": "2026-03-01",
     "files_at_creation": {
       ".claude/hooks/spec-gate.sh": "sha256:abc123...",
       "CLAUDE.md": "sha256:def456..."
     }
   }
   ```
   This provides a baseline for diff-based sync rather than category-based sync.

2. **Use a 5-category ownership model** instead of 3:
   - `infrastructure-always`: Always overwritten (hooks, scripts -- things that must match template exactly)
   - `infrastructure-once`: Copied on project creation, never synced again (`.mcp.json`, `.gitignore`)
   - `template`: Reference files, always overwritten (TEMPLATE_*.md)
   - `scaffolding`: Section-level merge (CLAUDE.md, gap_tracker.md)
   - `project`: Never touched (everything else)

3. **Allow per-project manifest overrides**. A `.template_overrides.json` in the project could override categories: "In this project, `.mcp.json` is `project`-owned, not `infrastructure`."

---

## FLAW 6: The Section-Level Merge Strategy Is Architecturally Unsound for Markdown

### The Flaw

The planned `template_sync.py` would perform section-level merging on `scaffolding` files. This means parsing markdown by `##` headers, identifying which sections are "template-owned" vs "project-owned," and merging them.

Markdown is not a structured data format. Section-level merge on markdown has fundamental failure modes:

1. **Header ambiguity**: `## Architecture` in the template and `## Architecture -- Load-Bearing Walls` in the project. Are these the "same" section? What about `## 5. Module Specifications` vs `## Module Specifications`?

2. **Nesting ambiguity**: A `### Subsection` under `## Section A` in the template might appear under `## Section B` in the project if someone moved it. Which version wins?

3. **Content-between-sections**: Text between the last line of one section and the `##` header of the next belongs to which section? This is a real problem in CLAUDE.md where intent comments and blank lines separate logical blocks.

4. **The CLAUDE.md specifically has HTML comments as agent instructions**: `<!-- AGENT INSTRUCTION: ... -->`. These are invisible in rendered markdown but critical for agent behavior. A merge that drops or duplicates these comments silently changes agent behavior.

5. **No merge conflict resolution**: When both template and project modify the same section, what happens? Git's three-way merge with manual conflict markers is the established solution. Section-level markdown merge without conflict detection is a silent data loss mechanism.

### Why It Matters

CLAUDE.md is the single most important file in the system. It is described as "LAW" that "overrides everything." A merge operation that corrupts, truncates, or misaligns sections in CLAUDE.md doesn't just break a config file -- it changes the fundamental operating instructions for every AI agent that touches the project. And because the corruption happens at the markdown structural level, it may not be obvious. A duplicated `## Anti-Patterns` section or a missing `<!-- AGENT INSTRUCTION -->` comment would silently degrade governance.

### Suggested Alternative

1. **Do not merge CLAUDE.md at all**. Treat it as a `project`-owned file after initial creation. Template updates to CLAUDE.md should be surfaced as a **diff report** that Nathan manually applies, not auto-merged.

2. **If merge is required, use structured markers, not markdown parsing**:
   ```markdown
   <!-- TEMPLATE-OWNED:BEGIN identity -->
   ## Identity
   {ProjectName} is ...
   <!-- TEMPLATE-OWNED:END identity -->
   
   <!-- PROJECT-OWNED:BEGIN architecture -->
   ## Architecture -- Load-Bearing Walls
   ...
   <!-- PROJECT-OWNED:END architecture -->
   ```
   These explicit markers are unambiguous and parser-friendly.

3. **Generate a merge preview for human review** instead of auto-applying. Show Nathan what would change, let him approve section by section.

---

## FLAW 7: The Bootstrap/Chicken-and-Egg Problem is Unresolved

### The Flaw

The system has a circular dependency that becomes critical during template sync:

1. `template_sync.py` needs to update hook files (e.g., `spec-gate.sh`, `protect-frozen-files.sh`)
2. Hook files control what can be written (e.g., `protect-frozen-files.sh` blocks writes to frozen specs)
3. The sync engine writes files via the filesystem, but hooks only trigger on Claude Code's Write/Edit tools

This means template sync **must** run outside of Claude Code (as a direct Python script) to avoid triggering hooks. But this creates a second problem: if sync runs outside Claude Code, the governance layer has no visibility into what changed. The session-start hook won't know about files that were modified by sync until the next session starts.

More fundamentally: **who syncs the sync engine?** If `template_sync.py` itself is an `infrastructure` file that gets updated via sync, the old version of the sync engine is updating itself with the new version. This is the same class of problem as updating a package manager with the package manager.

### Why It Matters

The self-referential update problem means that a bug in a new version of `template_sync.py` could corrupt the sync process itself, and the recovery path requires manual intervention with knowledge of the system's internals.

The governance bypass during sync means there is a window where files are modified without hook oversight. If the sync introduces a broken hook (e.g., a `spec-gate.sh` with a syntax error), every subsequent Claude Code session in that project will fail on the first Edit/Write operation, with no clear diagnostic path for an AI agent.

### Suggested Alternative

1. **Two-phase sync**: Phase 1 syncs everything except hooks and the sync engine itself. Phase 2 syncs hooks and the sync engine, but only after Phase 1 is verified to work. This limits the blast radius of a broken update.

2. **Sync engine versioning with rollback**: Before self-updating, the sync engine copies itself to a backup location. If the new version fails its own test suite (which it should have), the backup is restored.

3. **Hook health check**: Add a post-sync validation step that runs each hook with test input and verifies it produces expected output. If any hook fails its health check, roll back that specific hook and report the failure.

4. **Consider making hooks read-only to the sync engine**. Hooks are the most dangerous files to auto-update because a broken hook blocks ALL agent operations. Instead, sync should flag "hook update available" and require manual confirmation.

---

## FLAW 8: The Spec-Gate Has a Categorical Bypass via Path Manipulation

### The Flaw

The spec-gate hook (`spec-gate.sh`, lines 29-37) determines whether a file is "code" by checking if the path contains any of these strings:

```bash
CODE_DIRS=("Code/" "code/" "src/" "lib/" "app/" "packages/")
```

This is a substring match using `grep -q "$dir"`. An agent that wants to write code before specs are frozen can:

1. Write to `scripts/` (not in the list)
2. Write to `utils/` (not in the list)
3. Write to `server/` (not in the list)
4. Write to `functions/` (not in the list)
5. Write to any project-specific directory that wasn't anticipated

More subtly, the substring match means `Code/` also matches paths like `docs/SourceCode/examples.md` or `NotCode/file.py` -- false positives that block legitimate documentation work.

The Engineering Spec template includes categories like "Infrastructure Configuration" and "External API Contracts" that might naturally live in directories like `infra/` or `api/` -- none of which are gated.

### Why It Matters

The spec-gate is presented as a hard enforcement mechanism: "Blocks code file writes until 4 required specs are FROZEN." In reality, it blocks writes to six specific directory name patterns. Any project that uses a non-standard directory structure (which many frameworks dictate -- Next.js uses `pages/`, Django uses the project name as a directory, Go uses the module path) gets zero code gating.

This is not a minor configuration issue; it's a fundamental design assumption that projects will always organize code into one of six directory names. The spec-gate is effectively a convention check disguised as an enforcement mechanism.

### Suggested Alternative

1. **Invert the logic**: Instead of listing code directories, list **non-code directories** (Specs/, Testing/, WorkOrders/, Sessions/, Notes/, etc.) that are always allowed. Everything else is gated. This is the allowlist approach, which is inherently safer than the denylist approach.

2. **Add a project-level configuration for code directories**. In CLAUDE.md or a dedicated config file, let the project declare its code directories:
   ```markdown
   ## Code Directories (spec-gated)
   - Code/
   - pages/
   - api/
   - server/
   ```

3. **Use file extension matching as a secondary check**. If the file has a code extension (`.py`, `.js`, `.ts`, `.kt`, `.java`, `.go`, `.rs`, etc.), treat it as code regardless of directory. This catches code files that land in unexpected directories.

---

## FLAW 9: The System Has No Concept of Partial Freeze or Progressive Specification

### The Flaw

The entire spec lifecycle is binary: DRAFT or FROZEN. The spec-gate requires all four specs (PVD, Engineering Spec, Blueprint, Testing Plans) to be FROZEN before any code can be written. This is all-or-nothing.

In practice, software projects rarely have the luxury of fully specifying everything before writing any code. Common scenarios that this model cannot handle:

1. **Prototyping**: "I want to write a proof-of-concept for Module X to validate the approach before freezing the Engineering Spec." The system blocks this entirely.

2. **Partial implementation**: PVD-1 through PVD-3 are fully specified, but PVD-4 through PVD-8 are still in draft. The team should be able to start implementing PVD-1 while PVD-4 is still being specified. The current system requires ALL features to be in a FROZEN document before ANY code is written.

3. **Technical spikes**: "We need to write code to understand the technical constraints before we can finish the Engineering Spec." This is explicitly forbidden by the system, but it's a legitimate and common engineering practice.

4. **Framework setup**: Creating the project skeleton (build system, CI config, dependency manifests) is "code" that should happen before specs are frozen. It's infrastructure, not feature code, but the spec-gate doesn't distinguish.

### Why It Matters

The all-or-nothing freeze model assumes a waterfall-like specification process. While the SDD framework is philosophically correct (specs before code prevents drift), the binary enforcement means teams face a choice: (a) fully specify everything before writing a single line of code (slow, sometimes impossible without prototyping), or (b) find workarounds to bypass the spec-gate (writing to non-gated directories, marking specs as FROZEN prematurely).

Option (b) is the more likely outcome, and it's worse than not having the gate at all. Prematurely frozen specs create false confidence and make the formal revision process (which requires Nathan's approval) a bottleneck for spec corrections that should be routine during early development.

### Suggested Alternative

1. **Add a LOCKED status between DRAFT and FROZEN**. LOCKED means "approved for implementation but may still have minor revisions." FROZEN means "immutable, changes require formal revision." The spec-gate should accept LOCKED or FROZEN.

2. **Feature-scoped code gating instead of project-scoped**. If PVD-1 has a frozen ES-1.x and BP-1.x.x, allow code writes to the ES-1.x modules even if PVD-4's specs are still in draft. This requires the spec-gate to understand which module the code file belongs to -- harder to implement but much more practical.

3. **Add an explicit prototype/spike escape hatch**. A `Code/_prototypes/` or `Code/_spikes/` directory that is exempt from spec-gate but is blocked from production builds. This gives agents a place to experiment without bypassing governance.

4. **Allow Nathan to manually override the spec-gate per-session** with a recorded decision. A command like `/spec-gate override "prototyping database layer per Nathan's direction"` that logs the override in the Decision Record and allows code writes for the current session.

---

## FLAW 10: No Governance of the Governance Layer Itself

### The Flaw

The system meticulously governs spec documents, code files, and work orders. But it has no governance over its own infrastructure:

- **Who validates `settings.json`?** A typo in the hook matcher regex (`"Edit|Writ"` instead of `"Edit|Write"`) silently disables protection for all Write operations. No hook validates the hook configuration.

- **Who validates the hook scripts?** A syntax error in `spec-gate.sh` causes it to fail with a non-zero exit code on every invocation. Depending on how Claude Code interprets this, it either blocks ALL code writes (treating the error as a block signal) or allows ALL code writes (treating the crash as a non-block).

- **Who validates the rules files?** The `.claude/rules/` directory contains markdown files with `<!-- AGENT INSTRUCTION: ... -->` comments. If a rule file is corrupted or incomplete, there is no mechanism to detect this. The agent simply operates without that rule.

- **Who validates the skills?** A SKILL.md with incorrect frontmatter (wrong `name`, missing `description`) may fail to register with Claude Code. There is no health check that verifies all 13 skills are loadable.

- **The CLAUDE.md itself is unvalidated.** It claims to list 13 skills, but if the actual `.claude/skills/` directory has 12 (or 14), nobody notices the discrepancy.

### Why It Matters

This is a meta-governance gap. The system is designed to prevent drift in project artifacts but has no mechanism to detect drift in its own infrastructure. Over time, as hooks are updated, rules are modified, and skills are added, the governance layer itself will accumulate the same kinds of inconsistencies it was designed to prevent in project code.

The most dangerous scenario: a hook that silently fails. `spec-gate.sh` depends on `python "$HOOK_DIR/parse_hook_input.py"` to extract the file path. If Python is not in the PATH (which can happen on Windows after a Python update or in certain terminal configurations), `parse_hook_input.py` fails, `FILE_PATH` is empty, and the hook exits 0 (allow). The spec-gate is silently disabled. The agent writes code freely. The Work Ledger still says "CLEAN." Nobody knows governance is broken until the damage is done.

### Suggested Alternative

1. **Add a `/governance-health` skill** (or extend `/trace-check`) that validates the governance layer itself:
   - All hooks in `settings.json` reference existing files
   - All hook scripts execute without error on test input
   - All skills in `.claude/skills/` have valid SKILL.md frontmatter
   - The skill table in CLAUDE.md matches the actual skills directory
   - Python is available and `parse_hook_input.py` works
   - All rule files in `.claude/rules/` are parseable

2. **Add a self-test to session-start.sh** that runs each hook with dummy input and verifies expected output. If any hook fails, warn the agent before it starts work.

3. **Version-pin the governance infrastructure**. Create a manifest of governance files with checksums. On session start, verify the checksums match. If they don't, something changed outside of normal governance -- flag it.

---

## SUMMARY OF FUNDAMENTAL ARCHITECTURAL CONCERNS

| # | Flaw | Severity | Root Cause |
|---|------|----------|------------|
| 1 | Enforcement is advisory, not mechanistic | HIGH | Hooks are AI suggestions, not OS barriers |
| 2 | FROZEN detection is fragile and inconsistent | HIGH | String matching instead of structured markers |
| 3 | Traceability validates structure, not semantics | MEDIUM | IDs are numerical conventions without content binding |
| 4 | Session hooks are context budget time bombs | HIGH | Full file dumps scale with project size |
| 5 | No template versioning or integrity verification | HIGH | Copy-based distribution with no origin tracking |
| 6 | Section-level markdown merge is unsound | HIGH | Markdown is not a structured data format |
| 7 | Bootstrap/circular dependency in sync | MEDIUM | Sync engine updates its own enforcement layer |
| 8 | Spec-gate uses denylist instead of allowlist | MEDIUM | Hardcoded directory names miss non-standard layouts |
| 9 | Binary DRAFT/FROZEN prevents practical workflows | MEDIUM | All-or-nothing model assumes waterfall specification |
| 10 | No governance of the governance layer | HIGH | Meta-validation gap -- who watches the watchmen? |

### The Deepest Issue

The system's fundamental tension is between **deterministic enforcement** and **advisory guidance for AI agents**. The hooks, rules, and skills are all advisory -- they depend on an AI agent choosing to comply. But the documentation, the terminology ("BLOCKED," "FROZEN," "LAW"), and the system's design philosophy all assume deterministic enforcement.

This gap between the system's claims and its actual capabilities is the deepest architectural flaw. It means Nathan believes his projects have stronger protections than they actually do. The fix is not to make the advisory system more aggressive -- it's to honestly architect the system with two layers: a thin, truly deterministic layer (file permissions, git hooks, OS-level protections) and a thick advisory layer (Claude Code hooks, rules, skills) that guides agents within the hard boundaries. The deterministic layer prevents catastrophic failures. The advisory layer prevents quality failures. Neither pretends to be the other.



================================================================================

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



================================================================================

# 06_redteam_sync_failures (agent-ad227ad88789806d6.jsonl)

## Message 1



I'll perform a thorough red team analysis of the Template Sync Engine. Let me first examine the actual implementation and all related files to ground my analysis in reality, not just the spec description.



================================================================================

# 07_unknown_agent (agent-acee81c62beed16f9.jsonl)

## Message 1

Perfect! Now let me create a comprehensive summary document with all the information I've gathered.

## Comprehensive Project Template Exploration Report

I've completed a thorough exploration of the Epoch Labs Project Template repository. Here's the complete inventory:

---

## FILE INVENTORY

### Root-Level Files
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\README.md** — Master documentation (v2.0, 2026-03-01)
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\CLAUDE.md** — Project constitution template with placeholders for project-specific customization
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.gitignore** — Standard gitignore for secrets, artifacts, and local builds
- **c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.mcp.json** — MCP server configuration (Context7 as default)

---

## .CLAUDE DIRECTORY STRUCTURE

### .claude/settings.json
```
Hook registrations for SessionStart and PreToolUse events:
- SessionStart hooks:
  - startup → runs session-start.sh (injects Work Ledger + Gap Tracker)
  - resume → runs session-resume.sh (lightweight re-anchor)
  - compact → runs session-compact.sh (full context recovery post-compaction)
- PreToolUse hooks:
  - Bash → block-dangerous.sh + pre-commit-reminder.sh
  - Edit|Write → protect-frozen-files.sh + spec-gate.sh
```

### .claude/settings.local.json.example
Example permissions template for per-machine overrides (gitignored in actual use).

### .claude/hooks/ Directory

**session-start.sh**
- Fires on fresh session start
- Outputs Work Ledger + Gap Tracker summary
- Shows next task and tier summaries
- Anti-drift mechanism ensuring re-anchoring to project status

**session-resume.sh**
- Fires when resuming previous conversations
- Lighter than startup — assumes conversation context exists
- Re-anchors to Work Ledger status and active Work Orders

**session-compact.sh**
- MOST CRITICAL hook — fires after context compaction
- Re-injects FULL project context
- Warns that pre-compaction memory is unreliable
- Dumps complete Work Ledger + Gap Tracker

**spec-gate.sh**
- PreToolUse hook preventing code writes without frozen specs
- Enforces "no code before specs" principle
- Checks for: PVD OR (Product Brief + PRD), Engineering Spec, Blueprint, Testing Plans
- All must be FROZEN before Code/ writes allowed

**protect-frozen-files.sh**
- Prevents modification of frozen spec files
- Maintains a FROZEN_PATTERNS list (commented by default)
- Scales as project adds specs

**block-dangerous.sh**
- Blocks destructive bash commands:
  - Destructive git: `git push --force`, `git reset --hard`, `git clean -f`, `git branch -D`
  - Mass deletion: `rm -rf /`, `rm -rf *`, `del /s /q`
  - Database destruction: `DROP TABLE`, `DELETE FROM` with no WHERE clause

**pre-commit-reminder.sh**
- Advisory hook reminding to run `/pre-commit` before git commit
- Also reminds to run `/trace-check` if spec files modified

**parse_hook_input.py**
- Utility for all hooks to extract fields from JSON input
- Normalizes Windows backslashes to forward slashes

### .claude/rules/ Directory

**spec-readiness.md** — Guides spec creation sequence, traceability ID system, UX Spec conditional inclusion

**change-control.md** — Scope change protocol, spec revision protocol, Work Order failure handling, Decision Record usage

**quality-gates.md** — Definition of Done (6 gates): no stubs, test coverage, no TODOs, no GPL deps, clean build, performance targets

**problem-solving.md** — 4-tier escalation (max 3 actions per tier): Read & Trace → Internal Resources → External Resources → Escalate to Nathan

**naming-conventions.md** — File naming standards enabling automation (specs use `{Abbrev}_{Topic}_v{N}.md`, code follows language conventions)

### .claude/skills/ Directory

**12 Production Skills + Examples/Scripts:**

1. **spec-lookup** — Load primary and supporting specs before working on a module
2. **code-review** — Post-implementation quality review (correctness, error handling, security, testing)
3. **alignment-check** — Verify code matches spec using grep-based evidence gathering
4. **dep-check** — Check license, security, maintenance of dependencies
5. **security-review** — OWASP-style audit (secrets, input validation, injection prevention, auth, data protection, error handling)
6. **integration-logic** — Verify cross-module wiring and contracts
7. **pre-commit** — Secrets scan, prohibited content, file hygiene, build/test verification
8. **module-complete** — Run all 6 quality gates before marking module done
9. **frontend-design** — Production-grade UI design with bold aesthetic direction
10. **webapp-testing** — Playwright-based web testing with server lifecycle
11. **trace-check** — Validate traceability chains, generate Work Ledger
12. **skill-creator** — Create new project-specific skills following Agent Skills SDK

**trace-check Supporting Files:**
- **scripts/validate_traceability.py** — Python validation engine (parses IDs, validates chains, checks frozen status, generates Work Ledger)

**webapp-testing Supporting Files:**
- **examples/console_logging.py** — Example: capturing browser console messages
- **examples/element_discovery.py** — Example: finding and interacting with elements
- **examples/static_html_automation.py** — Example: automating static HTML pages
- **scripts/with_server.py** — Server lifecycle management for testing

---

## SPECS/ DIRECTORY (Document Templates)

**9 Spec Templates Implementing Full SDD Stack:**

1. **TEMPLATE_PVD.md** — Product Vision Document (collaborative path: what + why)
   - Sections: Executive Summary, Vision & Mission, Problem Statement, Target Users, Product Overview, Feature Specs
   - Assigns PVD-N identifiers (root of traceability chains)
   - Status: FROZEN before proceeding

2. **TEMPLATE_Product_Brief.md** — Lightweight go/no-go gate (autonomous path)
   - Sections: Problem Hypothesis, Target User Sketch, Market Opportunity, Value Proposition, Key Risks, Go/No-Go Decision
   - Gate before PRD investment

3. **TEMPLATE_PRD.md** — Detailed Requirements (autonomous path, follows Brief approval)
   - References Product Brief
   - Assigns PVD-N identifiers (same as PVD path)
   - Feature specs with user stories and acceptance criteria

4. **TEMPLATE_Engineering_Spec.md** — Technical architecture (how to build)
   - Sections: System Architecture, Technology Stack, Module Dependency Graph, Database Schema, Module Specifications
   - Assigns ES-N.M identifiers (trace to PVD-N)
   - Frozen interface contracts

5. **TEMPLATE_UX_Spec.md** — User experience (UI projects only)
   - Sections: Design Principles, Screen Inventory, Navigation Flows, Component Library
   - Assigns UX-N.M identifiers (trace to PVD-N)
   - Describes all user-facing interactions

6. **TEMPLATE_Blueprint.md** — Agent-executable build plan
   - Sections: Build Principles, Dependency Graph, Phase/Wave Schedule, Task Cards
   - Assigns BP-N.M.T identifiers (trace to ES-N.M)
   - Task cards with acceptance criteria and complexity estimates
   - FROZEN — never modified during development

7. **TEMPLATE_Decision_Record.md** — Living log of significant decisions
   - LIVING document (continuously appended, never frozen)
   - Format: DR-NNN entries with Context, Decision, Alternatives Considered, Consequences
   - Prevents re-litigation of settled questions

8. **TEMPLATE_Work_Order.md** — Scoped assignment (carved from Blueprint)
   - Bundles build tasks + tests + acceptance criteria
   - Assigns WO-N.M.T-X identifiers (trace to BP-N.M.T)
   - Lifecycle: PENDING → IN-PROGRESS → VALIDATION → DONE/FAILED
   - Failed WOs archived, new attempt suffix increments (-A → -B)

9. **gap_tracker.md** — Tiered work tracking (Tier 0-3: Critical → Functional → Quality → Enhancement)
   - Single source of truth for "what needs doing and in what order"
   - Mandatory scope guards (don't work Tier 1 while Tier 0 open, etc.)
   - SessionStart hooks read this automatically

10. **Work_Ledger.md** — Auto-generated by `/trace-check` skill
    - Persistent project status snapshot
    - Sections: Spec Readiness, Traceability Chain, Active Work Orders, Progress
    - CLEAN or list of warnings/errors

---

## TESTING/ DIRECTORY

**TEMPLATE_Testing_Plans.md** — Per-module test cases
- Sections: Testing Philosophy & Pyramid, Test Infrastructure & Tools, Per-Module Unit Test Specs, Integration Test Scenarios
- Assigns TP-N.M.T identifiers (mirror BP-N.M.T)
- Every Blueprint task MUST have corresponding TP entry

---

## SESSIONS/ DIRECTORY

**SESSION_TEMPLATE.md** — Reusable session summary template
- Sections: What Was Accomplished, Key Decisions Made, Files Created/Modified, Bug Fixes, Open Questions, Next Steps
- Provides continuity across sessions
- SessionStart hooks surface these on resume

---

## WORKORDERS/ DIRECTORY

- **_Archive/** — Completed/failed Work Orders storage

---

## OTHER DIRECTORIES

- **Code/** — Source code (gated by spec-gate hook)
- **Testing/** — Test plans, QA documentation
- **Quality/** — Feature-level quality assessments
- **Patents/** — Patent briefs, IP documents
- **Processes/** — Project-specific process docs
- **Research/** — Research docs (git-ignored)
- **Notes/** — General notes
- **Investor/** — Investor materials
- **Guides/** — Advanced patterns reference
- **_Archive/** — Archived/superseded files
- **_shared/** — Junction to `_SharedCore` (cross-project shared specs)

---

## TRACEABILITY SYSTEM EXPLAINED

**Hierarchical ID chains ensuring all work traces back to product justification:**

```
PVD-3              → Feature #3 (product vision)
  ES-3.2           → Module #2 implementing PVD-3
    UX-3.2         → Screen/flow for PVD-3
    BP-3.2.4       → Task #4 of ES-3.2
      TP-3.2.4     → Tests for BP-3.2.4 (mirror)
        WO-3.2.4-A → Work Order attempt A
```

**Validation chain:** `/trace-check` validates that:
- PVD features have corresponding ES modules
- ES modules have corresponding BP tasks
- BP tasks have corresponding TP test specs
- WO status tracks execution progress
- No orphan IDs or broken chains

---

## KEY PRINCIPLES & GOVERNANCE

### Gold Rush Doctrine (Immutable)
- No stubs or placeholders
- "What ships is finished, what isn't finished doesn't ship"
- Ship complete features, not complete products
- Quality bar must match or exceed best existing alternative

### Anti-Patterns (NEVER DO)
- No stubs or fake implementations
- No code before frozen specs
- No hardcoded API keys
- No HTTP (TLS everywhere)
- No GPL dependencies (Apache 2.0, MIT, BSD only)
- No TODO/FIXME in shipped code

### Safety Rules
- NEVER delete files (archive to `_Archive/` instead)
- NEVER overwrite without asking
- NEVER commit secrets
- Ask before structural changes

---

## GIT STRATEGY

- **main** — Production-ready releases only
- **dev** — Active development (default working branch)
- **feature branches** — Isolated work, merge to dev

---

## INITIALIZATION STEPS FOR NEW PROJECT

1. Copy entire template folder to `C:\Claude Folder\{YourProjectName}\`
2. Customize `CLAUDE.md` (replace all `{placeholders}`)
3. Create `_shared` junction: `mklink /J _shared C:\Claude Folder\_SharedCore`
4. Initialize git: `git init`, create `main` and `dev` branches
5. Start speccing: copy templates from `Specs/TEMPLATE_*.md`, begin with PVD

---

## ADVANCED PATTERNS (OPTIONAL)

Documented in **Guides/advanced_patterns.md**:

1. **Nested CLAUDE.md Assembly** — Project-wide rules + layer-specific rules for complex projects
2. **Structured Acceptance Criteria** — Verification methods for precise acceptance definitions
3. **Skills Discovery** — Installing additional Anthropic official skills and community skills

---

## CROSS-PROJECT RESOURCES

These live outside this template (in parent directories):

- **_SharedCore/** — Cross-project shared specs, schemas, security foundations
- **_Processes/** — Global skills and process library
- **_TaskQueue/** — Task briefs for future sessions
- **_IP_Pipeline/** — Patent brief queue
- **Memory/** — SQLite memory database (`claude_memory.db`) with `document_index`, `local_sessions`, `project_context` tables

---

## ABSOLUTE PATHS TO ALL KEY FILES

**Configuration & Documentation:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\README.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\CLAUDE.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.gitignore`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.mcp.json`

**Settings:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\settings.json`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\settings.local.json.example`

**Hooks (8 files):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\session-start.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\session-resume.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\session-compact.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\spec-gate.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\protect-frozen-files.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\block-dangerous.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\pre-commit-reminder.sh`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\hooks\parse_hook_input.py`

**Rules (5 files):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\spec-readiness.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\change-control.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\quality-gates.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\problem-solving.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\rules\naming-conventions.md`

**Skills (12 + supporting):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\spec-lookup\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\code-review\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\alignment-check\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\dep-check\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\security-review\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\integration-logic\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\pre-commit\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\module-complete\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\frontend-design\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\trace-check\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\skill-creator\SKILL.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\trace-check\scripts\validate_traceability.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\examples\console_logging.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\examples\element_discovery.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\examples\static_html_automation.py`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\.claude\skills\webapp-testing\scripts\with_server.py`

**Spec Templates (9 files):**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_PVD.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Product_Brief.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_PRD.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Engineering_Spec.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_UX_Spec.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Blueprint.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Decision_Record.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\TEMPLATE_Work_Order.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\gap_tracker.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Specs\Work_Ledger.md`

**Testing & Sessions:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Testing\TEMPLATE_Testing_Plans.md`
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Sessions\SESSION_TEMPLATE.md`

**Guides:**
- `c:\Claude Folder\Epoch_Labs\Epoch Labs Project Template\_ProjectTemplate\Guides\advanced_patterns.md`

---

This is a complete, production-ready template for building projects using Spec-Driven Development (SDD) with AI agents as primary implementers. Every system has been architected to prevent drift, enforce quality gates, maintain traceability, and ensure that only complete, finished features ship.



================================================================================

