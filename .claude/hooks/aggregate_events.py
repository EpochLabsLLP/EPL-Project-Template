#!/usr/bin/env python3
"""
Aggregate governance events from events.jsonl into session metrics.

Called by session-start.sh to compute and display compliance stats
from the previous session's governance events.

Reads:  .claude/observability/events.jsonl
Writes: .claude/observability/session_metrics.json
Output: One-line summary to stdout for session-start hook display

Fail-open: if anything goes wrong, output nothing and exit 0.
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime

def main():
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    obs_dir = os.path.join(project_dir, '.claude', 'observability')
    events_file = os.path.join(obs_dir, 'events.jsonl')
    metrics_file = os.path.join(obs_dir, 'session_metrics.json')

    if not os.path.exists(events_file):
        return  # No events yet

    # Read all events
    events = []
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (IOError, OSError):
        return

    if not events:
        return

    # Compute metrics
    gate_events = [e for e in events if e.get('event', '').startswith('gate.')]
    session_events = [e for e in events if e.get('event', '').startswith('session.')]

    total_gates = len(gate_events)
    blocks = [e for e in gate_events if e.get('decision') == 'block']
    allows = [e for e in gate_events if e.get('decision') == 'allow']
    total_blocks = len(blocks)
    total_allows = len(allows)

    # Compliance rate
    compliance = (total_allows / total_gates * 100) if total_gates > 0 else 100

    # Block distribution
    block_types = Counter(e.get('event', 'unknown') for e in blocks)

    # Session lifecycle
    compactions = len([e for e in session_events if e.get('event') == 'session.compact'])
    sessions = len([e for e in session_events if e.get('event') == 'session.start'])

    # Build metrics object
    metrics = {
        'computed_at': datetime.utcnow().isoformat() + 'Z',
        'total_events': len(events),
        'total_gate_events': total_gates,
        'total_blocks': total_blocks,
        'total_allows': total_allows,
        'compliance_pct': round(compliance, 1),
        'block_distribution': dict(block_types),
        'sessions': sessions,
        'compactions': compactions,
    }

    # Write metrics file
    try:
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)
    except (IOError, OSError):
        pass

    # Output summary line for session-start hook
    block_summary = ''
    if total_blocks > 0:
        top_blocks = block_types.most_common(3)
        block_summary = ' | Blocks: ' + ', '.join(
            f'{count} {typ.replace("gate.", "")}' for typ, count in top_blocks
        )

    compact_summary = f' | Compactions: {compactions}' if compactions > 0 else ''

    print(f'Compliance: {compliance:.0f}% ({total_allows}/{total_gates} allowed){block_summary}{compact_summary}')

    # Rotate events file if over 1MB
    try:
        if os.path.getsize(events_file) > 1_000_000:
            rotated = events_file + '.' + datetime.utcnow().strftime('%Y%m%d') + '.bak'
            os.rename(events_file, rotated)
    except (IOError, OSError):
        pass

if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # Fail-open: never crash the session hook
