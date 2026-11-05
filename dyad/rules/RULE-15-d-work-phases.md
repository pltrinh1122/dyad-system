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
- The agent is about to ask a plan counter-prompt: the plan file exists first.
- The operator answers `Y` to a plan: state becomes `planned`.
- A session, any session, begins executing a `planned` d-work.
- `main` has moved past a file the plan touches before execution starts.

## Phases
1. **Planning.** The plan is written to `agent-corpus/d-work/plans/<id>.md` before the
   counter-prompt: its definition of done (the operator's words, quoted from the provenance record,
   or one marked proposed that the plan-`Y` accepts; the d-work play-book), intent as read, mutation,
   files touched, base commit of `main`, falsification pointer. The reply reproduces it. The plan-`Y` binds to the file. A plan that
   needs an order of its steps or a split of its PRs says so as a requirement (`order: required`);
   otherwise order and split are execution detail (Rule-3 Plan, #555).
2. **Execution.** Begins by reading the plan file, in the same or any later session. If
   `main` has moved past a touched file, the agent re-plans (new plan-`Y`); otherwise it
   executes as written; the done-`Y` as Rule-3.
- A d-work interrupted mid-execution resumes from the plan file and the branch; the
  incident is recorded (Rule-3).
- An **accreted row** (Rule-3, Scope; what carries it: Rule-3, What a `Y` binds) has no planning phase of its own: its plan *is* the
  mandate's plan file, which the mandate's plan-`Y` already bound, so it carries no base commit
  of its own and no drift check — the base commit that was read is the mandate's, and re-planning
  fires on that one, for the parent and every row accreted under it together. Nothing fails today
  when such a row has no plan file of its own: `plans.py` and Rule-20's `plan.base->commit` judge
  only the plan files that exist, so the absence is silent by construction and not by exemption.
  It is stated here so a reader does not look for a check that is not there, and because the cost
  falls elsewhere — Rule-16's presence `files` union is built from stored plan files, so a
  plan-less row contributes none (#290).

## Enforcement
The PR guard (`dyad/guards/agent/prs.py`, Rule-3) accepts state `planned` at the plan gate. Inference otherwise; Rule-16 makes
the plan file the collision-free record for a second session.

## Provenance
Operator rule, 2026-09-13. Falsified; see `../falsification/rules/rule-15-d-work-phases.md`.
Phases gains the accreted-row bullet 2026-10-14 (d-work #290): a row accreted under another row's
mandate has no plan file, so phase 1 has nothing to write and phase 2's drift check nothing to
read, and that gap had been silent rather than stated; see the same record, amendment #290. Phase 1 gains the
stated requirement of order or split 2026-11-02 (d-work #555): without it an order the plan only narrated could not be
told from one it needed; see the same record, amendment #555. Operator and agent are lowercase in prose and done-`Y` replaces Done-`Y`, 2026-11-02
(d-work #553): the dyad-native terms; see `../falsification/rules/rule-6-vocabulary.md`, amendment #553 (part D). Phase 1 gains the definition
of done 2026-11-04 (d-work #574): a row's scope follows what the operator can evaluate, and the plan is where that is
stated and accepted; see the same record, amendment #574. The accreted-row bullet points to Rule-3's What a `Y` binds 2026-11-04 (d-work #585, the
Rule-3 refactor); see `../falsification/rules/rule-3-d-work.md`, amendment #585.

Set: System Requirements.
