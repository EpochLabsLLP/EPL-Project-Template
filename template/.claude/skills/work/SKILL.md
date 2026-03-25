---
name: work
description: Unified work pickup and execution sequence. Reads project state, picks up the next available Work Order, and executes the full lifecycle autonomously. Designed for both unattended CLI heartbeats and interactive VS Code sessions.
user-invocable: true
---

# work

Autonomous work pickup and execution. This is the primary entry point for agents that need to find and do work without human direction.

**This skill is designed for unattended operation.** Do not ask for permission to proceed. Do not wait for approval. Read the project state, pick up work, and execute. If you encounter a genuine blocker that prevents progress (not uncertainty — a real blocker), escalate per Step 8. Otherwise, keep working.

## When to Use

- CLI heartbeat agents waking up with no specific task
- VS Code sessions starting with "continue where we left off" or "do work"
- Any time you need to figure out what to work on next
- After completing a Work Order and ready for the next one

## How to Invoke

```
/work
```

## Execution

Follow all 8 steps in order. Do not skip steps. Do not ask for confirmation between steps — the sequence is designed to be self-contained.

---

### Step 1: CHECK STOP-WORK

Read `.claude/stop-work.md`. If it exists:
- Display the reason
- Send notification to PM via `/mail Epoch-PM` with the stop-work details
- **HALT. Do not continue.** Only Nathan or the issuing instance can clear this file.

If the file does not exist, proceed silently.

---

### Step 2: CHECK PROGRESS LOG

Read the last 20 lines of `.claude/progress.log`.

- Note what other instances have done recently
- If entries show another instance is actively working (timestamp within last 30 minutes): note which WOs they're touching — you must not touch those
- If entries show completed WOs: those are done, factor into your WO selection

Do not output a summary of the log. Internalize the context and proceed.

---

### Step 2.5: CHECK MAIL LEDGER

Read `.claude/mail-ledger.md` (last 10 lines). If the file doesn't exist, skip this step.

- Look for entries with `status:pending` — these are messages that were received but not yet acted on
- If any pending messages have `priority: urgent` (check the original file in `.claude/inbox/_processed/`): address them NOW before picking up work. Run `/mail --check` if needed.
- If pending messages are `priority: normal`: note them but proceed — handle after current WO completes or during Step 6 if no WOs are available
- If no pending entries: good, proceed silently

Do not output a summary. Internalize and proceed.

---

### Step 3: CHECK CHECKPOINT

Read `.claude/checkpoint.md`.

- **If it shows active work from YOUR instance ID:** Resume that work. Skip to Step 7 (Execute) and continue from where the checkpoint left off. Re-read every file listed in "Files In Progress" before editing anything.
- **If it shows active work from ANOTHER instance:** Do NOT resume it. That instance may still be running. Note the WO it's working on (you must not touch it) and proceed to Step 4.
- **If it shows "No active work" or doesn't exist:** Proceed to Step 4.

---

### Step 4: CHECK WORK LEDGER

Run `/trace-check` to refresh the Work Ledger, then read `Specs/Work_Ledger.md`.

Identify:
- Which WOs are DONE
- Which WOs are IN-PROGRESS (and who owns them — check instance stamps in filenames)
- Which WOs are PENDING
- Which WOs are FAILED

If no Work Ledger exists or no specs are frozen, check the Gap Tracker (`Specs/gap_tracker.md`) for non-WO work items. If neither exists, skip to Step 8 (Escalate) with "No work found — no frozen specs, no WOs, no gap tracker items."

---

### Step 5: EVALUATE IN-PROGRESS WOs

For each IN-PROGRESS WO:
- **Assigned to your instance:** Continue it. Skip to Step 7.
- **Assigned to another instance with recent activity (progress.log entry <2h old):** Skip it. That agent is working on it.
- **Assigned to another instance with stale activity (>2h, no progress.log update):** Flag it in progress.log as "potentially abandoned" but do NOT take it over. Move to Step 6.

---

### Step 6: PICK NEXT WORK

This is the decision step. Work through these sources in priority order:

**Priority A — PENDING Work Orders:**
1. Read the Blueprint to understand task ordering and wave structure
2. Identify the next PENDING task in the current wave (lowest BP-N.M.T number that doesn't have a DONE or IN-PROGRESS WO)
3. Check dependencies: does this task depend on any WO that is IN-PROGRESS or FAILED?
   - If dependencies clear: This is your WO. Create it with `/init-doc wo WO-{id}` if it doesn't exist, set status to IN-PROGRESS, assign your instance ID. Proceed to Step 7.
   - If dependencies blocked: Skip this task, try the next PENDING task in the wave.
4. If all remaining tasks in the current wave have unmet dependencies: log "wave blocked" in progress.log, send a beacon via `/mail Epoch-PM`, skip to Step 8.

**Priority B — Gap Tracker Items (no WOs available):**
1. Read `Specs/gap_tracker.md`
2. Tier 0 items first (critical), then Tier 1 (functional)
3. Pick the first unchecked item you can act on
4. Create a WO for it if the work is code-level, or execute directly if it's a spec/doc task
5. Proceed to Step 7.

**Priority C — No Work Available:**
If there are no PENDING WOs and no actionable Gap Tracker items:
- Log "No actionable work found" in progress.log
- Send a status beacon via `/mail Epoch-PM` reporting idle state
- End the skill. Do not invent work.

---

### Step 7: EXECUTE

You now have a WO to work on. Execute the full lifecycle without pausing for approval.

**This is not a planning step. This is where you do the actual work.**

1. **Prep:** Run `/spec-lookup <module>` to load spec context for the module this WO covers.
2. **Checkpoint:** Write `.claude/checkpoint.md` — WO ID, planned approach, files you expect to modify, Phase: IMPLEMENTING.
3. **Implement:** Write the code. Follow the execution protocol (no stubs, no TODOs, real logic). Follow the problem-solving protocol if you hit issues.
4. **Test:** Run tests. Fix failures. Update checkpoint to Phase: TESTING/FIXING as appropriate.
5. **Review:** Run `/code-review <module>` on your work.
6. **Complete:** Run `/module-complete <module>` to verify all 7 quality gates.
7. **If integration task:** Run `/integration-logic <mod-a> <mod-b>` and record the verdict.
8. **Close out:**
   - Set WO status to DONE
   - Clear checkpoint: `<!-- No active work. Last WO: {WO-ID}, completed {date} -->`
   - Log completion to progress.log: `WO-{id} DONE | {brief summary} | -> {next WO or "checking for more work"}`
   - Commit with message: `WO-{id}: {description}`
   - Run `/pre-commit` before the commit

9. **Loop:** After completing a WO, return to Step 4 to check for more work. Continue until no actionable work remains or you hit a blocker.

---

### Step 8: ESCALATE

You're here because something prevents progress. Categorize and act:

**Non-critical (blocked dependencies, no work available, stale WOs):**
- Log the situation in progress.log
- Send a status beacon to PM via `/mail Epoch-PM` describing the state
- End the skill gracefully

**Critical (broken specs, failing builds that shouldn't fail, schema conflicts, security issues):**
- Create `.claude/stop-work.md` with full details
- Notify PM via `/mail Epoch-PM` with priority: urgent
- Log to progress.log
- End the skill immediately

---

## Autonomy Principles

These principles govern how this skill operates. They exist because unattended agents cannot ask questions — they must act or explicitly halt.

1. **Proceed by default.** If the project state is clear and work is available, do it. Don't ask "should I start?" — start.
2. **Read, don't ask.** Every piece of context you need is in the project files: specs, Work Ledger, checkpoint, progress log, gap tracker. Read them. The answer is there.
3. **Own the full lifecycle.** The agent that picks up a WO runs it end-to-end: prep, code, test, review, complete, commit. No handoffs mid-WO.
4. **Respect boundaries.** Never touch another instance's WO. Never resume another instance's checkpoint. Never delete stop-work.md.
5. **Escalate, don't guess.** If you genuinely cannot determine what to do (not "I'm unsure" — "the information doesn't exist"), escalate. But exhaust the project's documentation first.
6. **Log everything meaningful.** Progress log entries are how other instances (and Nathan) understand what you did. Write clear, specific entries at WO boundaries.
7. **Stop when there's nothing to do.** Don't invent work. Don't refactor code that isn't in a WO. Don't "improve" things. If the queue is empty, report idle and stop.
