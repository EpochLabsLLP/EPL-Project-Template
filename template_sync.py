"""Template Sync Engine — Compare template repo against active projects.

Usage:
    python template_sync.py <template_dir> <project_dir>             # Dry-run report
    python template_sync.py <template_dir> <project_dir> --apply     # Apply changes
    python template_sync.py <template_dir> <project_dir> --backup-dir <path>

Categories (from TEMPLATE_MANIFEST.json):
    infrastructure — Template-owned. Always overwritten on sync.
    template       — Reference files. Always overwritten on sync.
    scaffolding    — Created once. Project-owned after. Never overwritten.
    generated      — Auto-generated. Skipped entirely.

Safety: Never deletes files. Never modifies scaffolding. Always backs up before overwriting.
"""
import sys
import os
import json
import hashlib
import shutil
import glob as globmod
from datetime import datetime


def file_hash(path):
    """SHA-256 hash of file contents."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
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

            if category_name == "scaffolding":
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


def apply_sync(template_dir, project_dir, report, backup_dir, template_version):
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
            shutil.copy2(src, dst)
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
            # Then overwrite
            shutil.copy2(src, dst)
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

    return applied, errors


def print_report(report, project_version, template_version, apply_mode=False):
    """Print human-readable sync report."""
    mode = "APPLY" if apply_mode else "DRY RUN"
    print(f"=== TEMPLATE SYNC REPORT ({mode}) ===")
    print(f"Project version: {project_version}")
    print(f"Template version: {template_version}")
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
    total_actions = len(report["created"]) + len(report["updated"]) + len(report["missing_dirs"])
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

    # Generate report
    report = sync_report(template_dir, project_dir, manifest)

    # Print report
    print_report(report, project_version, template_version, apply_mode)

    # Apply if requested
    if apply_mode:
        print()
        print("--- APPLYING CHANGES ---")
        applied, errors = apply_sync(template_dir, project_dir, report, backup_dir, template_version)
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
