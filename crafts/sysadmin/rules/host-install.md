# Host install (sysadmin craft, Tended Rule)

Read by no core kernel. A craft-owned rule, adjacent to Rule-11 property 2
(`dyad/rules/RULE-11-distribution-structure.md`: what an install *writes*, and that this craft is
bundled with the core release) and to Rule-8 (`dyad/rules/RULE-8-host-mutation.md`: the class,
authorization and record of every host action, an install included). Neither cites this rule back;
the citation is one-way until the core-side row d-work #81 opened for it lands. A Tended Rule — any
form, no Rule-4 block, no sweep, no Agent-vocabulary row (Rule-4 Boundaries). Terms (`host install`,
`prerequisite`): `crafts/sysadmin/vocabulary/CRAFT.md`.

**The case this rule holds, exactly as #81 scored it.** Not an unowned failure: what an install
writes is Rule-11's, the pin is Rule-14's, the act's class and row are Rule-8's, and when the
documented entrypoint failed on a host whose `python3` sat below the kernel pin, the symptom was
repaired in the core (`dyad/bin/dyad-python`, d-work #82) with no sysadmin rule in existence. What
had no owner was the *judgment* behind that repair: plan #82 decided three prerequisite questions —
that pydantic's absence is the manifest's own declared state and no host fault (its F2), that no
host package is touched (F3), that every `#!/usr/bin/env python3` shebang stays as it is (its
backlog item 2) — and wrote none of them anywhere a second host could read. A prerequisite judgment
made in a plan and discarded is a recurring task of the kind Rule-13 property 1 proposes code or a
rule for; this rule is the rule (#81, attacks A2 and A8). It states what a host must provide before
the act, how that is verified, how the act is authorized and recorded, and what holds afterwards.

## Prerequisites
A **prerequisite** is what a host must provide before a host install is attempted: declared by the
manifest (Rule-14; `dyad/infrastructure/INFRASTRUCTURE.md`), satisfied on the host by this craft.
The set, read from the manifest's kernel rows and the files that run first:
1. **An interpreter at the kernel pin** — Python 3.12 or newer (Rule-14 property 2;
   `dyad/scripts/package.py` refuses anything below it with one named line). It need not be the
   host's `python3`: `dyad/bin/dyad-python` probes `python3.13`, `python3.12`, `python3` in that order
   by running each, and execs the first that satisfies the pin (#82). A host with a conforming
   interpreter under any of those names meets this prerequisite, whatever its default `python3` is.
2. **Git**, as a local repository (Rule-14 property 2), honouring `core.hooksPath` and recording the
   executable bit (`100755`) the hooks and ops scripts are tracked at (ops-scripts rule, property 5).
3. **A shell**: `/bin/sh` for the two entrypoints (`dyad/bin/dyad`, `dyad/bin/dyad-python`) and
   `bash` for the two hooks (`dyad/hooks/pre-commit`, `dyad/hooks/pre-push`) and every ops script
   (`#!/usr/bin/env bash`; the manifest's library row). Which platforms provide these is the
   host-platform rule's table.
4. **pydantic at the manifest's pin** — declared kernel, and today imported by no module of the core
   or of any craft (the manifest row: "adopted when a plan first imports it"). Its absence is the
   manifest's declared state, not a host fault (#82, F2); it becomes a verified prerequisite the day
   a plan imports it, and that plan says so.

## Verification before the act
A prerequisite is verified by running the thing that needs it, never by reading a version string:
`dyad/bin/dyad check --list` on the source tree exits non-zero with a named line when no interpreter
meets the pin, and prints the guard registry when one does; `git --version` and `command -v bash`
cover the rest. The verdict is written in the plan of the d-work that performs the install, one line
per prerequisite — name, pin, what was observed, met or unmet, and what follows — before the act and
never gathered afterwards. An unmet prerequisite is a finding; satisfying it is a host action with
a class of its own (below), and working around it inside the repository instead (as #82 did) is a
plan decision stated in those words. The same prerequisite found unmet a second time, on any host,
proposes a fix in code or a line in this rule, never a third unrecorded workaround.

## Authorization and record
A **host install** is the act that writes the core craft, a Tended craft or both into a repository
on a live host — `dyad install`, `dyad craft install`, an upgrade of either — together with what the
host must be given for it to succeed. Every step is a host action; its class is the host-mutation
rule's and the authorization each class needs is Rule-8's:
- Writing the tree and its craft registry row is **reversible**: the undo is a checkout of the
  previous tree (the registry's `sha256` names what was there). Setting `core.hooksPath dyad/hooks`
  is reversible, undo `git config --unset core.hooksPath`. Both are authorized by the plan that
  names them, with the undo.
- Installing an interpreter or a package on the host through its package manager is reversible when
  the manager can remove exactly what it added, and **destructive** when it would upgrade, remove or
  replace anything else (host-mutation rule: `apt upgrade` is destructive; when in doubt,
  destructive). A destructive step needs its own authorizing disposition naming it, even inside a
  planned d-work.
- A step the session cannot run itself (privilege, a system package) is delivered for the operator
  to run as an ops script (ops-scripts rule; Rule-18), never as an inline block; its pasted output
  is the outcome.
Every reversible or destructive step gets a row in the host's change log (host-mutation rule), with
the seven columns `date`, `d-work`, `class`, `action`, `undo`, `outcome`, `actor`: `action` names the
craft and version installed and the target path (or the ops script and its commit), `outcome` the
install's own printed line (`installed into <target>: <n> changes`) and the registry row written,
`actor` the hands that drove it (`operator` for an ops script, `agent` otherwise).

## Postcondition
A host install is complete when all of the following hold, and the change-log row's `outcome`
reports them as observed: the craft registry row's `sha256` equals the installed tree's; a second
run of the same install reports `0 changes` (`crafts/syseng/rules/idempotence.md`, property 1);
`core.hooksPath` is `dyad/hooks`; and `dyad/bin/dyad check --guards` runs on the kernel alone and
exits 0, every absent store printing its skip line. Hooks are the core's only host-side writes
(Rule-11 property 2); a Tended craft install writes its root and its registry row and nothing else.

## Bundled with the core
This craft is a bundled craft (Rule-11 property 2, d-work #114): `dyad build` carries its tree in the
core's archive and `dyad install` writes it, so a system that installs the core alone has this rule.
Stated as a fact of where the rule is found, not as a dependency: the craft's `MANIFEST.md` floor is
unchanged by it (#81, re-plan finding).

## Boundaries (what this rule does not own)
- What is distributed and what an install writes — Rule-11; the design behind it (archive shape,
  version seed, entrypoint, the receiving-instance upgrade order) —
  `crafts/sysarch/rules/distribution.md`.
- That the install is scripted, idempotent and tested — `crafts/syseng/rules/idempotence.md`.
- The dependency itself and its pin — Rule-14; the manifest's form — `crafts/sysarch/rules/manifest.md`.
- The host-action classes, the read-before-act procedure and the change log's columns and guard —
  the host-mutation rule (read here, not restated).
- Which platforms exist and what each one demands — the host-platform rule.

## Provenance
Written by d-work #81 (plan `agent-corpus/d-work/plans/81.md`, revision 3, 2026-10-15): the
original plan's rule, the 2026-09-23 re-plan's corrections (the narrowed A2 case, the seven-column
record, the one-way citation of A7) and revision 3's numbers. Record:
`../falsification/rules/host-install.md`.
