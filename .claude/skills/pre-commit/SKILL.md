---
name: pre-commit
description: Pre-commit hygiene checklist including secrets scan, prohibited content check, file hygiene, build verification, and test verification. Use before every git commit, when preparing to commit staged changes, or when you want to verify nothing problematic is about to be committed.
---

# Pre-Commit

When invoked (no arguments needed):

1. **Check the staged diff.** Run `git diff --cached` to see what's being committed.

2. **Secrets scan** (BLOCKING):
   - Grep the diff for patterns: API keys, tokens, passwords, connection strings
   - Patterns to flag: `sk-`, `pk_`, `secret`, `password`, `token`, `Bearer `, base64 strings >40 chars
   - Check for `.env` files in the staged changes
   - If ANY secret found -> FAIL. Do not proceed with commit.

3. **Prohibited content** (BLOCKING):
   - No TODO/FIXME comments in newly added lines
   - No `console.log` / `print()` debug statements in production code (test files exempt)
   - No commented-out code blocks (>3 consecutive commented lines)
   - If found -> report with file:line references. Recommend fixing before commit.

4. **File hygiene:**
   - No files that should be gitignored (check against `.gitignore` patterns)
   - No binary files accidentally staged (images, compiled artifacts)
   - No files larger than 1MB staged

5. **Build verification:**
   - If a build command exists (check package.json scripts, Makefile, build.gradle), run it
   - Report: builds clean, builds with warnings, or build fails

6. **Test verification:**
   - If a test command exists, run it
   - Report: all pass, some fail (list which), or no tests configured

7. **Report:**
   | Check | Status | Details |
   |-------|--------|---------|
   | Secrets | PASS/FAIL | {findings} |
   | Prohibited content | PASS/WARN | {findings} |
   | File hygiene | PASS/WARN | {findings} |
   | Build | PASS/FAIL/SKIP | {result} |
   | Tests | PASS/FAIL/SKIP | {result} |

   **Verdict:** CLEAR TO COMMIT or ISSUES FOUND (list blockers).
