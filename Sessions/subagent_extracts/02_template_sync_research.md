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

