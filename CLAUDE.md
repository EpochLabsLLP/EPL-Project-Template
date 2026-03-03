# Project Governance Workshop

## Purpose
This is the development workshop for the **EPL Project Template** — an SDD governance framework for AI-assisted software development.

The template product lives in `template/` (git subtree → `EpochLabsLLP/EPL-Project-Template`).
This workshop is where we design, build, test, and improve the template.

## Architecture

```
Workshop (this repo)
  template/          ← git subtree of the product (EPL-Project-Template)
  Sessions/          ← development session notes
  Specs/             ← workshop-level specs and tracking
  .mcp.json          ← MCP server config for development tools
```

## Working with the Template Subtree

### Edit template files
Edit files directly under `template/`. Commit normally in this repo.

### Push changes to the template repo
```bash
git subtree push --prefix=template template-remote main
```

### Pull changes from the template repo (if edited directly)
```bash
git subtree pull --prefix=template template-remote main
```

### Tag a template release
Push to the template remote, then tag in that repo.

## Test Project Workflow

The EPL Test Project (`EpochLabsLLP/EPL-Test-Project`) is a standalone repo for validating the template. To test changes:

1. Edit template files in `template/`
2. Push to the template remote: `git subtree push --prefix=template template-remote main`
3. In the test project, run `template_sync.py` to pull updates
4. Exercise the governance system in the test project
5. Record findings back here in `Sessions/`

## Workshop Conventions
- Session notes go in `Sessions/YYYY-MM-DD_session_{topic}.md`
- No formal SDD governance on this repo (that's the product, not the workshop)
- Commit freely, iterate fast
- The template product has its own versioning (`.template_version` inside `template/`)
