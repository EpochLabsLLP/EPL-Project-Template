#!/usr/bin/env python3
"""
Epoch Labs — SDD Traceability Validator
Parses spec files for traceability IDs, validates chains, and generates the Work Ledger.

Usage:
    python validate_traceability.py <project_dir>             # Full validation + ledger generation
    python validate_traceability.py <project_dir> --quick     # Quick validation, one-line status, no ledger
    python validate_traceability.py <project_dir> --check-active-wo  # Check for IN-PROGRESS Work Order

Exit codes:
    0 = CLEAN (no errors; warnings are OK)
    1 = ERRORS present (broken chains, orphans) or no active WO (--check-active-wo)
    2 = Script error (bad input, crash)

Output:
    - Default: Writes Specs/Work_Ledger.md (persistent project status) + prints summary
    - --quick: Prints one-line status only (for hook use, <2s target)
    - --check-active-wo: Prints active WO IDs or "NO_ACTIVE_WO" (for hook use, <1s target)
"""

import re
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path


def find_files(project_dir, subdirs, pattern="*.md"):
    """Find markdown files in specified subdirectories."""
    files = []
    for subdir in subdirs:
        d = project_dir / subdir
        if d.exists():
            for f in d.rglob(pattern):
                # Skip templates and archive
                if f.name.startswith("TEMPLATE_"):
                    continue
                if "_Archive" in str(f):
                    continue
                files.append(f)
    return files


def extract_ids(content, pattern):
    """Extract all matching IDs from content."""
    return list(set(re.findall(pattern, content)))


def check_frozen(content):
    """Check if a document has FROZEN status in the first 15 lines."""
    lines = content.split("\n")[:15]
    for line in lines:
        if re.search(r'\bFROZEN\b', line):
            return True
    return False


def get_wo_status(content):
    """Extract Work Order status from content."""
    match = re.search(r'\*\*Status\*\*\s*\|\s*(PENDING|IN-PROGRESS|VALIDATION|DONE|FAILED)', content)
    if match:
        return match.group(1)
    return "UNKNOWN"


def parse_specs(project_dir):
    """Parse all spec files and extract traceability data."""
    data = {
        "pvd_ids": {},        # PVD-N -> {file, title}
        "es_ids": {},         # ES-N.M -> {file, parent_pvd}
        "ux_ids": {},         # UX-N.M -> {file, parent_pvd}
        "bp_ids": {},         # BP-N.M.T -> {file, parent_es}
        "tp_ids": {},         # TP-N.M.T -> {file, parent_bp}
        "wo_ids": {},         # WO-N.M.T-X -> {file, parent_bp, status}
        "dr_ids": {},         # DR-NNN -> {file}
        "gt_ids": {},         # GT-TN-NNN -> {file}
        "frozen_specs": {},   # spec_type -> {file, frozen}
    }

    spec_files = find_files(project_dir, ["Specs"])
    test_files = find_files(project_dir, ["Testing"])
    wo_files = find_files(project_dir, ["WorkOrders"])

    # --- Identify spec types and frozen status ---
    for f in spec_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        name = f.name.lower()

        if "pvd" in name and "template" not in name:
            data["frozen_specs"]["PVD"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}
        elif "prd" in name and "template" not in name:
            data["frozen_specs"]["PRD"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}
        elif "product_brief" in name and "template" not in name:
            data["frozen_specs"]["Product_Brief"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}
        elif "engineering_spec" in name and "template" not in name:
            data["frozen_specs"]["Engineering_Spec"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}
        elif "ux_spec" in name and "template" not in name:
            data["frozen_specs"]["UX_Spec"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}
        elif "blueprint" in name and "template" not in name:
            data["frozen_specs"]["Blueprint"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}
        elif "decision_record" in name and "template" not in name:
            data["frozen_specs"]["Decision_Record"] = {"file": str(f.relative_to(project_dir)), "frozen": False}  # Living, never frozen

    for f in test_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        name = f.name.lower()
        if "testing_plan" in name and "template" not in name:
            data["frozen_specs"]["Testing_Plans"] = {"file": str(f.relative_to(project_dir)), "frozen": check_frozen(content)}

    # --- Extract traceability IDs from all files ---
    all_files = spec_files + test_files + wo_files
    for f in all_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        rel_path = str(f.relative_to(project_dir))

        # PVD IDs: PVD-N (single number)
        for m in re.finditer(r'###\s+PVD-(\d+):\s*(.+)', content):
            pvd_id = f"PVD-{m.group(1)}"
            data["pvd_ids"][pvd_id] = {"file": rel_path, "title": m.group(2).strip()}

        # ES IDs: ES-N.M
        for m in re.finditer(r'###\s+ES-(\d+\.\d+):\s*(.+)', content):
            es_id = f"ES-{m.group(1)}"
            parent_n = m.group(1).split(".")[0]
            data["es_ids"][es_id] = {"file": rel_path, "parent_pvd": f"PVD-{parent_n}", "title": m.group(2).strip()}

        # UX IDs: UX-N.M
        for m in re.finditer(r'###\s+UX-(\d+\.\d+):\s*(.+)', content):
            ux_id = f"UX-{m.group(1)}"
            parent_n = m.group(1).split(".")[0]
            data["ux_ids"][ux_id] = {"file": rel_path, "parent_pvd": f"PVD-{parent_n}", "title": m.group(2).strip()}

        # BP IDs: BP-N.M.T
        for m in re.finditer(r'###\s+BP-(\d+\.\d+\.\d+):\s*(.+)', content):
            bp_id = f"BP-{m.group(1)}"
            parts = m.group(1).split(".")
            parent_es = f"ES-{parts[0]}.{parts[1]}"
            data["bp_ids"][bp_id] = {"file": rel_path, "parent_es": parent_es, "title": m.group(2).strip()}

        # TP IDs: TP-N.M.T
        for m in re.finditer(r'###\s+TP-(\d+\.\d+\.\d+):\s*(.+)', content):
            tp_id = f"TP-{m.group(1)}"
            parts = m.group(1).split(".")
            mirror_bp = f"BP-{parts[0]}.{parts[1]}.{parts[2]}"
            data["tp_ids"][tp_id] = {"file": rel_path, "mirror_bp": mirror_bp, "title": m.group(2).strip()}

        # WO IDs: WO-N.M.T-X (header format)
        for m in re.finditer(r'#\s+Work Order:\s+WO-(\d+\.\d+\.\d+)-([A-Z])', content):
            wo_id = f"WO-{m.group(1)}-{m.group(2)}"
            parts = m.group(1).split(".")
            parent_bp = f"BP-{parts[0]}.{parts[1]}.{parts[2]}"
            status = get_wo_status(content)
            data["wo_ids"][wo_id] = {"file": rel_path, "parent_bp": parent_bp, "status": status}

        # DR IDs: DR-NNN
        for m in re.finditer(r'###\s+DR-(\d+):', content):
            dr_id = f"DR-{m.group(1).zfill(3)}"
            data["dr_ids"][dr_id] = {"file": rel_path}

        # GT IDs: GT-TN-NNN
        for m in re.finditer(r'GT-T(\d+)-(\d+)', content):
            gt_id = f"GT-T{m.group(1)}-{m.group(2).zfill(3)}"
            data["gt_ids"][gt_id] = {"file": rel_path}

    return data


def validate_chains(data):
    """Validate traceability chains and report issues."""
    warnings = []
    errors = []

    # ES -> PVD validation
    for es_id, info in sorted(data["es_ids"].items()):
        parent = info["parent_pvd"]
        if parent not in data["pvd_ids"]:
            errors.append(f"ORPHAN: {es_id} references {parent} but {parent} not found in PVD")

    # UX -> PVD validation
    for ux_id, info in sorted(data["ux_ids"].items()):
        parent = info["parent_pvd"]
        if parent not in data["pvd_ids"]:
            errors.append(f"ORPHAN: {ux_id} references {parent} but {parent} not found in PVD")

    # BP -> ES validation
    for bp_id, info in sorted(data["bp_ids"].items()):
        parent = info["parent_es"]
        if parent not in data["es_ids"]:
            errors.append(f"ORPHAN: {bp_id} references {parent} but {parent} not found in Engineering Spec")

    # TP mirrors BP validation
    for bp_id in sorted(data["bp_ids"].keys()):
        tp_id = bp_id.replace("BP-", "TP-")
        if tp_id not in data["tp_ids"]:
            warnings.append(f"MISSING MIRROR: {bp_id} has no corresponding {tp_id} in Testing Plans")

    # WO -> BP validation
    for wo_id, info in sorted(data["wo_ids"].items()):
        parent = info["parent_bp"]
        if parent not in data["bp_ids"]:
            errors.append(f"ORPHAN: {wo_id} references {parent} but {parent} not found in Blueprint")

    # PVD features without ES modules (gaps)
    for pvd_id in sorted(data["pvd_ids"].keys()):
        n = pvd_id.split("-")[1]
        has_es = any(es.startswith(f"ES-{n}.") for es in data["es_ids"])
        if not has_es and data["es_ids"]:  # Only warn if ES exists at all
            warnings.append(f"GAP: {pvd_id} has no Engineering Spec modules (no ES-{n}.x found)")

    return warnings, errors


def build_traceability_tree(data):
    """Build the traceability tree for display."""
    lines = []
    if not data["pvd_ids"]:
        lines.append("No PVD features found. Create and freeze a PVD to begin traceability.")
        return lines

    for pvd_id in sorted(data["pvd_ids"].keys(), key=lambda x: int(x.split("-")[1])):
        pvd_info = data["pvd_ids"][pvd_id]
        n = pvd_id.split("-")[1]
        lines.append(f"{pvd_id}: {pvd_info['title']}")

        # Find ES modules for this PVD
        es_modules = sorted([k for k in data["es_ids"] if k.startswith(f"ES-{n}.")])

        # Find UX items for this PVD
        ux_items = sorted([k for k in data["ux_ids"] if k.startswith(f"UX-{n}.")])

        for ux_id in ux_items:
            ux_info = data["ux_ids"][ux_id]
            lines.append(f"  (UX) {ux_id}: {ux_info['title']}")

        for i, es_id in enumerate(es_modules):
            es_info = data["es_ids"][es_id]
            is_last_es = (i == len(es_modules) - 1) and not ux_items
            prefix = "  └─" if is_last_es else "  ├─"
            child_prefix = "    " if is_last_es else "  │ "
            lines.append(f"{prefix} {es_id}: {es_info['title']}")

            # Find BP tasks for this ES module
            nm = es_id.split("-")[1]
            bp_tasks = sorted([k for k in data["bp_ids"] if k.startswith(f"BP-{nm}.")])

            for j, bp_id in enumerate(bp_tasks):
                is_last_bp = (j == len(bp_tasks) - 1)
                bp_prefix = "└─" if is_last_bp else "├─"
                bp_child = "  " if is_last_bp else "│ "

                # Check TP mirror
                tp_id = bp_id.replace("BP-", "TP-")
                tp_mark = "✓" if tp_id in data["tp_ids"] else "(!) TP MISSING"

                # Check WO
                nmt = bp_id.split("-")[1]
                wo_matches = sorted([k for k in data["wo_ids"] if k.startswith(f"WO-{nmt}-")])

                if wo_matches:
                    wo_parts = []
                    for wo_id in wo_matches:
                        wo_status = data["wo_ids"][wo_id]["status"]
                        wo_parts.append(f"{wo_id} [{wo_status}]")
                    wo_str = " → ".join(wo_parts)
                    lines.append(f"{child_prefix}  {bp_prefix} {bp_id} → {tp_id} {tp_mark} → {wo_str}")
                else:
                    lines.append(f"{child_prefix}  {bp_prefix} {bp_id} → {tp_id} {tp_mark} → (no WO yet)")

        lines.append("")  # blank line between PVD features

    return lines


def check_spec_readiness(data):
    """Check which frozen specs exist."""
    lines = []
    required_specs = {
        "PVD": "PVD (or Product Brief + PRD)",
        "Engineering_Spec": "Engineering Spec",
        "Blueprint": "Blueprint",
        "Testing_Plans": "Testing Plans",
    }
    optional_specs = {
        "UX_Spec": "UX Spec",
        "Decision_Record": "Decision Record",
    }

    # Check PVD or Brief+PRD path
    has_pvd = "PVD" in data["frozen_specs"] and data["frozen_specs"]["PVD"]["frozen"]
    has_brief = "Product_Brief" in data["frozen_specs"] and data["frozen_specs"]["Product_Brief"]["frozen"]
    has_prd = "PRD" in data["frozen_specs"] and data["frozen_specs"]["PRD"]["frozen"]
    has_product_spec = has_pvd or (has_brief and has_prd)

    if has_pvd:
        f = data["frozen_specs"]["PVD"]["file"]
        lines.append(f"- [x] PVD: {f} (FROZEN)")
    elif has_brief and has_prd:
        fb = data["frozen_specs"]["Product_Brief"]["file"]
        fp = data["frozen_specs"]["PRD"]["file"]
        lines.append(f"- [x] Product Brief: {fb} (FROZEN)")
        lines.append(f"- [x] PRD: {fp} (FROZEN)")
    elif "PVD" in data["frozen_specs"]:
        f = data["frozen_specs"]["PVD"]["file"]
        lines.append(f"- [ ] PVD: {f} (not frozen)")
    elif "Product_Brief" in data["frozen_specs"] or "PRD" in data["frozen_specs"]:
        if "Product_Brief" in data["frozen_specs"]:
            fb = data["frozen_specs"]["Product_Brief"]["file"]
            frozen_b = data["frozen_specs"]["Product_Brief"]["frozen"]
            lines.append(f"- {'[x]' if frozen_b else '[ ]'} Product Brief: {fb} ({'FROZEN' if frozen_b else 'not frozen'})")
        else:
            lines.append("- [ ] Product Brief: not found")
        if "PRD" in data["frozen_specs"]:
            fp = data["frozen_specs"]["PRD"]["file"]
            frozen_p = data["frozen_specs"]["PRD"]["frozen"]
            lines.append(f"- {'[x]' if frozen_p else '[ ]'} PRD: {fp} ({'FROZEN' if frozen_p else 'not frozen'})")
        else:
            lines.append("- [ ] PRD: not found")
    else:
        lines.append("- [ ] PVD: not found")

    # Check other required specs
    for key in ["Engineering_Spec", "Blueprint", "Testing_Plans"]:
        label = required_specs[key]
        if key in data["frozen_specs"]:
            f = data["frozen_specs"][key]["file"]
            frozen = data["frozen_specs"][key]["frozen"]
            lines.append(f"- {'[x]' if frozen else '[ ]'} {label}: {f} ({'FROZEN' if frozen else 'not frozen'})")
        else:
            lines.append(f"- [ ] {label}: not found")

    # Check optional specs
    for key, label in optional_specs.items():
        if key in data["frozen_specs"]:
            f = data["frozen_specs"][key]["file"]
            if key == "Decision_Record":
                lines.append(f"- [x] {label}: {f} (LIVING)")
            else:
                frozen = data["frozen_specs"][key]["frozen"]
                lines.append(f"- {'[x]' if frozen else '[ ]'} {label}: {f} ({'FROZEN' if frozen else 'not frozen'})")
        else:
            if key == "UX_Spec":
                lines.append(f"- [ ] {label}: not found (N/A for non-UI projects)")
            else:
                lines.append(f"- [ ] {label}: not found")

    return lines, has_product_spec


def generate_work_ledger(project_dir, data, warnings, errors, tree_lines, readiness_lines, has_product_spec):
    """Generate the Work Ledger markdown file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_issues = len(warnings) + len(errors)
    status = "CLEAN" if total_issues == 0 else f"{len(errors)} error(s), {len(warnings)} warning(s)" if errors else f"{len(warnings)} warning(s)"

    lines = []
    lines.append("<!-- AUTO-GENERATED by validate_traceability.py — DO NOT HAND-EDIT -->")
    lines.append("<!-- Run /trace-check to regenerate this file -->")
    lines.append("")
    lines.append("# Work Ledger")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Status:** {status}")
    lines.append("")

    # Spec Readiness
    lines.append("## Spec Readiness")
    lines.extend(readiness_lines)
    lines.append("")

    # Traceability Chain
    lines.append("## Traceability Chain")
    if tree_lines:
        lines.extend(tree_lines)
    else:
        lines.append("No traceability data found. Create and freeze specs to populate.")
    lines.append("")

    # Active Work Orders
    lines.append("## Active Work Orders")
    active_wos = {k: v for k, v in data["wo_ids"].items() if v["status"] in ("PENDING", "IN-PROGRESS", "VALIDATION")}
    if active_wos:
        for wo_id in sorted(active_wos.keys()):
            info = active_wos[wo_id]
            bp_id = info["parent_bp"]

            # Build chain string
            bp_parts = bp_id.split("-")[1].split(".")
            es_id = f"ES-{bp_parts[0]}.{bp_parts[1]}"
            pvd_id = f"PVD-{bp_parts[0]}"
            chain = f"{bp_id} → {es_id} → {pvd_id}"

            lines.append(f"{wo_id} | {chain} | Status: {info['status']}")
    else:
        lines.append("No active Work Orders.")
    lines.append("")

    # Errors
    if errors:
        lines.append("## Errors")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    # Warnings
    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Progress
    lines.append("## Progress")
    total_bp = len(data["bp_ids"])
    bp_with_wo = set()
    bp_done = set()
    bp_in_progress = set()
    bp_failed = set()
    bp_pending = set()

    for wo_id, info in data["wo_ids"].items():
        bp_id = info["parent_bp"]
        bp_with_wo.add(bp_id)
        if info["status"] == "DONE":
            bp_done.add(bp_id)
        elif info["status"] == "IN-PROGRESS":
            bp_in_progress.add(bp_id)
        elif info["status"] == "FAILED":
            bp_failed.add(bp_id)
        elif info["status"] == "PENDING":
            bp_pending.add(bp_id)

    if total_bp > 0:
        coverage = int(len(bp_with_wo) / total_bp * 100)
        lines.append(f"Blueprint tasks: {total_bp} | With WOs: {len(bp_with_wo)} | "
                     f"Completed: {len(bp_done)} | In-Progress: {len(bp_in_progress)} | "
                     f"Failed: {len(bp_failed)} | Pending: {len(bp_pending)}")
        lines.append(f"Coverage: {coverage}% of tasks have Work Orders")
    else:
        lines.append("No Blueprint tasks found. Create and freeze a Blueprint to track progress.")
    lines.append("")

    # Write file
    ledger_path = project_dir / "Specs" / "Work_Ledger.md"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("\n".join(lines), encoding="utf-8")

    return lines, status


def run_check_active_wo(project_dir):
    """Quick check: is any Work Order IN-PROGRESS? Exit 0 if yes, 1 if no."""
    wo_dir = project_dir / "WorkOrders"
    if not wo_dir.exists():
        print("NO_ACTIVE_WO: WorkOrders/ directory not found")
        return 1

    wo_files = [f for f in wo_dir.glob("*.md")
                if not f.name.startswith("TEMPLATE_") and "_Archive" not in str(f)]

    if not wo_files:
        print("NO_ACTIVE_WO: No Work Order files found")
        return 1

    active = []
    for f in wo_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        status = get_wo_status(content)
        if status == "IN-PROGRESS":
            # Extract WO ID from filename or content
            m = re.search(r'WO-\d+\.\d+\.\d+-[A-Z]', f.name) or re.search(r'WO-\d+\.\d+\.\d+-[A-Z]', content)
            wo_id = m.group(0) if m else f.name
            active.append(wo_id)

    if active:
        print(f"ACTIVE_WO: {', '.join(sorted(active))}")
        return 0
    else:
        print("NO_ACTIVE_WO: No Work Order has status IN-PROGRESS")
        return 1


def run_quick(project_dir):
    """Quick validation: validate chains, print one-line status, no ledger generation."""
    data = parse_specs(project_dir)
    warnings, errors = validate_chains(data)

    error_count = len(errors)
    warning_count = len(warnings)

    if error_count == 0 and warning_count == 0:
        print("TRACEABILITY: CLEAN")
        return 0
    elif error_count == 0:
        print(f"TRACEABILITY: {warning_count} warning(s)")
        return 0  # Warnings don't block
    else:
        print(f"TRACEABILITY: {error_count} error(s), {warning_count} warning(s)")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1  # Errors block


def run_full(project_dir):
    """Full validation + ledger generation (default behavior)."""
    # Parse all specs
    data = parse_specs(project_dir)

    # Validate chains
    warnings, errors = validate_chains(data)

    # Build traceability tree
    tree_lines = build_traceability_tree(data)

    # Check spec readiness
    readiness_lines, has_product_spec = check_spec_readiness(data)

    # Generate Work Ledger
    ledger_lines, status = generate_work_ledger(
        project_dir, data, warnings, errors, tree_lines, readiness_lines, has_product_spec
    )

    # Print summary to stdout
    print("=" * 60)
    print("TRACEABILITY VALIDATION REPORT")
    print("=" * 60)
    print(f"Status: {status}")
    print()
    print("--- Spec Readiness ---")
    for line in readiness_lines:
        print(line)
    print()

    if data["pvd_ids"] or data["es_ids"] or data["bp_ids"]:
        print("--- Traceability Chain ---")
        for line in tree_lines:
            print(line)

    if data["wo_ids"]:
        active = {k: v for k, v in data["wo_ids"].items() if v["status"] in ("PENDING", "IN-PROGRESS", "VALIDATION")}
        if active:
            print("--- Active Work Orders ---")
            for wo_id in sorted(active.keys()):
                info = active[wo_id]
                print(f"  {wo_id} | Status: {info['status']}")
            print()

    if errors:
        print("--- ERRORS ---")
        for e in errors:
            print(f"  ✗ {e}")
        print()

    if warnings:
        print("--- WARNINGS ---")
        for w in warnings:
            print(f"  ! {w}")
        print()

    total_bp = len(data["bp_ids"])
    if total_bp > 0:
        bp_done = len(set(info["parent_bp"] for info in data["wo_ids"].values() if info["status"] == "DONE"))
        print(f"--- Progress: {bp_done}/{total_bp} Blueprint tasks completed ---")
    else:
        print("--- No Blueprint tasks found ---")

    print()
    print(f"Work Ledger written to: Specs/Work_Ledger.md")

    # Return exit code based on errors
    return 1 if errors else 0


def main():
    # Force UTF-8 output on Windows (cp1252 can't handle tree-drawing characters)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="SDD Traceability Validator")
    parser.add_argument("project_dir", help="Path to project directory")
    parser.add_argument("--quick", action="store_true",
                        help="Quick validation: one-line status, no ledger generation")
    parser.add_argument("--check-active-wo", action="store_true",
                        help="Check for IN-PROGRESS Work Order (exit 0=found, 1=not found)")

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse calls sys.exit on error; remap to exit code 2
        sys.exit(2)

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.exists():
        print(f"Error: Directory not found: {project_dir}")
        sys.exit(2)

    try:
        if args.check_active_wo:
            exit_code = run_check_active_wo(project_dir)
        elif args.quick:
            exit_code = run_quick(project_dir)
        else:
            exit_code = run_full(project_dir)
    except Exception as e:
        print(f"CRASH: {e}")
        sys.exit(2)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
