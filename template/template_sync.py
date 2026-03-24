"""Template Sync Engine — Compare template repo against active projects.

Usage:
    python template_sync.py <template_dir> <project_dir>             # Dry-run report
    python template_sync.py <template_dir> <project_dir> --apply     # Apply changes
    python template_sync.py <template_dir> <project_dir> --backup-dir <path>

Categories (from TEMPLATE_MANIFEST.json):
    infrastructure        — Template-owned. Always overwritten on sync.
    template              — Reference files. Always overwritten on sync.
    scaffolding           — Created once. Project-owned after. Never overwritten.
    managed_scaffolding   — Project-owned but hooks and marketplace blocks are merged from template.
    generated             — Auto-generated. Skipped entirely.

Safety: Never deletes files. Never modifies scaffolding. Always backs up before overwriting.
"""
import sys
import os
import json
import hashlib
import re
import shutil
import glob as globmod
from datetime import datetime


TEXT_EXTENSIONS = {
    ".sh", ".py", ".md", ".json", ".txt", ".yml", ".yaml",
    ".toml", ".cfg", ".ini", ".gitattributes", ".gitignore",
    ".env", ".example", ".csv", ".html", ".css", ".js", ".ts",
    ".jsx", ".tsx", ".xml", ".svg",
}

# Files with no extension that should also be normalized
TEXT_FILENAMES = {".gitattributes", ".gitignore", ".editorconfig"}


def _is_text_file(path):
    """Check if a file should have LF line endings enforced."""
    basename = os.path.basename(path).lower()
    if basename in TEXT_FILENAMES:
        return True
    _, ext = os.path.splitext(path)
    return ext.lower() in TEXT_EXTENSIONS


def copy_with_lf(src, dst):
    """Copy file, normalizing CRLF→LF for all text files.

    Ensures scripts and configs work on macOS/Linux even when the source
    working tree has CRLF (Windows core.autocrlf=true, Syncthing sync).
    Binary files are copied unchanged.
    """
    if _is_text_file(src):
        with open(src, "rb") as f:
            content = f.read()
        content = content.replace(b"\r\n", b"\n")
        with open(dst, "wb") as f:
            f.write(content)
        shutil.copystat(src, dst)
    else:
        shutil.copy2(src, dst)


def file_hash(path):
    """SHA-256 hash of file contents, normalized for all text files.

    For text files, CRLF is stripped before hashing so that a
    CRLF source and an LF dest are correctly detected as identical
    (or drifted for content-only differences, not line endings).
    """
    try:
        with open(path, "rb") as f:
            content = f.read()
        if _is_text_file(path):
            content = content.replace(b"\r\n", b"\n")
        return hashlib.sha256(content).hexdigest()
    except (OSError, IOError):
        return None


def resolve_glob(pattern, base_dir):
    """Resolve a glob pattern relative to base_dir. Returns list of relative paths."""
    full_pattern = os.path.join(base_dir, pattern.replace("/", os.sep))
    matches = globmod.glob(full_pattern)
    results = []
    for m in matches:
        rel = os.path.relpath(m, base_dir).replace(os.sep, "/")
        results.append(rel)
    return results


def load_manifest(template_dir):
    """Load TEMPLATE_MANIFEST.json from template directory."""
    manifest_path = os.path.join(template_dir, "TEMPLATE_MANIFEST.json")
    if not os.path.isfile(manifest_path):
        print(f"ERROR: TEMPLATE_MANIFEST.json not found in {template_dir}")
        sys.exit(1)
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_project_version(project_dir):
    """Load .template_version from project, or return '0.0.0' if missing."""
    version_path = os.path.join(project_dir, ".template_version")
    if os.path.isfile(version_path):
        with open(version_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.0.0"


def check_claude_md_version(project_dir, manifest):
    """Check if project CLAUDE.md structure matches template expectation.

    Returns:
        (project_version, template_version, needs_migration)
        - project_version: str or None (None if no marker found)
        - template_version: str or None (None if manifest predates this feature)
        - needs_migration: bool
    """
    expected = manifest.get("claude_md_structure_version", None)
    if expected is None:
        return (None, None, False)  # Template predates this feature

    claude_md_path = os.path.join(project_dir, "CLAUDE.md")
    if not os.path.isfile(claude_md_path):
        return (None, expected, True)  # No CLAUDE.md at all

    # Scan first 10 lines for version marker
    project_version = None
    try:
        with open(claude_md_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                match = re.search(r'<!-- claude_md_version: (\S+) -->', line)
                if match:
                    project_version = match.group(1)
                    break
    except (OSError, IOError):
        return (None, expected, True)

    if project_version is None:
        return (None, expected, True)  # Legacy CLAUDE.md, no marker

    needs_migration = project_version != expected
    return (project_version, expected, needs_migration)


def merge_settings_json(project_dir, manifest):
    """Merge template registrations into project settings.json.

    Preserves all existing project keys (permissions, custom hooks, custom plugins).
    Merges hooks from hook_registrations and marketplaces/plugins from
    marketplace_registrations. Both are additive only — never removes project entries.

    Returns:
        (changes, merged_settings)
        - changes: list of strings describing what would change
        - merged_settings: the merged dict (or None if no changes needed)
    """
    hook_regs = manifest.get("hook_registrations", None)
    if not hook_regs:
        return ([], None)

    settings_path = os.path.join(project_dir, ".claude", "settings.json")
    if os.path.isfile(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                project_settings = json.load(f)
        except (json.JSONDecodeError, OSError, IOError) as e:
            return ([f"ERROR: Could not parse settings.json — {e}"], None)
    else:
        project_settings = {}

    changes = []
    modified = False

    # Ensure hooks key exists
    if "hooks" not in project_settings:
        project_settings["hooks"] = {}
        modified = True

    proj_hooks = project_settings["hooks"]

    for event_type, template_matchers in hook_regs.items():
        # Ensure event type exists in project
        if event_type not in proj_hooks:
            proj_hooks[event_type] = []

        for tmpl_matcher_entry in template_matchers:
            tmpl_matcher = tmpl_matcher_entry["matcher"]
            tmpl_hook_list = tmpl_matcher_entry["hooks"]

            # Find matching entry in project by matcher string
            proj_matcher_entry = None
            for entry in proj_hooks[event_type]:
                if entry.get("matcher") == tmpl_matcher:
                    proj_matcher_entry = entry
                    break

            if proj_matcher_entry is None:
                # No matching entry — add the entire block
                proj_hooks[event_type].append(tmpl_matcher_entry)
                hook_names = [h["command"].split("/")[-1].rstrip('"') for h in tmpl_hook_list]
                changes.append(f"+ {event_type}/{tmpl_matcher}: adding matcher block ({', '.join(hook_names)})")
                modified = True
                continue

            # Matcher exists — merge hooks by command identity
            proj_hook_list = proj_matcher_entry.get("hooks", [])
            proj_commands = {h["command"]: h for h in proj_hook_list}

            for tmpl_hook in tmpl_hook_list:
                tmpl_cmd = tmpl_hook["command"]
                hook_name = tmpl_cmd.split("/")[-1].rstrip('"')

                if tmpl_cmd not in proj_commands:
                    # Hook not present — add it
                    proj_hook_list.append(tmpl_hook)
                    changes.append(f"+ {event_type}/{tmpl_matcher}: adding {hook_name}")
                    modified = True
                else:
                    # Hook exists — check if timeout needs updating
                    proj_h = proj_commands[tmpl_cmd]
                    if proj_h.get("timeout") != tmpl_hook.get("timeout"):
                        old_t = proj_h.get("timeout", "none")
                        new_t = tmpl_hook.get("timeout", "none")
                        proj_h["timeout"] = tmpl_hook["timeout"]
                        changes.append(f"~ {event_type}/{tmpl_matcher}: {hook_name} timeout {old_t} -> {new_t}")
                        modified = True

            proj_matcher_entry["hooks"] = proj_hook_list

    # Merge marketplace registrations (additive only, same philosophy as hooks)
    marketplace_regs = manifest.get("marketplace_registrations", None)
    if marketplace_regs:
        # Merge extraKnownMarketplaces
        tmpl_marketplaces = marketplace_regs.get("extraKnownMarketplaces", {})
        if tmpl_marketplaces:
            if "extraKnownMarketplaces" not in project_settings:
                project_settings["extraKnownMarketplaces"] = {}
            proj_marketplaces = project_settings["extraKnownMarketplaces"]
            for name, config in tmpl_marketplaces.items():
                if name not in proj_marketplaces:
                    proj_marketplaces[name] = config
                    changes.append(f"+ marketplace: adding {name}")
                    modified = True

        # Merge enabledPlugins
        tmpl_plugins = marketplace_regs.get("enabledPlugins", {})
        if tmpl_plugins:
            if "enabledPlugins" not in project_settings:
                project_settings["enabledPlugins"] = {}
            proj_plugins = project_settings["enabledPlugins"]
            for plugin_name, enabled in tmpl_plugins.items():
                if plugin_name not in proj_plugins:
                    proj_plugins[plugin_name] = enabled
                    changes.append(f"+ plugin: enabling {plugin_name}")
                    modified = True

    if not modified:
        return (["= settings.json: up to date"], None)

    return (changes, project_settings)


def expand_files(file_patterns, base_dir):
    """Expand a list of file patterns (may contain globs) to concrete relative paths."""
    results = []
    for pattern in file_patterns:
        if "*" in pattern:
            results.extend(resolve_glob(pattern, base_dir))
        else:
            results.append(pattern)
    return results


def sync_report(template_dir, project_dir, manifest):
    """Generate sync report comparing template to project.

    Returns dict with keys:
        updated  — files that differ and would be overwritten (infrastructure/template)
        created  — files missing from project that would be created
        skipped  — scaffolding files that exist in project (project-owned)
        missing  — expected directories not found
        drifted  — infrastructure/template files modified in project
        current  — files that are identical (no action needed)
        generated_skip — generated files (always skipped)
    """
    report = {
        "updated": [],
        "created": [],
        "skipped": [],
        "missing_dirs": [],
        "drifted": [],
        "current": [],
        "generated_skip": [],
    }

    # Check directories
    for d in manifest.get("directories", []):
        dir_path = os.path.join(project_dir, d.rstrip("/"))
        if not os.path.isdir(dir_path):
            report["missing_dirs"].append(d)

    # Process each category
    for category_name, category_data in manifest.get("categories", {}).items():
        file_patterns = category_data.get("files", [])
        template_files = expand_files(file_patterns, template_dir)

        for rel_path in template_files:
            template_file = os.path.join(template_dir, rel_path.replace("/", os.sep))
            project_file = os.path.join(project_dir, rel_path.replace("/", os.sep))

            if not os.path.isfile(template_file):
                continue  # Pattern matched nothing in template

            project_exists = os.path.isfile(project_file)

            if category_name == "generated":
                report["generated_skip"].append(rel_path)
                continue

            if category_name in ("scaffolding", "managed_scaffolding"):
                if project_exists:
                    report["skipped"].append(rel_path)
                else:
                    report["created"].append((rel_path, category_name))
                continue

            # infrastructure or template — compare and potentially overwrite
            if not project_exists:
                report["created"].append((rel_path, category_name))
            else:
                t_hash = file_hash(template_file)
                p_hash = file_hash(project_file)
                if t_hash == p_hash:
                    report["current"].append(rel_path)
                else:
                    report["drifted"].append(rel_path)
                    report["updated"].append((rel_path, category_name))

    return report


def apply_sync(template_dir, project_dir, report, backup_dir, template_version,
               merged_settings=None):
    """Apply sync changes based on report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if backup_dir is None:
        backup_dir = os.path.join(project_dir, ".template_backup", timestamp)

    applied = []
    errors = []

    # Create missing directories
    for d in report["missing_dirs"]:
        dir_path = os.path.join(project_dir, d.rstrip("/"))
        try:
            os.makedirs(dir_path, exist_ok=True)
            applied.append(f"MKDIR: {d}")
        except OSError as e:
            errors.append(f"MKDIR FAILED: {d} — {e}")

    # Create missing files
    for rel_path, category in report["created"]:
        src = os.path.join(template_dir, rel_path.replace("/", os.sep))
        dst = os.path.join(project_dir, rel_path.replace("/", os.sep))
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            copy_with_lf(src, dst)
            applied.append(f"CREATED: {rel_path} ({category})")
        except (OSError, IOError) as e:
            errors.append(f"CREATE FAILED: {rel_path} — {e}")

    # Overwrite drifted infrastructure/template files
    for rel_path, category in report["updated"]:
        src = os.path.join(template_dir, rel_path.replace("/", os.sep))
        dst = os.path.join(project_dir, rel_path.replace("/", os.sep))
        bak = os.path.join(backup_dir, rel_path.replace("/", os.sep))
        try:
            # Backup first
            os.makedirs(os.path.dirname(bak), exist_ok=True)
            shutil.copy2(dst, bak)
            # Then overwrite (LF-normalized for scripts)
            copy_with_lf(src, dst)
            applied.append(f"UPDATED: {rel_path} ({category}, backup at {os.path.relpath(bak, project_dir)})")
        except (OSError, IOError) as e:
            errors.append(f"UPDATE FAILED: {rel_path} — {e}")

    # Write .template_version
    version_path = os.path.join(project_dir, ".template_version")
    try:
        with open(version_path, "w", encoding="utf-8") as f:
            f.write(template_version + "\n")
        applied.append(f"VERSION: Updated .template_version to {template_version}")
    except (OSError, IOError) as e:
        errors.append(f"VERSION UPDATE FAILED: {e}")

    # Post-apply LF enforcement sweep — fix any text files in the project that
    # still have CRLF, regardless of whether they were "up to date" by hash.
    # This catches files that matched content-wise but had CRLF in the project copy.
    all_managed_files = set()
    for category_name, category_data in load_manifest(template_dir).get("categories", {}).items():
        if category_name in ("generated", "scaffolding", "managed_scaffolding"):
            continue
        for rel_path in expand_files(category_data.get("files", []), template_dir):
            all_managed_files.add(rel_path)

    lf_fixed = 0
    for rel_path in all_managed_files:
        dst = os.path.join(project_dir, rel_path.replace("/", os.sep))
        if os.path.isfile(dst) and _is_text_file(dst):
            try:
                with open(dst, "rb") as f:
                    content = f.read()
                if b"\r\n" in content:
                    content = content.replace(b"\r\n", b"\n")
                    with open(dst, "wb") as f:
                        f.write(content)
                    lf_fixed += 1
            except (OSError, IOError):
                pass
    if lf_fixed > 0:
        applied.append(f"LF ENFORCED: Normalized {lf_fixed} file(s) from CRLF to LF")

    # Apply settings.json hook merge
    if merged_settings is not None:
        settings_path = os.path.join(project_dir, ".claude", "settings.json")
        try:
            # Backup existing settings.json
            if os.path.isfile(settings_path):
                bak = os.path.join(backup_dir, ".claude", "settings.json")
                os.makedirs(os.path.dirname(bak), exist_ok=True)
                shutil.copy2(settings_path, bak)

            # Write merged settings
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(merged_settings, f, indent=2, ensure_ascii=False)
                f.write("\n")
            applied.append(f"SETTINGS: Merged hook registrations into .claude/settings.json")
        except (OSError, IOError) as e:
            errors.append(f"SETTINGS MERGE FAILED: {e}")

    return applied, errors


def print_report(report, project_version, template_version, apply_mode=False,
                 claude_md_info=None, settings_changes=None):
    """Print human-readable sync report."""
    mode = "APPLY" if apply_mode else "DRY RUN"
    print(f"=== TEMPLATE SYNC REPORT ({mode}) ===")
    print(f"Project version: {project_version}")
    print(f"Template version: {template_version}")

    if project_version != "0.0.0" and project_version != template_version:
        print(f"\n  UPGRADE: {project_version} -> {template_version} — See CHANGELOG.md for details.")

    print()

    # CLAUDE.md structure version check
    if claude_md_info:
        proj_v, tmpl_v, needs_migration = claude_md_info
        if needs_migration:
            label = proj_v if proj_v else "unversioned/legacy"
            print(f"CLAUDE.MD STRUCTURE OUTDATED:")
            print(f"  Project CLAUDE.md: {label}")
            print(f"  Template expects:  {tmpl_v}")
            print(f"  Run /template-migrate to update CLAUDE.md structure.")
            print(f"  (template_sync.py does not modify CLAUDE.md — this requires guided migration.)")
            print()
        else:
            if tmpl_v:
                print(f"CLAUDE.MD STRUCTURE: up to date ({tmpl_v})")
                print()

    # settings.json hook merge status
    if settings_changes:
        has_actions = any(c.startswith("+") or c.startswith("~") for c in settings_changes)
        if has_actions:
            action_count = sum(1 for c in settings_changes if c.startswith("+") or c.startswith("~"))
            print(f"SETTINGS.JSON HOOK MERGE ({action_count} change(s)):")
        else:
            print("SETTINGS.JSON HOOK MERGE:")
        for change in settings_changes:
            print(f"  {change}")
        print()

    if report["missing_dirs"]:
        print(f"MISSING DIRECTORIES ({len(report['missing_dirs'])}):")
        for d in report["missing_dirs"]:
            print(f"  + {d}")
        print()

    if report["created"]:
        print(f"WILL CREATE ({len(report['created'])}):")
        for rel_path, category in report["created"]:
            print(f"  + {rel_path}  ({category})")
        print()

    if report["updated"]:
        print(f"WILL UPDATE ({len(report['updated'])}):")
        for rel_path, category in report["updated"]:
            print(f"  ~ {rel_path}  ({category})")
        print()

    if report["drifted"]:
        print(f"DRIFTED FROM TEMPLATE ({len(report['drifted'])}):")
        for rel_path in report["drifted"]:
            print(f"  ! {rel_path}")
        print()

    if report["skipped"]:
        print(f"SKIPPED — PROJECT-OWNED ({len(report['skipped'])}):")
        for rel_path in report["skipped"]:
            print(f"  - {rel_path}")
        print()

    if report["current"]:
        print(f"UP TO DATE ({len(report['current'])}):")
        for rel_path in report["current"]:
            print(f"  = {rel_path}")
        print()

    if report["generated_skip"]:
        print(f"GENERATED — SKIPPED ({len(report['generated_skip'])}):")
        for rel_path in report["generated_skip"]:
            print(f"  * {rel_path}")
        print()

    # Summary
    settings_action_count = 0
    if settings_changes:
        settings_action_count = sum(1 for c in settings_changes if c.startswith("+") or c.startswith("~"))
    total_actions = len(report["created"]) + len(report["updated"]) + len(report["missing_dirs"]) + settings_action_count
    if total_actions == 0:
        print("STATUS: Project is fully in sync with template.")
    else:
        print(f"STATUS: {total_actions} action(s) needed.")
        if not apply_mode:
            print("Run with --apply to execute these changes.")


def main():
    if len(sys.argv) < 3:
        print("Usage: python template_sync.py <template_dir> <project_dir> [--apply] [--backup-dir <path>]")
        sys.exit(1)

    template_dir = os.path.abspath(sys.argv[1])
    project_dir = os.path.abspath(sys.argv[2])
    apply_mode = "--apply" in sys.argv
    backup_dir = None

    if "--backup-dir" in sys.argv:
        idx = sys.argv.index("--backup-dir")
        if idx + 1 < len(sys.argv):
            backup_dir = os.path.abspath(sys.argv[idx + 1])

    # Validate directories
    if not os.path.isdir(template_dir):
        print(f"ERROR: Template directory not found: {template_dir}")
        sys.exit(1)
    if not os.path.isdir(project_dir):
        print(f"ERROR: Project directory not found: {project_dir}")
        sys.exit(1)

    # Load manifest and versions
    manifest = load_manifest(template_dir)
    template_version = manifest.get("template_version", "unknown")
    project_version = load_project_version(project_dir)

    # Check CLAUDE.md structure version
    claude_md_info = check_claude_md_version(project_dir, manifest)

    # Check settings.json hook merge
    settings_changes, merged_settings = merge_settings_json(project_dir, manifest)

    # Generate report
    report = sync_report(template_dir, project_dir, manifest)

    # Print report
    print_report(report, project_version, template_version, apply_mode,
                 claude_md_info=claude_md_info, settings_changes=settings_changes)

    # Apply if requested
    if apply_mode:
        print()
        print("--- APPLYING CHANGES ---")
        applied, errors = apply_sync(template_dir, project_dir, report, backup_dir,
                                     template_version, merged_settings=merged_settings)
        for line in applied:
            print(f"  {line}")
        if errors:
            print()
            print("ERRORS:")
            for line in errors:
                print(f"  {line}")
            sys.exit(1)
        else:
            print()
            print(f"Sync complete. {len(applied)} action(s) applied.")


if __name__ == "__main__":
    # Force UTF-8 on Windows
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
