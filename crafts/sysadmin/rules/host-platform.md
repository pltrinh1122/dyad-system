# Host platform (sysadmin craft, Tended Rule)

Read by no core kernel. A craft-owned rule, adjacent to Rule-11 property 2
(`dyad/rules/RULE-11-distribution-structure.md`: a bundled craft is written by the core's own install,
so the platform set below is also where `dyad install` may be run at all) and to Rule-8
(`dyad/rules/RULE-8-host-mutation.md`: every act that makes a host meet a platform's contract is a
host action it classes). Neither cites this rule back; the citation is one-way until the core-side
row d-work #81 opened for it lands. A Tended Rule — any form, no Rule-4 block, no sweep, no
Agent-vocabulary row (Rule-4 Boundaries). Terms (`host platform`, `platform contract`):
`crafts/sysadmin/vocabulary/CRAFT.md`.

**The seam with `crafts/syseng/rules/host-facts.md`, stated from this side.** That rule says *how a
host fact is read in code*: one place per fact (`dyad/scripts/hostadapter.py`), never an inline
call site, two functions and not a framework. This rule says *which host platforms this system
supports and what each one demands*. The first is a property of the code; the second is a property
of the practice. This rule does not reverse host-facts property 2 and relies on it: a supported
platform earns a named function per fact it diverges on, justified in the plan that adds it — never
a registration hook, never a generic per-OS branch (#81, attacks B1–B3). The reciprocal sentence in
`host-facts.md` is a row of its own, not an edit made here.

## The platform set — a stated fact, read as obligation
A **host platform** is an operating system the operator has named as one this system is to run on.
Naming it puts the platform in the set; it says nothing about whether the dyad runs there today.
Each row below records a status, so the rule reads as an obligation this craft owes and never as a
capability the system has (#81, attacks B5 and B6).

| platform | status | what is known |
|----------|--------|---------------|
| Linux | **verified** | every host this system has run on: the authoring workstation (`workstation-corpus/`) and the cloud sessions (#82's host). The contract below is met in full; `dyad check --guards` exits 0 on the kernel alone. |
| macOS | **in scope, unmet** | named by the operator (#81). One fact is read in code already — `/var` → `/private/var`, the symlink `hostadapter.resolve` collapses (host-facts rule, #179) — and its test runs on Linux because the divergence cannot be reproduced here. No host install has been performed on macOS; no item of the contract is verified. |
| Windows | **in scope, unmet** | named by the operator (#81). A POSIX shell is not part of the platform, so the four core shell files and the ops-script skeleton below cannot run as they are; no item of the contract is verified and no host fact for it is read in code. |

## What a platform contract states
A **platform contract** is the list of what a platform must provide for a host install to succeed
and the installed system to run its gates, one item per obligation, each marked met or unmet for
that platform. Every contract states at least:
1. **The interpreter names.** Under which names a Python at the kernel pin (Rule-14 property 2) is
   found. The Linux answer is `dyad/bin/dyad-python`'s candidate list — `python3.13`, `python3.12`,
   `python3` — probed by running each (#82). Another platform that finds its interpreter under another
   name earns a change to that list, in a plan that says why.
2. **The shell.** Four core files and this craft's skeleton assume one, verified by reading each
   shebang (2026-10-15): the two entrypoints `dyad/bin/dyad` and `dyad/bin/dyad-python` need a
   POSIX `/bin/sh`; the two hooks `dyad/hooks/pre-commit` and `dyad/hooks/pre-push` and the
   ops-script skeleton `crafts/sysadmin/templates/ops-script.sh` need `bash` (`#!/usr/bin/env
   bash`; the skeleton also reads its confirmation from `/dev/tty`). Nothing in the package runs on a platform that lacks the
   shell its first file names; the manifest's library row for bash is the dependency this item
   satisfies on the host.
3. **Git.** A local repository that honours `core.hooksPath` and records the executable bit the
   hooks and ops scripts are tracked at (`100755`; the ops-scripts rule, property 5, and the
   `core.fileMode=false` case it names).
4. **The host facts the code reads**, with the platform's answer to each: path resolution
   (symlinks), filesystem case-sensitivity, line endings — the host-facts rule's list, read through
   `hostadapter.py`. A platform whose answer differs from Linux's earns a named function there, not
   a line here.
5. **The package manager** through which a prerequisite is satisfied on that platform, and the
   host-action class of that act (the host-install rule, Authorization): what the undo is, and
   where the manager would touch more than it was asked to and the act is destructive.

A contract item is met when it has been observed on a host of that platform and the observation is
recorded (below); until then it is unmet, whatever the code suggests.

## Where a divergence is recorded
A per-platform divergence is recorded in two places, by kind:
- **In code**: a host fact that differs is a named function in `dyad/scripts/hostadapter.py`, with
  its test (the host-facts rule, property 2). A shell obligation that differs is a change to the
  file that carries it, in the core craft (agent zone), planned as its own d-work.
- **In the practice**: the platform's row in the table above (status and what is known), and, for a
  host that actually runs the system, the host's own records under the host path (preference
  `host-path`, default `workstation-corpus`): its operating manifest rows
  (`<host-path>/INFRASTRUCTURE.md`, Rule-14 property 1) and its host-specific Tended rules
  (`<host-path>/rules/`).
The set changes only by the operator's decision — a prompt that names a platform, a d-work that
records it here — never by a code change that adds a branch. A platform's status moves from unmet
to verified only when a host install on that platform has been performed and recorded as the
host-install rule says.

## Boundaries (what this rule does not own)
- How a host fact is read in code — `crafts/syseng/rules/host-facts.md`.
- The dependency rows and the observation that The World is never pinned (the OS row of the
  manifest) — Rule-14; the manifest's form — `crafts/sysarch/rules/manifest.md`.
- What an install writes and where — Rule-11, `crafts/sysarch/rules/distribution.md`.
- The prerequisites, their verification and the act's record — the host-install rule.
- What one host *should* look like — that host's Tended rules under its host path.

## Provenance
Written by d-work #81 (plan `agent-corpus/d-work/plans/81.md`, revision 3, 2026-10-15): the
original plan's rule shaped by attacks B3 (does not reverse host-facts property 2), B5 (status per
platform, obligation not capability) and B6 (the shell inventory grew to five files when #82 added
`dyad/bin/dyad-python`). The macOS and Windows contracts are residuals #81's mandate opens as
`backlog` rows, one per platform when the work is prompted. Record:
`../falsification/rules/host-platform.md`.
