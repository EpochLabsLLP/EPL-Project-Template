#!/usr/bin/env python3
"""
Detect the current SDD workflow phase from project state.

Phase is DERIVED from governance artifacts (frozen specs, WO statuses),
not declared by the agent. This eliminates drift — the phase IS the state.

Phases:
  SPEC           - Any required frozen spec missing
  PLANNING       - All specs frozen, no WOs or all PENDING
  IMPLEMENTATION - Any WO IN-PROGRESS
  VALIDATION     - Any WO in VALIDATION, none IN-PROGRESS
  MAINTENANCE    - All WOs DONE, all specs frozen

Usage:
  python detect_phase.py [project_dir]
  Output: single word (SPEC, PLANNING, IMPLEMENTATION, VALIDATION, MAINTENANCE)

Caches result for 5 seconds to avoid re-scanning on consecutive hook calls.
"""

import os
import sys
import time
import json
import re

def detect_phase(project_dir):
    specs_dir = os.path.join(project_dir, 'Specs')
    wo_dir = os.path.join(project_dir, 'WorkOrders')
    testing_dir = os.path.join(project_dir, 'Testing')

    # --- Check cache (5 second TTL) ---
    cache_file = os.path.join(project_dir, '.claude', 'observability', '.phase_cache')
    try:
        if os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < 5:
                with open(cache_file, 'r') as f:
                    return f.read().strip()
    except (IOError, OSError):
        pass

    # --- Check frozen specs ---
    has_pvd = False
    has_brief = False
    has_prd = False
    has_es = False
    has_bp = False
    has_tp = False

    if os.path.isdir(specs_dir):
        for fname in os.listdir(specs_dir):
            if fname.startswith('TEMPLATE_'):
                continue
            fpath = os.path.join(specs_dir, fname)
            if not os.path.isfile(fpath):
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    head = f.read(2000)
                is_frozen = bool(re.search(r'FROZEN', head, re.IGNORECASE))
            except (IOError, OSError):
                continue

            fname_upper = fname.upper()
            if 'PVD' in fname_upper and is_frozen:
                has_pvd = True
            if 'PRODUCT_BRIEF' in fname_upper and is_frozen:
                has_brief = True
            if 'PRD' in fname_upper and 'PRODUCT' not in fname_upper and is_frozen:
                has_prd = True
            if 'ENGINEERING_SPEC' in fname_upper and is_frozen:
                has_es = True
            if 'BLUEPRINT' in fname_upper and is_frozen:
                has_bp = True

    if os.path.isdir(testing_dir):
        for fname in os.listdir(testing_dir):
            if fname.startswith('TEMPLATE_'):
                continue
            fpath = os.path.join(testing_dir, fname)
            if not os.path.isfile(fpath):
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    head = f.read(2000)
                if re.search(r'FROZEN', head, re.IGNORECASE):
                    has_tp = True
            except (IOError, OSError):
                continue

    # Path A: PVD frozen, or Path B: Brief + PRD frozen
    has_product_spec = has_pvd or (has_brief and has_prd)
    all_specs_frozen = has_product_spec and has_es and has_bp and has_tp

    if not all_specs_frozen:
        phase = 'SPEC'
    else:
        # --- Check WO statuses ---
        wo_statuses = []
        if os.path.isdir(wo_dir):
            for fname in os.listdir(wo_dir):
                if fname.startswith('TEMPLATE_') or '_Archive' in fname:
                    continue
                if not fname.endswith('.md'):
                    continue
                fpath = os.path.join(wo_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        head = f.read(1000)
                    # Extract status
                    m = re.search(r'\*\*Status\*\*[:\s|]*\s*([\w-]+)', head)
                    if m:
                        wo_statuses.append(m.group(1).upper().strip())
                except (IOError, OSError):
                    continue

        has_in_progress = 'IN-PROGRESS' in wo_statuses
        has_validation = 'VALIDATION' in wo_statuses
        all_done = all(s == 'DONE' for s in wo_statuses) if wo_statuses else False

        if not wo_statuses:
            phase = 'PLANNING'
        elif has_in_progress:
            phase = 'IMPLEMENTATION'
        elif has_validation and not has_in_progress:
            phase = 'VALIDATION'
        elif all_done:
            phase = 'MAINTENANCE'
        else:
            phase = 'PLANNING'

    # --- Write cache ---
    try:
        cache_dir = os.path.dirname(cache_file)
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, 'w') as f:
            f.write(phase)
    except (IOError, OSError):
        pass

    return phase


if __name__ == '__main__':
    project_dir = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('CLAUDE_PROJECT_DIR', '.')
    try:
        print(detect_phase(project_dir))
    except Exception:
        print('UNKNOWN')
