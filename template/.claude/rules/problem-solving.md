<!-- AGENT INSTRUCTION: This is the mandatory problem-solving protocol.
     Follow these tiers IN ORDER. Do not skip tiers.
     The hard cap of 3 actions per tier prevents runaway debugging loops
     that burn through context without making progress.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# Problem-Solving Protocol

## Rules
- Follow tiers in order. Do NOT skip to a higher tier.
- **Maximum 3 actions per tier.** If 3 actions at a tier don't resolve it, escalate.
- *Intent: Prevents runaway debugging spirals that consume context budget without progress. Forces structured escalation rather than increasingly desperate attempts.*

## Tier 1: Read and Trace (3 actions max)
1. Read the error message carefully — full stack trace, not just the summary
2. Trace the error to the source file and line number
3. Check the immediate code context for obvious issues

If unresolved after 3 actions → move to Tier 2.

## Tier 2: Consult Internal Resources (3 actions max)
1. Read the relevant project spec (use module-to-spec lookup if available)
2. Check related code for established patterns that should be followed
3. Review recent changes to the affected area (git log/diff)

If unresolved after 3 actions → move to Tier 3.

## Tier 3: Consult External Resources (3 actions max)
1. Search official documentation (use Context7 MCP if available, or WebFetch)
2. Check authoritative reference implementations
3. Search for known issues/solutions in the framework's issue tracker

If unresolved after 3 actions → move to Tier 4.

## Tier 4: Escalate to Nathan
- Present what you tried (tiers 1-3 summary)
- Present what you think the issue is
- Present 2-3 possible approaches if you have them
- Ask for guidance before proceeding
