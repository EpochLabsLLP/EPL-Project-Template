---
name: security-review
description: OWASP-style security audit for modules handling sensitive data, authentication, authorization, or external input. Use when reviewing modules that handle user data, auth flows, API endpoints, file uploads, or any external-facing functionality. Also use when a security concern is discovered during development.
argument-hint: <module>
---

# Security Review

When invoked with a module name (`$ARGUMENTS`):

1. **Read all source files** in the module.

2. **Check each category** (report pass/fail with evidence):

   **Secrets Management**
   - No hardcoded API keys, tokens, passwords, or connection strings
   - Secrets loaded from environment variables or secure vault
   - No secrets in logs, error messages, or user-facing output

   **Input Validation**
   - All external input validated before use (user input, API params, file uploads)
   - Validation rejects invalid input rather than trying to sanitize
   - No trust of client-side validation alone

   **Injection Prevention**
   - No string concatenation for SQL queries (use parameterized queries)
   - No unescaped user input in HTML output (XSS)
   - No user input in shell commands (command injection)
   - No user input in file paths without sanitization (path traversal)

   **Authentication & Authorization**
   - Auth checks on every protected endpoint/action
   - Principle of least privilege applied
   - Session management follows best practices (secure cookies, expiry, rotation)

   **Data Protection**
   - Sensitive data encrypted at rest and in transit (TLS everywhere)
   - PII handled according to applicable regulations
   - No sensitive data in URLs, query strings, or browser storage

   **Error Handling**
   - Errors don't leak internal details (stack traces, DB schemas, file paths)
   - Failed operations don't leave system in insecure state
   - Rate limiting on authentication endpoints

3. **Report findings:**
   | Category | Status | Finding | Severity |
   |----------|--------|---------|----------|

   Severity levels: CRITICAL (fix immediately), HIGH (fix before shipping), MEDIUM (fix soon), LOW (track for later).

4. **If any CRITICAL or HIGH findings:** Flag to Nathan immediately per escalation rules.
