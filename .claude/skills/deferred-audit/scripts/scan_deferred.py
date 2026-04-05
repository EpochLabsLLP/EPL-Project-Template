#!/usr/bin/env python3
"""
Epoch Labs - Deferred Items Auditor
Scans spec files for deferred/follow-up sections and checks whether each item
was picked up by subsequent specs, Work Orders, or Gap Tracker entries.

Usage:
    python scan_deferred.py <project_dir>            # Full audit + ledger generation
    python scan_deferred.py <project_dir> --quick     # One-line status for hook use

Exit codes:
    0 = No orphaned items (clean)
    1 = Orphaned items found (items deferred but never picked up)
    2 = Script error
"""

import re
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path


# --- Section Detection ---
# These patterns match markdown headers that typically contain deferred/follow-up items.
# Case-insensitive matching. Must appear as markdown headers (##, ###, etc.) or as
# the first content in a section.
DEFERRED_SECTION_PATTERNS = [
    r'follow[\s-]?up',
    r'deferred',
    r'deferrals',
    r'future[\s-]?work',
    r'future[\s-]?implement',
    r'post[\s-]?phase',
    r'remaining[\s-]?work',
    r'remaining[\s-]?items',
    r'not[\s-]?yet[\s-]?(?:done|implement|schedul)',
    r'parking[\s-]?lot',
    r'backlog',
    r'open[\s-]?items',
    r'pending[\s-]?items',
    r'outstanding[\s-]?items',
    r'unresolved',
    r'left[\s-]?behind',
    r'carry[\s-]?over',
    r'to[\s-]?be[\s-]?(?:done|implement|schedul|address)',
]

# Compile into a single regex for header detection
SECTION_PATTERN = re.compile(
    r'^#{1,6}\s+.*(?:' + '|'.join(DEFERRED_SECTION_PATTERNS) + r')',
    re.IGNORECASE | re.MULTILINE
)

# Header pattern for detecting section boundaries
HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

# --- Item Extraction ---
# Patterns for extracting individual items from deferred sections
BULLET_PATTERN = re.compile(r'^\s*[-*]\s+(.+)$', re.MULTILINE)
NUMBERED_PATTERN = re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE)
# Table row: | content | priority | status | etc.
TABLE_ROW_PATTERN = re.compile(r'^\|\s*([^|]+?)\s*\|', re.MULTILINE)

# Skip patterns for table headers and separators
TABLE_SKIP = re.compile(r'^[\s|:-]+$|^\|\s*[-:]+')
TABLE_HEADER_KEYWORDS = {'task', 'item', 'description', 'priority', 'status', 'target', 'notes'}

# --- Stop Words for Keyword Extraction ---
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'can', 'need', 'must',
    'this', 'that', 'these', 'those', 'it', 'its', 'not', 'no', 'nor',
    'if', 'then', 'than', 'when', 'where', 'what', 'which', 'who', 'whom',
    'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
    'some', 'such', 'only', 'own', 'same', 'so', 'very', 'too', 'also',
    'just', 'into', 'out', 'up', 'down', 'about', 'after', 'before',
    'between', 'under', 'over', 'through', 'during', 'above', 'below',
    'any', 'as', 'new', 'low', 'high', 'medium', 'phase', 'see', 'per',
    'via', 'etc', 'e.g', 'i.e', 'vs', 'non', 'pre', 'post',
}

# --- Spec Filename Patterns ---
SKIP_FILES = {
    'Work_Ledger.md', 'gap_tracker.md', 'Deferred_Ledger.md',
    'SESSION_TEMPLATE.md',
}


def find_spec_files(project_dir):
    """Find all spec files worth scanning for deferred items."""
    spec_dir = project_dir / "Specs"
    files = []
    if not spec_dir.exists():
        return files

    for f in sorted(spec_dir.iterdir()):
        if not f.is_file() or f.suffix != '.md':
            continue
        if f.name.startswith('TEMPLATE_'):
            continue
        if f.name in SKIP_FILES:
            continue
        # Skip archived files
        if '_Archive' in str(f):
            continue
        files.append(f)

    # Also scan Testing/ for deferred items in test plans
    test_dir = project_dir / "Testing"
    if test_dir.exists():
        for f in sorted(test_dir.iterdir()):
            if not f.is_file() or f.suffix != '.md':
                continue
            if f.name.startswith('TEMPLATE_'):
                continue
            files.append(f)

    return files


def find_resolution_files(project_dir):
    """Find all files that could contain resolution evidence (downstream specs, WOs, gap tracker)."""
    files = []
    for search_dir in ['Specs', 'WorkOrders', 'Testing']:
        d = project_dir / search_dir
        if not d.exists():
            continue
        for f in d.rglob('*.md'):
            if f.name.startswith('TEMPLATE_'):
                continue
            if f.name in SKIP_FILES:
                continue
            files.append(f)
    return files


def extract_sections(content):
    """Extract all sections from markdown content, returning list of (header, level, body) tuples."""
    headers = list(HEADER_PATTERN.finditer(content))
    sections = []
    for i, match in enumerate(headers):
        level = len(match.group(1))
        header = match.group(2).strip()
        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        body = content[start:end].strip()
        sections.append((header, level, body))
    return sections


def is_deferred_section(header):
    """Check if a section header matches deferred-item patterns."""
    for pattern in DEFERRED_SECTION_PATTERNS:
        if re.search(pattern, header, re.IGNORECASE):
            return True
    return False


def extract_items_from_section(body):
    """Extract individual deferred items from a section body."""
    items = []

    # Try bullet points first
    bullets = BULLET_PATTERN.findall(body)
    if bullets:
        for b in bullets:
            text = b.strip()
            # Skip checked items (already done)
            if text.startswith('[x]') or text.startswith('[X]'):
                continue
            # Clean up checkbox markers
            text = re.sub(r'^\[[ ~DdXx]\]\s*', '', text)
            if len(text) > 10:  # Skip very short items (likely not meaningful)
                items.append(text)
        return items

    # Try numbered items
    numbered = NUMBERED_PATTERN.findall(body)
    if numbered:
        for n in numbered:
            text = n.strip()
            if len(text) > 10:
                items.append(text)
        return items

    # Try table rows
    rows = TABLE_ROW_PATTERN.findall(body)
    if rows:
        for r in rows:
            text = r.strip()
            # Skip header rows and separators
            if TABLE_SKIP.match(text):
                continue
            if text.lower() in TABLE_HEADER_KEYWORDS:
                continue
            if len(text) > 10:
                items.append(text)
        return items

    # Fallback: treat non-empty lines as items
    for line in body.split('\n'):
        line = line.strip()
        if line and len(line) > 15 and not line.startswith('#') and not line.startswith('|'):
            items.append(line)

    return items


def extract_keywords(text):
    """Extract significant keywords from item text for resolution matching."""
    # Remove markdown formatting
    clean = re.sub(r'[*_`\[\](){}|#>]', ' ', text)
    clean = re.sub(r'\b(https?://\S+)\b', '', clean)
    clean = re.sub(r'[^\w\s-]', ' ', clean)

    words = clean.lower().split()
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    return keywords


def check_resolution(item_text, item_keywords, source_file, resolution_files, gap_content, dr_content):
    """
    Check if a deferred item was resolved by downstream artifacts.

    Returns (status, evidence) where:
      status: 'RESOLVED' | 'ORPHANED' | 'ACKNOWLEDGED' | 'DONE'
      evidence: string describing where resolution was found (or empty)
    """
    if not item_keywords:
        return 'ORPHANED', ''

    source_name = source_file.name

    # Check if the item is marked as done/complete in its own text
    done_markers = ['done', 'complete', 'implemented', 'shipped', 'resolved', 'fixed']
    item_lower = item_text.lower()
    for marker in done_markers:
        if marker in item_lower and any(c in item_lower for c in ['[x]', 'done', 'complete']):
            return 'DONE', 'Marked as done in source'

    # Check Gap Tracker for acknowledgment
    if gap_content:
        match_count = sum(1 for kw in item_keywords if kw in gap_content.lower())
        if match_count >= min(3, len(item_keywords)):
            return 'ACKNOWLEDGED', 'Found in Gap Tracker'

    # Check Decision Records for formal deferral
    if dr_content:
        match_count = sum(1 for kw in item_keywords if kw in dr_content.lower())
        if match_count >= min(3, len(item_keywords)):
            return 'ACKNOWLEDGED', 'Found in Decision Record'

    # Check downstream specs and Work Orders
    best_match = 0
    best_file = ''

    for res_file in resolution_files:
        # Don't match against the source file itself
        if res_file.name == source_name:
            continue

        try:
            content = res_file.read_text(encoding='utf-8', errors='replace').lower()
        except (OSError, IOError):
            continue

        match_count = sum(1 for kw in item_keywords if kw in content)
        match_ratio = match_count / len(item_keywords) if item_keywords else 0

        if match_ratio > best_match:
            best_match = match_ratio
            best_file = res_file.name

    # Threshold: at least 60% of keywords must match, and at least 3 keywords
    if best_match >= 0.6 and sum(1 for kw in item_keywords if kw in best_file.lower() or True) >= 2:
        # Re-verify: need at least 3 matching keywords in the best file
        try:
            content = next(f for f in resolution_files if f.name == best_file).read_text(
                encoding='utf-8', errors='replace'
            ).lower()
            actual_matches = sum(1 for kw in item_keywords if kw in content)
            if actual_matches >= min(3, len(item_keywords)):
                return 'RESOLVED', f'Keywords matched in {best_file}'
        except (StopIteration, OSError):
            pass

    return 'ORPHANED', ''


def scan_project(project_dir):
    """
    Main scan function. Returns a dict with:
      - items: list of dicts with item details and status
      - summary: dict with counts
      - source_files: list of files that contained deferred sections
    """
    spec_files = find_spec_files(project_dir)
    resolution_files = find_resolution_files(project_dir)

    # Pre-load gap tracker and decision record content
    gap_file = project_dir / "Specs" / "gap_tracker.md"
    gap_content = ''
    if gap_file.exists():
        try:
            gap_content = gap_file.read_text(encoding='utf-8', errors='replace')
        except (OSError, IOError):
            pass

    dr_content = ''
    for f in (project_dir / "Specs").iterdir() if (project_dir / "Specs").exists() else []:
        if f.is_file() and 'decision_record' in f.name.lower():
            try:
                dr_content += f.read_text(encoding='utf-8', errors='replace') + '\n'
            except (OSError, IOError):
                pass

    all_items = []
    source_files = set()

    for spec_file in spec_files:
        try:
            content = spec_file.read_text(encoding='utf-8', errors='replace')
        except (OSError, IOError):
            continue

        sections = extract_sections(content)

        for header, level, body in sections:
            if not is_deferred_section(header):
                continue

            items = extract_items_from_section(body)
            if not items:
                continue

            source_files.add(spec_file.name)

            for item_text in items:
                keywords = extract_keywords(item_text)
                status, evidence = check_resolution(
                    item_text, keywords, spec_file,
                    resolution_files, gap_content, dr_content
                )

                all_items.append({
                    'source_file': spec_file.name,
                    'section': header,
                    'text': item_text,
                    'keywords': keywords,
                    'status': status,
                    'evidence': evidence,
                })

    # Summary
    counts = {'total': len(all_items)}
    for status in ['RESOLVED', 'ORPHANED', 'ACKNOWLEDGED', 'DONE']:
        counts[status.lower()] = sum(1 for i in all_items if i['status'] == status)

    return {
        'items': all_items,
        'summary': counts,
        'source_files': sorted(source_files),
    }


def generate_ledger(project_dir, results):
    """Generate the Deferred Items Ledger markdown file."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    counts = results['summary']
    items = results['items']

    lines = []
    lines.append('# Deferred Items Ledger')
    lines.append(f'Generated: {now}')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'- **Total deferred items found:** {counts["total"]}')
    lines.append(f'- **Resolved:** {counts["resolved"]} (picked up in subsequent specs/WOs)')
    lines.append(f'- **Orphaned:** {counts["orphaned"]} (never picked up — ACTION REQUIRED)')
    lines.append(f'- **Acknowledged:** {counts["acknowledged"]} (in Gap Tracker or Decision Record)')
    lines.append(f'- **Done:** {counts["done"]} (marked complete in source)')
    lines.append('')

    # Orphaned items first (most important)
    orphaned = [i for i in items if i['status'] == 'ORPHANED']
    if orphaned:
        lines.append('## Orphaned Items (ACTION REQUIRED)')
        lines.append('')
        lines.append('These items were deferred in completed specs but never picked up by any ')
        lines.append('subsequent Engineering Spec, Blueprint, Work Order, or Gap Tracker entry.')
        lines.append('Each must be either:')
        lines.append('1. Added to the Gap Tracker at the appropriate tier')
        lines.append('2. Assigned to a Work Order in the current or next phase')
        lines.append('3. Formally deferred via a Decision Record entry (with rationale)')
        lines.append('')

        # Group by source file
        by_source = {}
        for item in orphaned:
            src = item['source_file']
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(item)

        for src, src_items in by_source.items():
            lines.append(f'### From: `{src}`')
            lines.append('')
            lines.append('| Item | Section | Key Terms |')
            lines.append('|------|---------|-----------|')
            for item in src_items:
                # Truncate long items for table display
                text = item['text'][:100] + ('...' if len(item['text']) > 100 else '')
                text = text.replace('|', '\\|')
                kw = ', '.join(item['keywords'][:5])
                section = item['section'].replace('|', '\\|')
                lines.append(f'| {text} | {section} | {kw} |')
            lines.append('')

    # Acknowledged items
    acknowledged = [i for i in items if i['status'] == 'ACKNOWLEDGED']
    if acknowledged:
        lines.append('## Acknowledged Items')
        lines.append('')
        lines.append('These items appear in the Gap Tracker or a Decision Record. No action needed ')
        lines.append('unless the gap tracker entry is stale or the DR decision has changed.')
        lines.append('')
        lines.append('| Item | Source | Evidence |')
        lines.append('|------|--------|----------|')
        for item in acknowledged:
            text = item['text'][:80] + ('...' if len(item['text']) > 80 else '')
            text = text.replace('|', '\\|')
            lines.append(f'| {text} | {item["source_file"]} | {item["evidence"]} |')
        lines.append('')

    # Resolved items
    resolved = [i for i in items if i['status'] == 'RESOLVED']
    if resolved:
        lines.append('## Resolved Items')
        lines.append('')
        lines.append('These items were picked up by downstream specs or Work Orders.')
        lines.append('')
        lines.append('| Item | Source | Resolved In |')
        lines.append('|------|--------|-------------|')
        for item in resolved:
            text = item['text'][:80] + ('...' if len(item['text']) > 80 else '')
            text = text.replace('|', '\\|')
            lines.append(f'| {text} | {item["source_file"]} | {item["evidence"]} |')
        lines.append('')

    # Done items
    done = [i for i in items if i['status'] == 'DONE']
    if done:
        lines.append('## Completed Items')
        lines.append('')
        lines.append('| Item | Source |')
        lines.append('|------|--------|')
        for item in done:
            text = item['text'][:80] + ('...' if len(item['text']) > 80 else '')
            text = text.replace('|', '\\|')
            lines.append(f'| {text} | {item["source_file"]} |')
        lines.append('')

    # Write ledger
    ledger_path = project_dir / "Specs" / "Deferred_Ledger.md"
    ledger_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    return ledger_path


def main():
    parser = argparse.ArgumentParser(description='Scan specs for deferred/follow-up items')
    parser.add_argument('project_dir', help='Project root directory')
    parser.add_argument('--quick', action='store_true',
                        help='One-line status output (for hook use)')
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(2)

    specs_dir = project_dir / "Specs"
    if not specs_dir.exists():
        if args.quick:
            print("Deferred audit: No Specs/ directory")
        sys.exit(0)

    try:
        results = scan_project(project_dir)
    except Exception as e:
        print(f"Error during scan: {e}", file=sys.stderr)
        sys.exit(2)

    orphaned_count = results['summary']['orphaned']
    total_count = results['summary']['total']

    if args.quick:
        if total_count == 0:
            print("Deferred audit: No deferred items found in specs")
            sys.exit(0)
        elif orphaned_count == 0:
            print(f"Deferred audit: CLEAN — {total_count} deferred items, all resolved or acknowledged")
            sys.exit(0)
        else:
            source_count = len(set(i['source_file'] for i in results['items'] if i['status'] == 'ORPHANED'))
            print(f"Deferred audit: {orphaned_count} orphaned item(s) across {source_count} spec(s) — run /deferred-audit")
            sys.exit(1)
    else:
        # Full mode: generate ledger and print summary
        ledger_path = generate_ledger(project_dir, results)

        print(f"=== DEFERRED ITEMS AUDIT ===")
        print(f"Scanned: {len(results['source_files'])} spec files with deferred sections")
        print(f"Total items: {total_count}")
        print(f"  Resolved:     {results['summary']['resolved']}")
        print(f"  Acknowledged: {results['summary']['acknowledged']}")
        print(f"  Done:         {results['summary']['done']}")
        print(f"  ORPHANED:     {orphaned_count}")
        print(f"")
        print(f"Ledger written to: {ledger_path.relative_to(project_dir)}")

        if orphaned_count > 0:
            print(f"")
            print(f"WARNING: {orphaned_count} deferred item(s) were never picked up.")
            print(f"Review Specs/Deferred_Ledger.md and address each orphaned item.")

        sys.exit(1 if orphaned_count > 0 else 0)


if __name__ == '__main__':
    main()
