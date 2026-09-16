# Rule-15: d-work phases

**Intent:** Split every d-work into a planning phase that is stored and an execution phase
that can start in any later session.
**Target:** a d-work phase

## Boundaries (out of scope)
- The d-work lifecycle, counter-prompt forms and the ledger itself — Rule-3; Rule-15 adds a
  stored plan and one state, nothing else.
- Who ratifies — Rule-2. Where files live for concurrent sessions — Rule-16.
- What a plan proposes — Rules 9, 10, 12, 13 as today.

## Conditions (triggers)
- The Agent is about to ask a plan counter-prompt: the plan file exists first.
- The Operator answers `Y` to a plan: state becomes `planned`.
- A session, any session, begins executing a `planned` d-work.
- `main` has moved past a file the plan touches before execution starts.

## Phases
1. **Planning.** The plan is written to `agent-corpus/d-work/plans/<id>.md` before the
   counter-prompt: intent as read, mutation, files touched, base commit of `main`,
   falsification pointer. The reply reproduces it. The plan-`Y` binds to the file.
2. **Execution.** Begins by reading the plan file, in the same or any later session. If
   `main` has moved past a touched file, the Agent re-plans (new plan-`Y`); otherwise it
   executes as written. Done-`Y` as Rule-3.
- A d-work interrupted mid-execution resumes from the plan file and the branch; the
  incident is recorded (Rule-3).

## Enforcement
The PR guard (`dyad/guards/agent/prs.py`, Rule-3) accepts state `planned` at the plan gate. Inference otherwise; Rule-16 makes
the plan file the collision-free unit for a second session.

## Provenance
Operator rule, 2026-09-13. Falsified; see `../falsification/rules/rule-15-d-work-phases.md`.

Set: System Requirements.
