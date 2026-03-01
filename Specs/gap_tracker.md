<!-- AGENT INSTRUCTION: This is the project's tiered work tracking document.
     It is the single source of truth for "what needs to be done and in what order."

     MAINTENANCE: Update this file as you complete work during sessions.
     - Check off items: change `- [ ]` to `- [x]`
     - Add new items discovered during implementation to the appropriate tier
     - Respect the scope guards — tier ordering is mandatory

     The SessionStart hooks read this file automatically. Keep it current.

     WHEN CREATING A NEW PROJECT: Delete the example text under each tier
     and add real deliverables from the PVD and Engineering Spec using
     the format: - [ ] Description of work item -->

# Gap Tracker — {ProjectName}
**Phase:** {Current Phase Name}
**Last Updated:** {YYYY-MM-DD}

---

## Scope Guards (MANDATORY)
- Do NOT work on Tier 1 items while any Tier 0 items remain open
- Do NOT work on Tier 2 items while any Tier 1 items remain open
- Do NOT work on Tier 3 items while any Tier 2 items remain open
- Exception: Nathan can explicitly authorize out-of-order work (log in mission-lock deviation log)

---

## Tier 0: Critical Defects
<!-- MUST fix before any other work. These are blocking issues — broken builds,
     data loss risks, security vulnerabilities, or crashes.
     Example entries:
       Fix [specific critical bug]
       Resolve [security vulnerability] -->

## Tier 1: Functional Gaps
<!-- Required for current phase completion. These are features or behaviors
     specified in the PVD/Engineering Spec that aren't implemented yet.
     Example entries:
       Implement [feature from PVD section X.Y]
       Complete [module] per Engineering Spec
       Wire up [integration point] -->

## Tier 2: Quality Improvements
<!-- Required before phase sign-off. Test coverage, error handling,
     performance targets, accessibility, polish.
     Example entries:
       Increase test coverage on [module] to [target]%
       Add error handling for [edge case]
       Meet performance target: [specific metric] -->

## Tier 3: Enhancements
<!-- Nice to have. Can defer to a future phase without blocking sign-off.
     Optimizations, developer experience improvements, non-critical polish.
     Example entries:
       Add keyboard shortcuts for [common actions]
       Optimize [operation] for large datasets
       Improve [UI element] visual polish -->

---

## Completed Items Archive
<!-- Move checked-off items here periodically to keep the active tiers clean.
     Format: YYYY-MM-DD | Tier | Description -->

| Date | Tier | Item |
|------|------|------|
