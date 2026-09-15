# Rule-18: ops scripts

**Intent:** Deliver every command the Operator runs on the Agent's behalf as a committed,
executable, syntax-checked shell file whose text and outcome are provenance.
**Target:** an Operator-executed command

## Boundaries (out of scope)
- The class of the action, its authorization and its change-log row — Rule-8. Rule-18 owns
  only the form of delivery; it cites Rule-8 and Rule-8 cites it back only in Conduct (one-way
  ownership).
- The file's form — name, header, body, provenance, check, idempotence, run-time confirmation —
  is the active craft's ops-script rule (`crafts/sysadmin/rules/ops-scripts.md`, a Tended Rule;
  #155); Rule-18 keeps *that* it is one checked file and what its outcome proves.
- When the action is planned and when its d-work closes — Rule-3; the plan names the script as
  the H-row and the completion reply cites its path and outcome.
- Which zone the file lands in — Rule-1 (`workstation-corpus/` is workstation zone); package
  layout and the `generated` pattern — Rule-11; the guard's mechanical check — Rule-12.
- The interpreter: bash is a library row (Rule-14); nothing in the package runs an ops script.
- Commands the Agent runs itself, and commands already run before this Rule: the change log is
  their record; capture is for commands still to run.
- Recurring operations of a server instance are run-book commands, run by either party through
  Rule-19's runner, which records an event; an ops script is a one-off d-work action delivered for
  the Operator to run. Both share the craft's header vocabulary (class, undo, postcondition,
  destructive confirmation); Rule-19 adds role, scope and the event and owns the run-book's use of it.

## Conditions (triggers)
- A plan names a host action the Agent may not run (privilege, credentials, physical presence):
  the plan names the ops script that delivers it.
- An ops script is added or edited: the PR carries it in the workstation zone, one file per
  change-log row.
- The Operator has run an ops script: the pasted output is compared to the script's commit and
  hash before the change-log row is written.
- Every push and PR: the active craft's guard (`crafts/sysadmin/guards/ops_scripts.py`, registry
  label `sysadmin/ops_scripts`) runs through `package.py check` (the craft rule owns the check; the
  runner owns none of its semantics).

## Properties
1. **Form.** An Operator-executed command is one file `<ops>/<d-work>-<hN>-<slug>.sh` (instance,
   workstation zone; `DYAD_OPS`, default `workstation-corpus/ops`, in the manner of Rule-11
   property 3) in the active craft's ops-script form (`crafts/sysadmin/rules/ops-scripts.md`),
   checked by that craft's guard; the pasted output is compared to the script's commit and hash
   before the change-log row is written; the exit code is completion evidence.

## Conduct
- Never an inline block: a command the Operator is asked to run is a file in the PR, or it is
  not asked.
- Reading before running is the Operator's; `set -x` and the header make the script legible.
  Rule-8's plan-`Y` and destructive counter-prompt remain per action.
- A mismatch between the pasted output's commit or hash and the committed script is reported as
  an incident (Rule-3) before any row is written.
- The run-time `Y` of the craft's confirmation form executes an action the chat counter-prompt
  already ratified (Rule-8; Rule-2 by reference) and is no ratification event; a declined step
  (exit 2) is withdrawn execution, reported as an incident (Rule-3) and recorded as the row's outcome.
- Exit codes are completion evidence: the completion reply cites the script's exit code with its
  outcome (0, 1 or 2 per the craft rule's property 7f).

## Enforcement
The active craft's guard `crafts/sysadmin/guards/ops_scripts.py` (`check_package`; placed per
`crafts/sysarch/rules/guards.md` under the craft's root), tests in `crafts/sysadmin/tests/guards/test_ops_scripts.py`,
invoked by `package.py check` as `sysadmin/ops_scripts`. shellcheck is deferred (a new World row,
Rules 13/14); named in the record.

## Provenance
Operator rule, 2026-09-14. Falsified; see `../falsification/rules/rule-18-ops-scripts.md`. Kernel
since #155: properties 1–7 moved to the sysadmin craft.

Set: System Requirements.
