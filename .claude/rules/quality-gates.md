<!-- AGENT INSTRUCTION: These gates must ALL pass before any module can be marked complete.
     This is the "Definition of Done" for every module in the project.
     Do not skip gates. Do not mark a module complete with any gate failing.

     THIS FILE IS ALWAYS LOADED (no path scope). -->

# Quality Gates — Module Completion Criteria

*Intent: These gates prevent shipping incomplete work. Every gate addresses a specific failure mode observed in past projects.*

## Before Marking ANY Module Complete

1. **All interface contract methods are implemented with real logic (no stubs).**
   *Intent: Stubs create false confidence. Downstream modules call them expecting real behavior.*

2. **Unit tests cover all public methods.**
   *Intent: Untested code is unverified code. Tests are the proof that implementation matches spec.*

3. **No TODO/FIXME comments remain in the module.**
   *Intent: TODOs are deferred decisions. Resolve them now or explicitly defer to the gap tracker.*

4. **No GPL dependencies introduced.**
   *Intent: GPL viral licensing constrains Epoch Labs' commercial options. Apache 2.0, MIT, BSD only.*

5. **Compiles/builds without warnings.**
   *Intent: Warnings are future bugs. A clean build is the minimum quality bar.*

6. **Performance meets targets specified in the Engineering Spec.**
   *Intent: A feature that works but is too slow is a feature that doesn't work.*

## How to Invoke

Run `/module-complete <module>` to verify all gates against a specific module. The skill will check each gate and report pass/fail.
