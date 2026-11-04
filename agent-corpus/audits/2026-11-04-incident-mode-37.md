# Incident mode 37 — a new call site or writer added without enumerating other paths to the same code or state

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 3 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a new call site or writer added without enumerating other paths to the same code or state.

**What would have to change** (the derivation's one-sentence test): the change enumerates callers and writers of the target, at code write.

**Predecessor:** mode J of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-j.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 52 | 2026-09-24 | #155 | V1-31 |
| 53 | 2026-09-24 | #155 | V1-31 |
| 106 | 2026-10-07 | #228 | V1-31 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| nested-suite guard | `package.py:426`, `:668` `DYAD_NO_NESTED_TESTS` early return; set in `suite_env` `:739` | suite run | 52 | 53, 106 | shipped (2026-09-14; the new call site of #155 lacked it, fixed 09-24) | no |
| suite once per process | `package.py:379` `_SUITE_RAN` (2026-09-24) | evidence run | 53 | 52, 106 | shipped | no |
| install idempotence over both writers | `package.py:1730-1731` `check --corroborate` steps `expect=" 0 changes"`; `:1777` comment on the two-writer ping-pong | CI after merge (`dyad-package.yml:28`) and automaton corroboration | 106 | 52, 53 | shipped | no |
| general: enumerate callers/writers of a target | none in code; mode J backlog row `agent-corpus/d-work/rows/271.md` | plan time (conduct) | — | all three as a class | candidate (backlog) | — (also the primary mode of V2-42's rows 218-221, after #155's fixes) |

Closure: (2) backlog #271 (mode J, a call site added without its call graph). The three instances are each fenced by a
point test; the class has no fence.

## Status
Exit 2 — backlog row; fence row proposed: **R-c** (index, Proposals).

**Reconciliation (index, decision 5):** the general mode of a change made without its call graph is read by no mechanism at plan time today. Its fence is folded into R-c (`dyad plan check` lists every caller of each function the plan's files change), and row #271 is proposed for retirement as superseded by R-c.
