---
name: prepare-work
description: Evaluate governance readiness, extract spec chains into per-task Work Context Documents, and validate completeness. Pre-builds everything an implementing agent needs so they never have to navigate 5 spec files themselves. Run before starting a wave or phase.
user-invocable: true
---

# prepare-work

Prepares the implementation environment by extracting the full spec chain (PVD → ES → BP → TP) into per-task Work Context Documents. Each document bundles everything an implementing agent needs for one Blueprint task — the product requirement, engineering spec, task card, test scenarios, and acceptance checklist — in a single, focused file.

## Why This Exists

Agents produce higher-quality implementations when given pre-decomposed, fully-specified tasks vs. having to derive context from high-level specs. Research shows:
- Agent performance degrades after ~35 minutes of sustained work — atomic, focused tasks prevent drift
- LLMs can identify irrelevant content but cannot ignore it — pre-extraction prevents context pollution
- Agents that must navigate 5+ spec files silently drop requirements they don't find — pre-extraction makes gaps visible before implementation

The most common pattern in critical-review findings is "spec requirement silently dropped" — the agent never said "I'm skipping this," it just didn't build it. Pre-extraction makes every requirement explicit in the implementing agent's context.

## When to Use

- **Before starting a new wave** — generate context docs for all tasks in the wave
- **Before starting a new phase** — generate context docs for the entire Blueprint
- **When onboarding a new agent** — the context docs are self-contained, no prior project knowledge needed
- **After spec revisions** — regenerate to pick up changes

## How to Invoke

```
/prepare-work
```

## Execution

### Stage 1: Evaluate Governance Readiness

Run the evaluation:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/prepare-work/scripts/extract_work_context.py" "$CLAUDE_PROJECT_DIR" --evaluate
```

This produces a readiness score and route recommendation:

| Route | Score | Meaning | Action |
|-------|-------|---------|--------|
| **GREEN** | 80-100 | Well-governed repo, clean spec chains | Proceed to Tier 1 extraction |
| **YELLOW** | 40-79 | Partial governance, some chains broken | Tier 1 extraction + LLM fills gaps |
| **RED** | 1-39 | Messy repo, custom conventions | Full LLM-assisted extraction |
| **BLACK** | 0 | No specs exist | STOP — write specs first |

**If cleanup suggestions are reported**, present them to the user. Archiving superseded specs, old sessions, and research docs before extraction improves both the script's accuracy and the implementing agent's focus.

### Stage 2: Extract (route-dependent)

#### GREEN/YELLOW Route (Tier 1: Structural)

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/prepare-work/scripts/extract_work_context.py" "$CLAUDE_PROJECT_DIR" --extract
```

The script structurally parses the spec chain and generates Work Context Documents in `WorkContexts/`. Each document contains 5 pre-extracted sections plus an acceptance checklist.

**For YELLOW routes:** Some documents will have gaps (marked with `[NOT FOUND]`). After the script runs, read each gapped document and fill the missing sections by reading the actual spec files. The script tells you exactly which chain links are broken.

#### RED Route (Tier 2: LLM-Assisted)

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/prepare-work/scripts/extract_work_context.py" "$CLAUDE_PROJECT_DIR" --extract
```

The script writes `WorkContexts/_llm_extraction_prep.json` with a spec inventory and content summaries. Use this to perform LLM-assisted extraction:

1. Read the preparation file
2. Read each spec file listed in the inventory
3. For each identifiable task/work unit in the specs, create a Work Context Document manually by extracting:
   - The product requirement it traces to (the *why*)
   - The technical specification (the *what*)
   - The task definition with acceptance criteria (the *how to verify*)
   - The test scenarios (the *proof*)
   - A pre-structured acceptance checklist

Write each as `WorkContexts/TASK-{id}_context.md` following the same format as Tier 1 output.

### Stage 3: Validate

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/prepare-work/scripts/extract_work_context.py" "$CLAUDE_PROJECT_DIR" --validate
```

Checks every Work Context Document for completeness:
- All 4 spec sections must have real content (not just placeholders)
- Every Blueprint task must have a corresponding context document
- Reports gaps that need to be filled before implementation begins

### Full Pipeline

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/prepare-work/scripts/extract_work_context.py" "$CLAUDE_PROJECT_DIR" --all
```

Runs evaluate → extract → validate in sequence.

## Work Context Document Format

Each generated document at `WorkContexts/{BP-id}_context.md` contains:

```markdown
# Work Context: BP-N.M.T — Task Title
Generated: YYYY-MM-DD HH:MM
Traceability: PVD-N → ES-N.M → BP-N.M.T → TP-N.M.T

## 1. Why — Product Requirement
[Full PVD-N section extracted from the product spec]

## 2. What — Engineering Specification
[Full ES-N.M section extracted from the Engineering Spec]

## 3. How — Blueprint Task Card
[Full BP-N.M.T task card with type, wave, dependencies, acceptance criteria]

## 4. Proof — Test Scenarios
[Full TP-N.M.T section extracted from Testing Plans]

## 5. Acceptance Checklist
- [ ] GIVEN/WHEN/THEN criteria extracted from Blueprint
- [ ] ...

## 6. Implementation Notes
[Agent fills this during implementation]
```

## How to Feed Work Context to Agents

**One task at a time.** Read the Work Context Document for the next BP task, then implement. Do not load all context docs at once — that reintroduces context pollution.

The `/work` skill's Step 7 (EXECUTE) should begin with:
1. Check if `WorkContexts/{BP-id}_context.md` exists for the current WO's Blueprint task
2. If yes: read it — this is the complete specification context for this task
3. If no: run `/spec-lookup` as before (backward compatible)

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `/trace-check` | Validates chain health — `/prepare-work` consumes the same chain |
| `/spec-lookup` | Loads spec context on demand — Work Context Documents pre-extract this |
| `/work` | Picks up and executes WOs — checks for Work Context Documents first |
| `/critical-review` | Reviews spec fidelity after implementation — Work Context Documents make the spec explicit upfront |
| `/init-doc wo` | Creates Work Orders — Work Context Documents supplement WOs with full spec chain |
