<!-- AGENT INSTRUCTION: This file documents advanced patterns available to projects
     built from this template. These are OPTIONAL — use them when the project's
     complexity warrants it. Read this file when setting up a new project to
     decide which patterns to adopt. -->

# Advanced Patterns Reference

These patterns were harvested from mature Epoch Labs projects. They are not required for every project — adopt them when the problem they solve is relevant to your project.

---

## 1. Nested CLAUDE.md Assembly (7-Layer Pattern)

**Source:** EPOE
**When to use:** Projects with deep directory structures where different areas need different rules (e.g., multi-module monorepos, projects with distinct backend/frontend/mobile layers).

### How It Works

Claude Code natively loads CLAUDE.md files from every ancestor directory when you work in a subdirectory. This is built-in behavior, not something you configure.

```
ProjectName/
  CLAUDE.md                         ← Always loaded (project constitution)
  Code/
    CLAUDE.md                       ← Loaded when working in Code/
    src/
      CLAUDE.md                     ← Loaded when working in src/
      auth/
        CLAUDE.md                   ← Loaded when working in auth/
      payments/
        CLAUDE.md                   ← Loaded when working in payments/
```

### What Goes Where

| Level | Content | Example |
|-------|---------|---------|
| Root `CLAUDE.md` | Project-wide rules, architecture decisions, anti-patterns | "No GPL dependencies", "TLS everywhere" |
| `Code/CLAUDE.md` | Tech stack conventions, build commands, import patterns | "Use Kotlin coroutines for async, not RxJava" |
| `src/CLAUDE.md` | Source-specific patterns, shared utilities | "All services extend BaseService" |
| `src/auth/CLAUDE.md` | Module-specific rules, security requirements | "All endpoints require JWT validation" |

### Rules for Nested CLAUDE.md Files

- **Keep them short.** Each nested file should be 10-30 lines. They add to context budget.
- **Don't repeat the root.** Nested files add specificity, not redundancy.
- **Use them for constraints, not tutorials.** "Always use parameterized queries in this module" — not "here's how SQL works."
- **Consider `.claude/rules/` first.** Path-scoped rules files (`/.claude/rules/auth.md` with path scope `src/auth/`) achieve the same effect without files scattered through the source tree. Prefer rules files for most cases.

### When NOT to Use This Pattern

- Small projects with <5 source directories
- Projects where all modules follow the same conventions
- When `.claude/rules/` path scoping covers your needs

---

## 2. Structured Acceptance Criteria

**Source:** EPOE
**When to use:** Projects where "is this module done?" requires more precision than a checklist. Particularly valuable when multiple people (or Claude instances across sessions) need to agree on what "done" means.

### The Problem

Loose acceptance criteria like this are ambiguous:

```markdown
## Acceptance Criteria
- User can log in
- Errors are handled
- Tests pass
```

"User can log in" — via what method? With what error messages? What happens on failure? Each Claude instance (or session) interprets this differently, causing drift.

### The Pattern

Replace loose strings with structured criteria that specify the verification method:

```markdown
## Acceptance Criteria

| # | Criterion | Type | Verification |
|---|-----------|------|--------------|
| 1 | User can authenticate via email/password | Functional | Unit test: `auth.test.ts::testEmailLogin` passes |
| 2 | Invalid credentials return 401 with error message | Functional | Unit test: `auth.test.ts::testInvalidCredentials` passes |
| 3 | Login endpoint responds in <200ms | Performance | Load test: p95 latency <200ms at 100 req/s |
| 4 | No credentials stored in browser localStorage | Security | `/security-review auth` passes with no CRITICAL/HIGH findings |
| 5 | Failed logins are rate-limited to 5/minute | Security | Unit test: `auth.test.ts::testRateLimiting` passes |
```

### Criterion Types

| Type | What It Means | How to Verify |
|------|---------------|---------------|
| **Functional** | The feature works as specified | Unit/integration test passes |
| **Performance** | Meets speed/throughput targets | Benchmark or load test |
| **Security** | No vulnerabilities introduced | `/security-review` skill passes |
| **Integration** | Works correctly with other modules | `/integration-logic` skill passes |
| **UX** | User experience meets design spec | Manual review or screenshot comparison |

### Where to Put Them

Structured criteria belong in:
- **Mission Lock** (`/.claude/rules/mission-lock.md`) — for phase-level success criteria
- **Engineering Spec** — for module-level acceptance criteria
- **Gap Tracker** — for individual work items that need precise definition

### Integration with Quality Gates

The `/module-complete` skill already checks 6 quality gates. Structured acceptance criteria extend this by defining project-specific criteria beyond the universal gates. When a module has structured criteria in the Engineering Spec, `/module-complete` should verify those in addition to the standard 6 gates.

---

## 3. Skills Discovery — Finding and Installing Additional Skills

**When to use:** When a project needs capabilities beyond the 12 base skills bundled with this template.

### Anthropic's Official Skills Repository

**URL:** https://github.com/anthropics/skills
**Standard:** https://agentskills.io (open standard, supported by Claude Code, Cursor, GitHub Copilot, Gemini CLI, and others)

Anthropic maintains a repository of official skills. These can be installed via the plugin marketplace:

```
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
/plugin install document-skills@anthropic-agent-skills
```

### Recommended Skills by Project Type

| Project Type | Skill | What It Does | Install |
|-------------|-------|-------------|---------|
| **Any with docs** | doc-coauthoring | 3-stage collaborative documentation workflow (context gathering, refinement, reader testing) | `/plugin install example-skills@anthropic-agent-skills` |
| **Web apps** | webapp-testing | Playwright-based testing with server lifecycle management and screenshots | `/plugin install example-skills@anthropic-agent-skills` |
| **MCP development** | mcp-builder | 4-phase guide for creating MCP servers (research, implement, review, eval) | `/plugin install example-skills@anthropic-agent-skills` |
| **Office docs** | pdf, docx, pptx, xlsx | Create, read, edit Office documents and PDFs | `/plugin install document-skills@anthropic-agent-skills` |
| **HTML artifacts** | web-artifacts-builder | Multi-component HTML with React 18 + TypeScript + Vite + Tailwind | `/plugin install example-skills@anthropic-agent-skills` |
| **Generative art** | algorithmic-art | p5.js generative art with seeded randomness and interactive controls | `/plugin install example-skills@anthropic-agent-skills` |

### Community Skills Repositories

These community repositories contain additional skills and Claude Code configurations:

- **Awesome Claude Skills** — https://github.com/travisvn/awesome-claude-skills
  Curated list of community-contributed skills across many domains.

- **Awesome Claude Code** — https://github.com/hesreallyhim/awesome-claude-code
  Broader resource covering Claude Code configurations, CLAUDE.md examples, and skills.

### Creating Project-Specific Skills

Use the bundled `/skill-creator` skill to create new skills following the Agent Skills SDK format. Every skill created this way will be compatible with Claude Code, Cursor, and other tools that support the agentskills.io standard.

### Skill Format Quick Reference

Skills follow the Agent Skills SDK standard. Minimum structure:

```
skill-name/
└── SKILL.md          # Required — YAML frontmatter + markdown instructions
```

SKILL.md format:
```yaml
---
name: skill-name
description: What the skill does and when to use it. Max 1024 chars.
---

# Skill Title

[Markdown instructions for Claude to follow]
```

Validation rules:
- `name`: kebab-case only (`[a-z0-9-]+`), max 64 chars, must match directory name
- `description`: max 1024 chars, no angle brackets
- Optional fields: `argument-hint`, `license`, `compatibility`, `disable-model-invocation`, `user-invocable`

Full specification: https://agentskills.io/specification
