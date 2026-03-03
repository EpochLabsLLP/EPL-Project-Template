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

