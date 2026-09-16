# Rule-19: server instances

**Intent:** Leave every server instance the Agent deploys or operates with a run-book and a
health command whose observed pass is the deploying d-work's completion evidence.
**Target:** a server instance

## Boundaries (out of scope)
- The class, authorization and change-log row of every action that starts, stops or alters a
  server — Rule-8. Rule-19 names what a deployment must leave behind; Rule-8 classes each step.
- The run-book's form — supervisor, sections, commands, health criterion form, telemetry, one
  execution path, contained mutation — is the active craft's server-instances rule
  (`crafts/sysadmin/rules/server-instances.md`, a Tended Rule; #155), checked by that craft's
  guards; Rule-19 keeps existence at the instance path and the observed health pass. A run-book's
  section set is declared in its header (`# sections:`), default the craft rule's ten; a core
  run-book (`dyad/runbooks/`, the play-books' steps, #165) is checked with its own set — the
  craft rule states it.
- The form of a command the Operator runs for the Agent — Rule-18 (ops script). A run-book
  command is a reference the reader runs by choice; an ops script is a delivered action. A
  run-book may cite an ops script; it never replaces one.
- Package versus instance and what `package.py check` refuses — Rule-11; a run-book is
  instance. The manifest row of the server software and its supervisor — Rule-14.
- What the host *should* look like beyond persistence — Tended Rules (`workstation-corpus/rules/`,
  Rule-4 classifies); a Tended Rule may add host-specific constraints on a server, never remove
  the properties below.
- When the deploying d-work opens and closes — Rule-3; Rule-19 states one condition of Done.

## Conditions (triggers)
- A plan deploys, replaces or removes a server instance: the plan names the supervisor and
  the run-book path.
- A server instance's compose file, unit or image changes: the run-book is revised in the same
  workstation-zone PR.
- The Agent or the Operator operates a server instance: the run-book's command is used and,
  if it does not work, corrected in a PR.
- The completion counter-prompt of a deploying d-work: the run-book exists and its health
  command passes as observed.
- Either party runs a run-book command: it runs through the runner (`dyad runbook run`,
  `dyad/scripts/runbook.py`, core), which records its event; a run-book is added or edited: the
  active craft's guards `sysadmin/runbooks` and `sysadmin/events` (`crafts/sysadmin/guards/`)
  check it on every push and PR, in Rule-11's runner and on the kernel-only path.

## Properties
1. **Run-book and health.** Every server instance has a run-book at `<runbooks>/<instance>.md`
   (instance, workstation zone; `DYAD_RUNBOOKS`, default `workstation-corpus/runbooks`, in the
   manner of Rule-11 property 3) in the active craft's run-book form
   (`crafts/sysadmin/rules/server-instances.md`), with a health command whose pass criterion is
   stated. `dyad runbook new <instance>` seeds it from the craft's template.
2. **Deployed means run-book and health.** A server's deploying d-work is not Done until the
   run-book exists and the health command passes; the completion reply cites the run-book path
   and the health command's observed output (Rule-3 completion evidence). The run-book and its
   events (`<runbooks>/events/<instance>.jsonl`, append-only on `main`) are the evidence.

## Enforcement
The active craft's guards `sysadmin/runbooks` (`crafts/sysadmin/guards/runbooks.py`) and
`sysadmin/events` (`crafts/sysadmin/guards/events.py`) through Rule-11's runner; what they check
is the craft rule's. The runner `dyad runbook` (`dyad/scripts/runbook.py`) is core: it holds the
run-book parser and the event store's primitives, which the craft's guards import, so
`list | run | new` work with no craft installed and `check` exits 2 when no craft provides the
check (#155 amendment). Rule-20 resolves event references. Not checked, stated: whether the health
criterion is right and whether a command works — inference, tested by running them and read from
the events.

## Provenance
Operator rule, 2026-09-14 (ledger #134). Falsified; see
`../falsification/rules/rule-19-server-instances.md`. Kernel since #155: properties 1–4 and 6–9
moved to the sysadmin craft; its `Set:` line names that (#160 finding, fixed by #162).

Set: System Requirements (kernel; content: crafts/sysadmin/rules/server-instances.md).
