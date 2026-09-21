# Host mutation (sysadmin craft, Tended Rule)

Read by Rule-8's kernel (`dyad/rules/RULE-8-host-mutation.md`): the core Rule binds *that* every host
action is classed, authorized at the level its class demands and recorded; this rule says *which*
actions fall in which class and what the record looks like. Text moved verbatim from Rule-8 by
d-work #155; a Tended Rule — any form, no Rule-4 block, no sweep, no Agent-vocabulary row (Rule-4
Boundaries). Terms: `crafts/sysadmin/vocabulary/CRAFT.md`.

## Reading before acting (the procedure Rule-8 Conditions bullet 4 names)
Before any reversible or destructive host action: the Agent reads every file in
`workstation-corpus/rules/` and in `crafts/sysadmin/rules/` (once per d-work, again if it changed).

## Classes
- **read-only** — observes and changes nothing (`ls`, `systemctl status`, `cat`). Free.
- **reversible** — changes state and has a stated undo (`git config`, editing a config file
  with a kept copy, starting a service). Authorized by the plan-`Y` of the plan that names it,
  with its undo.
- **destructive** — no undo, or loses data, or the undo is untested (`rm` of user data,
  package removal, partition or filesystem changes, `apt upgrade`). Needs its own
  counter-prompt naming the action, even inside a planned d-work. When in doubt, destructive.

## The change log (the record Rule-8 Conduct requires)
Every reversible or destructive action gets a row in the host's change log
(`workstation-corpus/CHANGELOG.md`, instance; seeded from `crafts/sysadmin/templates/CHANGELOG.md`)
with the columns (date, d-work, class, action, undo, outcome, actor), in a workstation-zone PR of
the same d-work. `actor` is `operator` or `agent` — the party whose hands executed the action (who
drove it: typed the command or ran the ops script, versus the Agent's own process), matching what
a server's own audit log and a run-book event's `role` (server-instances rule) already mean; an
Operator-run ops script (Rule-18) is `operator`, an Agent-run command `agent`. The credential it
ran under can diverge from the hands that drove it (an Agent-run git commit still carries the
Operator's own git identity, Rule-2 Enforcement) — `actor` names hands only; a divergent credential
is named in the row's `outcome`. Only an action the Agent takes is *required* by Rule-8's kernel
(Target: "a host action");
an Operator action performed independently — outside an ops script, for the Operator's own reasons
— has no row the kernel requires, but this craft records one it learns of, at the Operator's
instruction (d-work #216). A run-book command's event (server-instances rule, telemetry) is its
change-log evidence: the row's outcome cites `event: <id>` instead of a pasted transcript, and
Rule-20 resolves the id. The guard `crafts/sysadmin/guards/changelog.py` (registry label
`sysadmin/changelog`) checks the header equals the columns (or the columns without `actor`, for an
instance mid-migration — `OPTIONAL`, #216), each row's date form, `#<id>` d-work, class, non-empty
action, an actor in `operator`/`agent` where the column is present, and — for a reversible or
destructive row — a non-empty undo; a missing change log passes (fresh install).

## Provenance
Rule-8 Classes, Conduct bullet 2's column list and Conditions bullet 4's procedure, moved by #155
(plan `agent-corpus/d-work/plans/155.md`, attack 3). `actor` column added 2026-09-16 (#216, plan
`agent-corpus/d-work/plans/216.md`): Operator prompt, "i agree with keeping provenance for operator
performed mutation, e.g. Gitea UI, and agent performed mutation, e.g. CLI." Record:
`../falsification/rules/host-mutation.md`.
