---
name: skill-creator
description: Create a new project-specific skill following the Agent Skills SDK format. Use when the user wants to add a new skill, create a slash command, capture a workflow as a reusable skill, or extend the project's skill library.
argument-hint: <skill-name>
---

# Skill Creator

This is a meta-skill — it creates new skills that extend the project's capabilities using the SDK-compliant Agent Skills format.

When invoked with a skill name (`$ARGUMENTS`):

1. **Ask the user** for the skill's purpose in one sentence.

2. **Create the skill directory** at `.claude/skills/$ARGUMENTS/` with a `SKILL.md` file.

3. **Use this SKILL.md template:**

   ```yaml
   ---
   name: {skill-name}
   description: {What the skill does and when to use it. Be specific — this is the primary trigger mechanism. Include keywords and contexts that should activate this skill. Max 1024 chars.}
   argument-hint: <{describe expected args}>
   ---
   ```

   Below the frontmatter, write the skill instructions in markdown:

   ```markdown
   # {Skill Title}

   When invoked with {describe expected arguments}:

   1. **{Context loading}** — What to read/load/check before starting.
   2. **{Core workflow}** — The main steps, numbered, with clear pass/fail criteria.
   3. **Report findings** as a table:
      | Category | Status | Details |
      |----------|--------|---------|
   4. **Verdict:** {PASS|CONDITIONAL|FAIL} with explanation.
   ```

4. **Required elements** (every skill must have these):
   - **YAML frontmatter:** `name` (kebab-case, max 64 chars) and `description` (max 1024 chars) are required
   - **Context loading:** Step 1 should read relevant specs or code before doing work
   - **Numbered steps:** Clear, sequential workflow (typically 4-6 steps)
   - **Reporting:** A findings table with status columns
   - **Verdict/outcome:** A clear final assessment (not just a list of findings)

5. **Frontmatter rules:**
   - `name` must be kebab-case: lowercase letters, numbers, hyphens only (`[a-z0-9-]+`)
   - `name` must match the parent directory name
   - No leading, trailing, or consecutive hyphens in `name`
   - `description` must not contain angle brackets (`<` or `>`)
   - `description` should be "pushy" — include contexts where the skill should trigger, even if the user doesn't explicitly name it
   - Optional: `argument-hint` for autocomplete hints, `disable-model-invocation: true` to prevent auto-loading

6. **Supporting directories** (create only if the skill needs them):
   - `scripts/` — Executable code for deterministic or repetitive tasks
   - `references/` — Documentation loaded on demand (keeps SKILL.md lean)
   - `assets/` — Templates, fonts, images used in output

7. **Style rules:**
   - Write instructions TO Claude (the skill's audience is a future Claude instance)
   - Explain the **why** behind instructions — reasoning is more effective than rigid MUSTs
   - Use imperative voice ("Read the spec", not "You should read the spec")
   - Be specific about what to grep/read/check — don't leave it vague
   - Include file paths or glob patterns where relevant
   - If the skill can FAIL in a way that should block work, say so explicitly
   - Keep SKILL.md under 500 lines; if longer, move details to `references/`

8. **After creating the skill**, add it to the CLAUDE.md skills table:
   ```markdown
   | {skill-name} | `/{skill-name} <args>` | {When to use — one phrase} |
   ```

9. **Test the skill** by invoking it once on a real or example module to verify the workflow makes sense.
