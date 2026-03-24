---
name: dep-check
description: Check a dependency for license, security, maintenance, and compatibility before adding it to the project. Use before adding ANY new dependency, when evaluating a library or package, or when unsure whether a dependency's license is permissive enough for commercial use.
argument-hint: <dependency-name>
---

# Dependency Check

Before adding ANY new dependency to the project, run this check. Adding a dependency without this check requires Nathan's explicit approval.

When invoked with a dependency name (`$ARGUMENTS`):

1. **License check (BLOCKING):**
   - Look up the dependency's license
   - PASS: Apache 2.0, MIT, BSD (2-clause or 3-clause), ISC, Unlicense, CC0
   - FAIL: GPL, LGPL, AGPL, SSPL, or any copyleft license
   - WARN: MPL 2.0 (file-level copyleft — acceptable with caution)
   - If FAIL -> STOP. Do not add this dependency. Report to Nathan.

2. **Security check:**
   - Search for known vulnerabilities (CVEs) via web search
   - Check if the package has had recent security advisories
   - Note: no critical/high CVEs is required; medium/low is acceptable with awareness

3. **Maintenance check:**
   - Last release date (warn if >12 months ago)
   - Open issue count vs. closed ratio
   - Number of maintainers (warn if single maintainer)
   - Download/usage stats if available

4. **Compatibility check:**
   - Does it conflict with existing dependencies?
   - What's the bundle size / dependency tree impact?
   - Does it support the project's target platforms?

5. **Report:**
   | Check | Status | Details |
   |-------|--------|---------|
   | License | PASS/FAIL/WARN | {license name} |
   | Security | PASS/WARN | {CVE count or clean} |
   | Maintenance | PASS/WARN | {last release, maintainers} |
   | Compatibility | PASS/WARN | {conflicts, size impact} |

   **Verdict:** APPROVED, CONDITIONAL (explain), or REJECTED (explain).
