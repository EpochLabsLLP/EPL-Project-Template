---
name: spec-lookup
description: Load the primary and supporting specs for a given module before working on it. Use when starting work on any module, when you need to understand requirements, interface contracts, or constraints for a module, or when checking what a module should do before reviewing or implementing it.
argument-hint: <module>
---

# Spec Lookup

When invoked with a module name (`$ARGUMENTS`):

1. **Check for a module-to-spec lookup map.** Search for a table mapping modules to specs in:
   - `Specs/module_spec_map.md` (if it exists)
   - The Engineering Spec's module breakdown section
   - The PVD's architecture section

2. **If a map exists**, read the primary spec and all supporting specs listed for this module.

3. **If no map exists**, search for the most relevant specs:
   - Glob for `Specs/*{module_name}*` files
   - Read the PVD table of contents for sections mentioning this module
   - Read the Engineering Spec for this module's section

4. **Present a summary** to the user:
   - Module name and purpose (from spec)
   - Key requirements (bulleted list)
   - Interface contracts (inputs, outputs, dependencies)
   - Constraints or special rules that apply
   - Related modules that interact with this one

5. **Keep the specs loaded in context** for follow-up work. Do NOT summarize away details — the user likely wants to implement against these specs next.
