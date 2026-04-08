#!/usr/bin/env python3
"""
Epoch Labs — Work Context Extractor
Evaluates governance readiness, extracts spec chains into per-WO context
documents, and validates completeness.

Usage:
    python extract_work_context.py <project_dir> --evaluate       # Assess readiness, recommend route
    python extract_work_context.py <project_dir> --extract        # Extract work context documents
    python extract_work_context.py <project_dir> --validate       # Validate extracted documents
    python extract_work_context.py <project_dir> --all            # Run all three stages

Exit codes:
    0 = Success (or GREEN/YELLOW readiness)
    1 = Issues found (RED readiness, or validation gaps)
    2 = Cannot proceed (BLACK readiness, or script error)
"""

import re
import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Reusable parsing helpers (aligned with validate_traceability.py patterns)
# ---------------------------------------------------------------------------

def find_md_files(project_dir, subdirs):
    """Find markdown files in specified subdirectories, skipping templates and archives."""
    files = []
    for subdir in subdirs:
        d = project_dir / subdir
        if d.exists():
            for f in d.rglob("*.md"):
                if f.name.startswith("TEMPLATE_"):
                    continue
                if "_Archive" in str(f):
                    continue
                files.append(f)
    return files


def check_frozen(content):
    """Check if a document has FROZEN status in the first 15 lines."""
    lines = content.split("\n")[:15]
    for line in lines:
        if re.search(r'\bFROZEN\b', line):
            return True
    return False


def classify_spec_file(file_path):
    """Classify a spec file by type based on filename."""
    name = file_path.name.lower()
    if "engineering_spec" in name:
        return "Engineering_Spec"
    if "ux_spec" in name:
        return "UX_Spec"
    if "blueprint" in name:
        return "Blueprint"
    if "product_brief" in name:
        return "Product_Brief"
    if "decision_record" in name:
        return "Decision_Record"
    if "testing_plan" in name:
        return "Testing_Plans"
    if re.search(r'(^|_)prd(?:_|\.|$)', name):
        return "PRD"
    if re.search(r'(^|_)pvd(?:_|\.|$)', name):
        return "PVD"
    if "gap_tracker" in name or "pre_coding_checklist" in name:
        return "Gap_Tracker"
    return None


# ---------------------------------------------------------------------------
# ID extraction patterns
# ---------------------------------------------------------------------------

PVD_HEADER = re.compile(r'###\s+PVD-(\d+):\s*(.+)')
ES_HEADER = re.compile(r'###?\s+ES-(\d+\.\d+):?\s*(.+)')
BP_HEADER = re.compile(r'###\s+BP-(\d+\.\d+\.\d+):\s*(.+)')
TP_HEADER = re.compile(r'###\s+TP-(\d+\.\d+\.\d+):\s*(.+)')
WO_HEADER = re.compile(r'#\s+(?:Work Order:\s+)?WO-(\d+\.\d+\.\d+)-([A-Z])')

# Looser patterns for detecting ANY traceability IDs in content
ID_PVD = re.compile(r'PVD-\d+')
ID_ES = re.compile(r'ES-\d+\.\d+')
ID_BP = re.compile(r'BP-\d+\.\d+\.\d+')
ID_TP = re.compile(r'TP-\d+\.\d+\.\d+')
ID_WO = re.compile(r'WO-\d+\.\d+\.\d+-[A-Z]')


def count_ids(files):
    """Count traceability IDs found across all files."""
    counts = {"PVD": set(), "ES": set(), "BP": set(), "TP": set(), "WO": set()}
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            continue
        counts["PVD"].update(ID_PVD.findall(content))
        counts["ES"].update(ID_ES.findall(content))
        counts["BP"].update(ID_BP.findall(content))
        counts["TP"].update(ID_TP.findall(content))
        counts["WO"].update(ID_WO.findall(content))
    return {k: len(v) for k, v in counts.items()}


# ---------------------------------------------------------------------------
# Stage 1: Governance Readiness Assessment
# ---------------------------------------------------------------------------

def evaluate_readiness(project_dir):
    """Assess governance readiness and recommend extraction route.

    Returns a dict with:
      route: GREEN | YELLOW | RED | BLACK
      score: 0-100
      details: list of findings
      spec_files: dict of classified files found
      cleanup_suggestions: list of files to archive
    """
    findings = []
    spec_files = {}
    cleanup = []

    specs_dir = project_dir / "Specs"
    testing_dir = project_dir / "Testing"
    wo_dir = project_dir / "WorkOrders"

    # --- Check if spec directories exist ---
    has_specs = specs_dir.exists() and any(specs_dir.iterdir())
    has_testing = testing_dir.exists() and any(testing_dir.iterdir()) if testing_dir.exists() else False
    has_wos = wo_dir.exists() and any(wo_dir.iterdir()) if wo_dir.exists() else False

    if not has_specs:
        return {
            "route": "BLACK",
            "score": 0,
            "details": ["No Specs/ directory found or it is empty. Cannot extract work context without specifications."],
            "spec_files": {},
            "cleanup_suggestions": [],
            "id_counts": {},
        }

    # --- Classify spec files ---
    all_spec_files = find_md_files(project_dir, ["Specs"])
    all_test_files = find_md_files(project_dir, ["Testing"])
    all_wo_files = find_md_files(project_dir, ["WorkOrders"])
    all_files = all_spec_files + all_test_files + all_wo_files

    for f in all_spec_files + all_test_files:
        spec_type = classify_spec_file(f)
        if spec_type:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                frozen = check_frozen(content)
            except (OSError, IOError):
                frozen = False
            if spec_type not in spec_files:
                spec_files[spec_type] = []
            spec_files[spec_type].append({"file": f.name, "path": str(f), "frozen": frozen})

    # --- Score components ---
    score = 0
    max_score = 100

    # Component 1: PVD or Product Brief exists (20 pts)
    has_pvd = "PVD" in spec_files or "Product_Brief" in spec_files
    if has_pvd:
        score += 20
        findings.append("[PASS] Product spec found (PVD or Product Brief)")
    else:
        findings.append("[MISS] No PVD or Product Brief found — upstream requirements unknown")

    # Component 2: Engineering Spec exists (20 pts)
    has_es = "Engineering_Spec" in spec_files
    if has_es:
        score += 20
        frozen_es = any(f["frozen"] for f in spec_files.get("Engineering_Spec", []))
        if frozen_es:
            score += 5
            findings.append("[PASS] Engineering Spec found and FROZEN")
        else:
            findings.append("[WARN] Engineering Spec found but not FROZEN")
    else:
        findings.append("[MISS] No Engineering Spec found")

    # Component 3: Blueprint exists (20 pts)
    has_bp = "Blueprint" in spec_files
    if has_bp:
        score += 20
        frozen_bp = any(f["frozen"] for f in spec_files.get("Blueprint", []))
        if frozen_bp:
            score += 5
            findings.append("[PASS] Blueprint found and FROZEN")
        else:
            findings.append("[WARN] Blueprint found but not FROZEN")
    else:
        findings.append("[MISS] No Blueprint found — no task decomposition available")

    # Component 4: Testing Plans exist (10 pts)
    has_tp = "Testing_Plans" in spec_files
    if has_tp:
        score += 10
        findings.append("[PASS] Testing Plans found")
    else:
        findings.append("[MISS] No Testing Plans found")

    # Component 5: Traceability ID coverage (20 pts)
    id_counts = count_ids(all_files)
    total_ids = sum(id_counts.values())

    # Also check for non-standard BP formats (e.g., BP-0.1 instead of BP-0.1.1)
    nonstandard_bp = set()
    for f in all_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            continue
        # Match BP-N.M (two-part) that are NOT BP-N.M.T (three-part)
        for m in re.finditer(r'BP-(\d+\.\d+)(?!\.\d)', content):
            nonstandard_bp.add(f"BP-{m.group(1)}")

    if total_ids == 0:
        findings.append("[MISS] No traceability IDs found (PVD-N, ES-N.M, BP-N.M.T patterns)")
    else:
        # Check chain completeness
        chain_levels = sum(1 for k in ["PVD", "ES", "BP"] if id_counts.get(k, 0) > 0)
        if chain_levels >= 3:
            score += 20
            findings.append(f"[PASS] Full traceability chain detected: PVD({id_counts['PVD']}) → ES({id_counts['ES']}) → BP({id_counts['BP']})")
        elif chain_levels >= 2:
            score += 10
            findings.append(f"[PARTIAL] Partial chain: PVD({id_counts['PVD']}) → ES({id_counts['ES']}) → BP({id_counts['BP']})")
        else:
            score += 5
            findings.append(f"[WEAK] Minimal IDs found: PVD({id_counts['PVD']}), ES({id_counts['ES']}), BP({id_counts['BP']})")

    # Check for non-standard BP ID format (two-part vs three-part)
    if nonstandard_bp and id_counts.get("BP", 0) == 0:
        score -= 15  # Downgrade: IDs exist but wrong format for structural extraction
        findings.append(f"[WARN] {len(nonstandard_bp)} non-standard BP IDs found (BP-N.M instead of BP-N.M.T). Structural extraction will miss these — LLM assistance needed.")

    # --- Cleanup suggestions ---
    sessions_dir = project_dir / "Sessions"
    research_dir = project_dir / "Research"
    notes_dir = project_dir / "Notes"

    for check_dir in [sessions_dir, research_dir, notes_dir]:
        if check_dir.exists():
            count = sum(1 for f in check_dir.rglob("*.md") if not f.name.startswith("."))
            if count > 20:
                cleanup.append(f"{check_dir.name}/: {count} files — consider archiving old items to reduce context noise")

    # Check for superseded specs in Specs/ (multiple versions of same type)
    for spec_type, file_list in spec_files.items():
        if len(file_list) > 1:
            non_frozen = [f for f in file_list if not f["frozen"]]
            if non_frozen:
                for f in non_frozen:
                    cleanup.append(f"Specs/{f['file']}: Superseded/draft {spec_type} — archive to Specs/_Archive/")

    # --- Route decision ---
    if score >= 80:
        route = "GREEN"
    elif score >= 40:
        route = "YELLOW"
    elif score > 0:
        route = "RED"
    else:
        route = "BLACK"

    return {
        "route": route,
        "score": score,
        "details": findings,
        "spec_files": spec_files,
        "cleanup_suggestions": cleanup,
        "id_counts": id_counts,
    }


# ---------------------------------------------------------------------------
# Stage 2: Structural Extraction (Tier 1)
# ---------------------------------------------------------------------------

def extract_section(content, header_pattern, section_id):
    """Extract a full section from markdown content given a header pattern and ID.

    Returns the section text from the header to the next same-level or higher header.
    """
    # Build a regex that matches the specific section header
    pattern = re.compile(
        r'^(#{1,4})\s+' + re.escape(section_id) + r'[:\s]',
        re.MULTILINE
    )
    match = pattern.search(content)
    if not match:
        return None

    level = len(match.group(1))
    start = match.start()

    # Find the next header at the same level or higher
    next_header = re.compile(r'^#{1,' + str(level) + r'}\s+', re.MULTILINE)
    rest = content[match.end():]
    next_match = next_header.search(rest)
    if next_match:
        end = match.end() + next_match.start()
    else:
        end = len(content)

    return content[start:end].strip()


def extract_bp_section(content, bp_id):
    """Extract a Blueprint task card section."""
    # BP task cards may use ### or #### headers, with optional extra # prefix
    pattern = re.compile(
        r'^#{2,4}\s+#?\s*' + re.escape(bp_id) + r':\s*(.+?)$',
        re.MULTILINE
    )
    match = pattern.search(content)
    if not match:
        return None

    start = match.start()
    header_level = len(re.match(r'^(#+)', content[start:]).group(1))
    # Find next BP task or same/higher-level header
    rest = content[match.end():]
    next_section = re.search(r'^#{2,' + str(header_level) + r'}\s+(?:#?\s*BP-|Wave\s)', rest, re.MULTILINE)
    if next_section:
        end = match.end() + next_section.start()
    else:
        end = len(content)

    return content[start:end].strip()


def structural_extract(project_dir, spec_files_info):
    """Tier 1: Extract work context documents using structural parsing.

    For each BP task found, extracts the full chain:
      PVD requirement → ES module → BP task card → TP test scenarios

    Returns a list of work context dicts.
    """
    contexts = []

    # Load spec file contents
    spec_contents = {}
    for spec_type, file_list in spec_files_info.items():
        # Use the first frozen file, or first file if none frozen
        frozen = [f for f in file_list if f["frozen"]]
        chosen = frozen[0] if frozen else file_list[0]
        try:
            spec_contents[spec_type] = Path(chosen["path"]).read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            pass

    bp_content = spec_contents.get("Blueprint", "")
    es_content = spec_contents.get("Engineering_Spec", "")
    pvd_content = spec_contents.get("PVD", spec_contents.get("Product_Brief", spec_contents.get("PRD", "")))
    tp_content = spec_contents.get("Testing_Plans", "")

    if not bp_content:
        return contexts

    # Find all BP task cards — support both standard (BP-N.M.T) and non-standard (BP-N.M) formats
    bp_tasks = list(re.finditer(r'###?\s+#?\s*(BP-(\d+)\.(\d+)(?:\.(\d+))?):\s*(.+)', bp_content))

    for match in bp_tasks:
        bp_id = match.group(1)
        pvd_n = match.group(2)
        es_nm = f"{match.group(2)}.{match.group(3)}"
        task_num = match.group(4)  # May be None for BP-N.M format
        bp_title = match.group(5).strip()

        if task_num:
            tp_id = f"TP-{match.group(2)}.{match.group(3)}.{task_num}"
        else:
            tp_id = f"TP-{match.group(2)}.{match.group(3)}"

        context = {
            "bp_id": bp_id,
            "bp_title": bp_title,
            "pvd_id": f"PVD-{pvd_n}",
            "es_id": f"ES-{es_nm}",
            "tp_id": tp_id,
            "sections": {},
            "gaps": [],
        }

        # Extract PVD section
        pvd_section = extract_section(pvd_content, PVD_HEADER, f"PVD-{pvd_n}")
        if pvd_section:
            context["sections"]["pvd"] = pvd_section
        else:
            context["gaps"].append(f"PVD-{pvd_n}: No matching section found in product spec")

        # Extract ES module section
        es_section = extract_section(es_content, ES_HEADER, f"ES-{es_nm}")
        if es_section:
            context["sections"]["es"] = es_section
        else:
            context["gaps"].append(f"ES-{es_nm}: No matching section found in Engineering Spec")

        # Extract BP task card
        bp_section = extract_bp_section(bp_content, bp_id)
        if bp_section:
            context["sections"]["bp"] = bp_section
        else:
            context["gaps"].append(f"{bp_id}: Could not extract task card from Blueprint")

        # Extract TP test scenarios
        tp_section = extract_section(tp_content, TP_HEADER, context["tp_id"])
        if tp_section:
            context["sections"]["tp"] = tp_section
        else:
            context["gaps"].append(f"{context['tp_id']}: No matching section found in Testing Plans")

        # Extract acceptance criteria from BP section
        if bp_section:
            criteria = re.findall(r'(?:GIVEN|WHEN|THEN|AND)\s+.+', bp_section, re.IGNORECASE)
            context["acceptance_criteria"] = criteria

        contexts.append(context)

    return contexts


# ---------------------------------------------------------------------------
# Stage 2: LLM-Assisted Preparation (Tier 2)
# ---------------------------------------------------------------------------

def prepare_llm_extraction(project_dir, spec_files_info, id_counts):
    """Tier 2: Prepare context for LLM-assisted extraction.

    Instead of parsing structurally, this gathers all spec content and
    produces a prompt that the /prepare-work skill feeds to the LLM.

    Returns a dict with:
      spec_inventory: what spec files exist and their types
      content_summaries: first 100 lines of each spec (for LLM context)
      unmapped_areas: areas where structural parsing found nothing
      prompt_template: the prompt for the LLM to use
    """
    inventory = []
    summaries = {}

    for spec_type, file_list in spec_files_info.items():
        for f_info in file_list:
            try:
                content = Path(f_info["path"]).read_text(encoding="utf-8", errors="replace")
                lines = content.split("\n")
                # Get headers for a TOC
                headers = [l for l in lines if l.startswith("#")]
                summary = "\n".join(headers[:50])
                summaries[f_info["file"]] = {
                    "type": spec_type,
                    "frozen": f_info["frozen"],
                    "headers": summary,
                    "line_count": len(lines),
                }
                inventory.append(f"{spec_type}: {f_info['file']} ({'FROZEN' if f_info['frozen'] else 'DRAFT'}, {len(lines)} lines)")
            except (OSError, IOError):
                pass

    # Also gather any unclassified spec files
    for f in find_md_files(project_dir, ["Specs", "Testing"]):
        if f.name not in summaries:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                lines = content.split("\n")
                headers = [l for l in lines if l.startswith("#")]
                summaries[f.name] = {
                    "type": "Unclassified",
                    "frozen": check_frozen(content),
                    "headers": "\n".join(headers[:30]),
                    "line_count": len(lines),
                }
                inventory.append(f"Unclassified: {f.name} ({len(lines)} lines)")
            except (OSError, IOError):
                pass

    return {
        "spec_inventory": inventory,
        "content_summaries": summaries,
        "id_counts": id_counts,
    }


# ---------------------------------------------------------------------------
# Work Context Document Generation
# ---------------------------------------------------------------------------

def generate_work_context_doc(context, project_dir):
    """Generate a single Work Context Document from an extracted context."""
    lines = []
    bp_id = context["bp_id"]
    lines.append(f"# Work Context: {bp_id} — {context['bp_title']}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Traceability: {context['pvd_id']} → {context['es_id']} → {bp_id} → {context['tp_id']}")
    lines.append("")

    if context["gaps"]:
        lines.append("## Extraction Gaps")
        lines.append("The following chain links could not be extracted structurally.")
        lines.append("Use `/prepare-work` with LLM assistance to fill these, or fill manually.")
        lines.append("")
        for gap in context["gaps"]:
            lines.append(f"- **{gap}**")
        lines.append("")

    # Section 1: Why (PVD)
    lines.append("## 1. Why — Product Requirement")
    lines.append(f"*Source: {context['pvd_id']}*")
    lines.append("")
    if "pvd" in context["sections"]:
        lines.append(context["sections"]["pvd"])
    else:
        lines.append("*[NOT FOUND — read the PVD manually and paste the relevant section here]*")
    lines.append("")

    # Section 2: What (ES)
    lines.append("## 2. What — Engineering Specification")
    lines.append(f"*Source: {context['es_id']}*")
    lines.append("")
    if "es" in context["sections"]:
        lines.append(context["sections"]["es"])
    else:
        lines.append("*[NOT FOUND — read the Engineering Spec manually and paste the relevant module section here]*")
    lines.append("")

    # Section 3: How (BP task card)
    lines.append("## 3. How — Blueprint Task Card")
    lines.append(f"*Source: {bp_id}*")
    lines.append("")
    if "bp" in context["sections"]:
        lines.append(context["sections"]["bp"])
    else:
        lines.append("*[NOT FOUND]*")
    lines.append("")

    # Section 4: Proof (TP)
    lines.append("## 4. Proof — Test Scenarios")
    lines.append(f"*Source: {context['tp_id']}*")
    lines.append("")
    if "tp" in context["sections"]:
        lines.append(context["sections"]["tp"])
    else:
        lines.append("*[NOT FOUND — read the Testing Plans manually and paste the relevant section here]*")
    lines.append("")

    # Section 5: Acceptance Checklist
    lines.append("## 5. Acceptance Checklist")
    lines.append("Every item must be verified before marking this task DONE.")
    lines.append("")
    criteria = context.get("acceptance_criteria", [])
    if criteria:
        for c in criteria:
            lines.append(f"- [ ] {c.strip()}")
    else:
        lines.append("*[Extract GIVEN/WHEN/THEN criteria from the Blueprint task card above]*")
    lines.append("")

    # Section 6: Implementation Notes (empty — agent fills this)
    lines.append("## 6. Implementation Notes")
    lines.append("*Agent fills this during implementation: approach, key decisions, file paths.*")
    lines.append("")

    return "\n".join(lines) + "\n"


def write_context_docs(contexts, project_dir):
    """Write Work Context Documents to WorkContexts/ directory."""
    output_dir = project_dir / "WorkContexts"
    output_dir.mkdir(exist_ok=True)

    written = []
    for ctx in contexts:
        filename = f"{ctx['bp_id']}_context.md"
        filepath = output_dir / filename
        content = generate_work_context_doc(ctx, project_dir)
        filepath.write_text(content, encoding="utf-8")
        written.append(filepath)

    return written


# ---------------------------------------------------------------------------
# Stage 3: Validation
# ---------------------------------------------------------------------------

def validate_contexts(project_dir):
    """Validate that generated Work Context Documents are complete.

    Returns a dict with:
      total: number of context docs found
      complete: number with all 4 spec sections filled
      incomplete: list of docs with gaps
      missing_tasks: BP tasks found in Blueprint but with no context doc
    """
    ctx_dir = project_dir / "WorkContexts"
    if not ctx_dir.exists():
        return {
            "total": 0,
            "complete": 0,
            "incomplete": [],
            "missing_tasks": [],
        }

    docs = list(ctx_dir.glob("BP-*_context.md"))
    complete = 0
    incomplete = []

    required_sections = [
        ("## 1. Why", "pvd"),
        ("## 2. What", "es"),
        ("## 3. How", "bp"),
        ("## 4. Proof", "tp"),
    ]

    for doc in docs:
        try:
            content = doc.read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            incomplete.append({"file": doc.name, "gaps": ["Could not read file"]})
            continue

        gaps = []
        for header, label in required_sections:
            if header in content:
                # Check if the section has real content (not just the placeholder)
                section_start = content.index(header)
                # Find next ## header
                next_section = content.find("\n## ", section_start + len(header))
                if next_section == -1:
                    section_body = content[section_start + len(header):]
                else:
                    section_body = content[section_start + len(header):next_section]

                if "NOT FOUND" in section_body or len(section_body.strip()) < 50:
                    gaps.append(f"{label}: Section exists but has no extracted content")
            else:
                gaps.append(f"{label}: Section header missing entirely")

        if gaps:
            incomplete.append({"file": doc.name, "gaps": gaps})
        else:
            complete += 1

    # Check for BP tasks without context docs
    missing = []
    bp_files = find_md_files(project_dir, ["Specs"])
    for f in bp_files:
        if "blueprint" not in f.name.lower():
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            continue
        for m in re.finditer(r'###\s+(BP-\d+\.\d+\.\d+):', content):
            bp_id = m.group(1)
            expected_file = ctx_dir / f"{bp_id}_context.md"
            if not expected_file.exists():
                missing.append(bp_id)

    return {
        "total": len(docs),
        "complete": complete,
        "incomplete": incomplete,
        "missing_tasks": missing,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract work context from spec chains")
    parser.add_argument("project_dir", help="Project root directory")
    parser.add_argument("--evaluate", action="store_true", help="Assess governance readiness")
    parser.add_argument("--extract", action="store_true", help="Extract work context documents")
    parser.add_argument("--validate", action="store_true", help="Validate extracted documents")
    parser.add_argument("--all", action="store_true", help="Run all stages")
    parser.add_argument("--json", action="store_true", help="Output as JSON (for skill consumption)")
    args = parser.parse_args()

    if not any([args.evaluate, args.extract, args.validate, args.all]):
        parser.print_help()
        sys.exit(2)

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(2)

    results = {}

    # --- Stage 1: Evaluate ---
    if args.evaluate or args.all or args.extract:
        readiness = evaluate_readiness(project_dir)
        results["evaluation"] = readiness

        if not args.json:
            print("=== GOVERNANCE READINESS ASSESSMENT ===")
            print(f"Route: {readiness['route']} (score: {readiness['score']}/100)")
            print()
            for detail in readiness["details"]:
                print(f"  {detail}")
            print()

            if readiness["cleanup_suggestions"]:
                print("CLEANUP RECOMMENDATIONS:")
                for s in readiness["cleanup_suggestions"]:
                    print(f"  - {s}")
                print()

            if readiness["route"] == "BLACK":
                print("CANNOT PROCEED: No specifications found. Write specs first.")
                if not args.all:
                    sys.exit(2)
            elif readiness["route"] == "RED":
                print("ROUTE: LLM-assisted extraction required (Tier 2).")
                print("Run /prepare-work to use the skill for LLM-powered extraction.")
            elif readiness["route"] == "YELLOW":
                print("ROUTE: Hybrid extraction — structural with LLM gap-filling.")
            else:
                print("ROUTE: Full structural extraction (Tier 1).")

        if args.evaluate and not args.all:
            if args.json:
                print(json.dumps(readiness, indent=2, default=str))
            sys.exit(0 if readiness["route"] in ("GREEN", "YELLOW") else 1 if readiness["route"] == "RED" else 2)

    # --- Stage 2: Extract ---
    if args.extract or args.all:
        readiness = results.get("evaluation") or evaluate_readiness(project_dir)

        if readiness["route"] == "BLACK":
            if not args.json:
                print("\nCANNOT EXTRACT: No specifications found.")
            sys.exit(2)

        if readiness["route"] in ("GREEN", "YELLOW"):
            # Tier 1: Structural extraction
            if not args.json:
                print("\n=== EXTRACTING WORK CONTEXTS (Tier 1: Structural) ===")

            contexts = structural_extract(project_dir, readiness["spec_files"])

            if contexts:
                written = write_context_docs(contexts, project_dir)
                results["extraction"] = {
                    "tier": 1,
                    "documents_written": len(written),
                    "with_gaps": sum(1 for c in contexts if c["gaps"]),
                    "total_gaps": sum(len(c["gaps"]) for c in contexts),
                }

                if not args.json:
                    print(f"  Generated {len(written)} Work Context Documents")
                    gap_count = results["extraction"]["with_gaps"]
                    if gap_count:
                        print(f"  {gap_count} documents have extraction gaps (marked for LLM fill)")
                    print(f"  Output: WorkContexts/")
            else:
                results["extraction"] = {"tier": 1, "documents_written": 0, "error": "No BP tasks found in Blueprint"}
                if not args.json:
                    print("  No BP tasks found in Blueprint. Nothing to extract.")

        elif readiness["route"] == "RED":
            # Tier 2: Prepare for LLM extraction
            llm_prep = prepare_llm_extraction(project_dir, readiness["spec_files"], readiness.get("id_counts", {}))
            results["extraction"] = {
                "tier": 2,
                "llm_preparation": llm_prep,
            }

            # Write the preparation file for the skill to consume
            prep_path = project_dir / "WorkContexts" / "_llm_extraction_prep.json"
            (project_dir / "WorkContexts").mkdir(exist_ok=True)
            prep_path.write_text(json.dumps(llm_prep, indent=2, default=str), encoding="utf-8")

            if not args.json:
                print("\n=== LLM EXTRACTION PREPARATION (Tier 2) ===")
                print(f"  Found {len(llm_prep['spec_inventory'])} spec files")
                print(f"  Preparation written to: WorkContexts/_llm_extraction_prep.json")
                print(f"  Run /prepare-work to complete LLM-assisted extraction")

    # --- Stage 3: Validate ---
    if args.validate or args.all:
        if not args.json:
            print("\n=== VALIDATING WORK CONTEXTS ===")

        validation = validate_contexts(project_dir)
        results["validation"] = validation

        if not args.json:
            print(f"  Total documents: {validation['total']}")
            print(f"  Complete (all 4 sections filled): {validation['complete']}")
            print(f"  Incomplete: {len(validation['incomplete'])}")

            if validation["incomplete"]:
                print("\n  INCOMPLETE DOCUMENTS:")
                for doc in validation["incomplete"]:
                    print(f"    {doc['file']}:")
                    for gap in doc["gaps"]:
                        print(f"      - {gap}")

            if validation["missing_tasks"]:
                print(f"\n  MISSING CONTEXT DOCS ({len(validation['missing_tasks'])} BP tasks with no context):")
                for bp_id in validation["missing_tasks"]:
                    print(f"    - {bp_id}")
            elif validation["total"] > 0:
                print("\n  All Blueprint tasks have context documents.")

    # --- Output ---
    if args.json:
        print(json.dumps(results, indent=2, default=str))

    # Exit code
    evaluation = results.get("evaluation", {})
    validation = results.get("validation", {})
    if evaluation.get("route") == "BLACK":
        sys.exit(2)
    elif validation.get("incomplete") or validation.get("missing_tasks"):
        sys.exit(1)
    elif evaluation.get("route") == "RED":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
