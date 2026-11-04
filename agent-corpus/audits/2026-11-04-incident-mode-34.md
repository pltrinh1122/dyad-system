# Incident mode 34 — hosting outage refuses writes

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
hosting outage refuses writes.

**What would have to change** (the derivation's one-sentence test): queue and retry with the local-merge path, at push.

**Predecessor:** mode U of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-u.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 97 | 2026-10-07 | #232 | V1-41 |
| 112 | 2026-10-07 | #234 | V1-41 |

Secondary mechanism on rows: 112 (V2-04). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| local merge path while the hosting is unreachable | Rule-14 p3 (#138); Rule-2 Binding | conduct, merge | 97 | 112 (a ledger push, not a merge) | shipped (rule text) | — |
| land rebuilds and re-allocates the id on a moved main | `land.py:343-374` | call | 112 (the id collision part) | 112 (an unmoved-main 500 refuses, no retry) | shipped (#447, 2026-10-25) | none after |
| ids contiguous from base max+1 | `rows.py:568` | push | 112 (collision) | — | shipped (#467) | — |

Closure: (3) impossible on this kernel — the outage is The World (Rule-14 p4); the fences that bound its damage are the
local merge path and `land`'s rebuild. No queue-and-retry for a 500 on an unmoved `main` exists (`land.py`
`Refused("the push failed with main unmoved")`); that is a deliberate refusal, not a gap to fence.

## Status
Exit 3 — impossible on this kernel.
