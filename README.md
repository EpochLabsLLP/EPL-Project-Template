# Project Governance Workshop

Development workspace for the [EPL Project Template](https://github.com/EpochLabsLLP/EPL-Project-Template) — an SDD governance framework for AI-assisted software development by Epoch Labs, LLP.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `template/` | The product — git subtree of EPL-Project-Template |
| `Sessions/` | Development session notes and records |
| `Specs/` | Workshop-level specs and tracking |

## Related Repos

- **[EPL-Project-Template](https://github.com/EpochLabsLLP/EPL-Project-Template)** — The template product (extracted as subtree here)
- **[EPL-Test-Project](https://github.com/EpochLabsLLP/EPL-Test-Project)** — Standalone test project for validating governance

## What's in the Template

The EPL Project Template provides a complete governance framework:

- **10 hooks** — Automated enforcement (code-gate, commit-gate, dep-gate, session heartbeat)
- **6 rules** — Always-loaded project rules (change control, execution protocol, quality gates)
- **15 skills** — Slash commands for spec lookup, code review, module completion, and more
- **9 spec templates** — PVD, Engineering Spec, Blueprint, Testing Plans, Work Orders, etc.
- **Traceability system** — Automated validation of PVD → ES → BP → TP → WO chains
- **Template sync** — `template_sync.py` for propagating template updates to projects

## License

Proprietary — Epoch Labs, LLP. All rights reserved.
