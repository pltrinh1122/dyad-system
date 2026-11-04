# Incident mode 35 — concurrent processes on one host contend for memory/CPU and corrupt runs

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 3 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
concurrent processes on one host contend for memory/CPU and corrupt runs.

**What would have to change** (the derivation's one-sentence test): runs serialize or record host load, at run start.

**Predecessor:** mode Y of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-y.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 35 | 2026-09-16 | #48 | V1-39 |
| 74 | 2026-09-29 | #190 | V1-39 |
| 177 | 2026-10-15 | #297 | V1-39 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| per-process bound on suite children | `dyad/scripts/package.py:754-755` `SUITE_JOBS`, `_SUITE_SLOTS` (#475, 2026-10-26) | suite run (push gate, evidence) | none (bounds one runner's own children only) | 35, 74, 177 (peer sessions, host-wide load, a spin-wait) | shipped | none of the rows is after 10-26 |
| suite-once per process | `package.py:379` `_SUITE_RAN` (#155, 2026-09-24) | evidence run | none (self-contention, not peer) | 35, 74, 177 | shipped | — |
| nothing records host load or serializes across sessions | grep for `getloadavg`/`loadavg`/lock in `dyad/scripts/*.py`: no hit | — | — | 35, 74, 177 | — | — |

Closure: (2) backlog, NEW fence — the runner (`run_suite`, `package.py`) takes a host-wide `flock` under the git common
dir and prints `os.getloadavg()` into the evidence block and the suite memo key, at run start; owner engineer. Row 177's
spin-wait is conduct (no mechanism reads the Agent's shell loop) and stays inference.

## Status
Exit 2 — backlog row; fence row proposed: **R-f** (index, Proposals).
